import datetime
import logging
from typing import Any

from django.db import models, transaction

from system.models import CoreModel
from utils import generate_date_sequence_code

from .devices import Device
from .materials import Material
from .processes import Process

logger = logging.getLogger(__name__)


class ProductionOrder(CoreModel):
    """生产任务单模型"""

    class Status(models.TextChoices):
        PENDING = "pending", "已创建"  # 生产任务单（生产订单）由管理员手动生成
        PUBLISHED = "published", "已下发"  # 管理员手动下发任务单，任务单自动拆分为工序派工单
        CANCELLED = "cancelled", "已取消"  # 管理员手动取消任务单，同时，对应的所有工序派工单也会被取消
        COMPLETED = "completed", "已完成"  # 当所有工序派工单完成后，任务单状态变更为已完成
        OBSOLETE = "obsolete", "已废弃"  # 数据异常时（如产品被删除，或工艺路线被删除等），任务单将自动废弃，使用信号处理机制实现

    code = models.CharField(max_length=100, unique=True, verbose_name="生产任务单编码")
    product = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="production_orders", verbose_name="产品")
    quantity = models.PositiveIntegerField(verbose_name="生产数量")
    status = models.CharField(max_length=20, verbose_name="状态", choices=Status.choices, default=Status.PENDING)
    process_route = models.ForeignKey("ProcessRoute", on_delete=models.SET_NULL, null=True, related_name="production_orders", verbose_name="工艺路线")

    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存生产任务单，自动生成编号.

        编号格式：PO-8位日期-4位序列号
        示例：PO-20250313-0001

        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if not self.code:
            self.code = generate_date_sequence_code(
                model_class=ProductionOrder,
                prefix="PO",
            )
        super().save(*args, **kwargs)

    def calculate_material_requirements(self) -> dict:
        """计算所需原材料数量

        Returns:
            dict: {material_id: {material: Material, quantity: int}}
        """
        ordered_nodes = self.process_route.get_topological_nodes()
        first_node = ordered_nodes[0][0] if ordered_nodes else None
        if not first_node or not first_node.process_bom:
            return {}
        
        requirements = {}
        for detail in first_node.process_bom.bom_details.all():
            material = detail.material
            # quantity 表示生产1个产品需要多少个该原料
            required_qty = self.quantity * detail.quantity
            requirements[material.id] = {
                'material': material,
                'quantity': int(required_qty)
            }
        return requirements

    def publish(self) -> list:
        """下发生产任务单，自动拆分为工序派工单

        Returns:
            list: 创建的工序派工单列表
        """
        with transaction.atomic():
            # 更新状态为已下发
            self.status = self.Status.PUBLISHED
            self.save()
            
            # 获取工艺路线按拓扑排序后的所有工序节点
            route_nodes = self.process_route.get_topological_nodes()
            
            created_orders = []
            
            for i, (route_node, level) in enumerate(route_nodes):
                # 第一道工序派工单状态设为可派发，其他设为等待前置工序
                status = DispatchOrder.Status.PENDING if i == 0 else DispatchOrder.Status.WAITING_PREVIOUS
                
                order = DispatchOrder.objects.create(
                    production_order=self,
                    process=route_node.process,
                    sequence=level,
                    quantity=self.quantity,
                    status=status
                )
                created_orders.append(order)
            
            logger.info("生产任务单已下发: %s, 创建了 %d 个工序派工单", self.code, len(created_orders))
            return created_orders

    def cancel(self) -> None:
        """取消生产任务单及所有关联派工单"""
        with transaction.atomic():
            # 更新状态为已取消
            self.status = self.Status.CANCELLED
            self.save()
            
            # 取消所有未完成的派工单
            dispatch_orders = DispatchOrder.objects.filter(
                production_order=self,
                status__in=[
                    DispatchOrder.Status.PENDING,
                    DispatchOrder.Status.DISPATCHED,
                    DispatchOrder.Status.GRABBED,
                    DispatchOrder.Status.IN_PROGRESS,
                    DispatchOrder.Status.PAUSED,
                    DispatchOrder.Status.WAITING_PREVIOUS
                ]
            )
            
            for order in dispatch_orders:
                order.status = DispatchOrder.Status.CANCELLED
                order.save()
            
            logger.info("生产任务单已取消: %s, 取消了 %d 个工序派工单", self.code, dispatch_orders.count())


class DispatchOrder(CoreModel):
    """工序派工单模型

    当派工/抢单的生产数量小于派工单的生产数量时，自动触发拆分，将派工单拆分为2个子工单，当子工单全部完工时，父级派工单自动完成。
    父级派工单和子工单之间的已完成数量自动同步。
    派工单拆分后，父级派工单将不可接取，仅能接取子工单。
    """

    class Status(models.TextChoices):
        PENDING = "pending", "待抢单"  # 派工单创建后默认为待抢单状态
        DISPATCHED = "dispatched", "已派工"  # 管理员手动将派工单派工后，状态变更为已派工
        GRABBED = "grabbed", "已抢单"  # 员工手动抢单后，状态变更为已抢单
        IN_PROGRESS = "in_progress", "生产中"  # 员工手动开始生产后，状态变更为生产中
        PAUSED = "paused", "已暂停"  # 员工手动暂停生产后，状态变更为已暂停
        WAITING_PREVIOUS = "waiting_previous", "等待前置工序"  # 等待前一工序产出
        CANCELLED = "cancelled", "已取消"  # 员工不可取消派工单，由管理员手动取消
        COMPLETED = "completed", "已完成"  # 生产完成（报工数量等于生产数量）
        OBSOLETE = "obsolete", "已废弃"  # 数据异常时（如工序被删除，或父级任务单被删除等），派工单将自动废弃，使用信号处理机制实现

    code = models.CharField(max_length=100, unique=True, verbose_name="工序派工单编码")
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="生产任务单")
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="工序")
    sequence = models.PositiveIntegerField(verbose_name="工序顺序")
    operator = models.ForeignKey("system.User", on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="接单人")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="生产设备")
    quantity = models.PositiveIntegerField(verbose_name="生产数量")
    completed_quantity = models.PositiveIntegerField(verbose_name="已完成数量", default=0)
    status = models.CharField(max_length=20, verbose_name="状态", choices=Status.choices, default=Status.PENDING)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="children", verbose_name="父级工序派工单")
    is_parent = models.BooleanField(verbose_name="是否为父工单", default=False)
    is_child = models.BooleanField(verbose_name="是否为子工单", default=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存工序派工单，自动生成编号.

        编号格式：DO-8位日期-4位序列号
        示例：DO-20250313-0001

        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if not self.code:
            self.code = generate_date_sequence_code(
                model_class=DispatchOrder,
                prefix="DO",
            )
        super().save(*args, **kwargs)

    @property
    def is_reachable(self) -> bool:
        """判断当前工序是否可派发（前一序产出足够）"""
        # 第一道工序始终可派发
        if self.sequence == 1:
            return self.status == self.Status.PENDING
        
        # 其他工序需要前一工序有足够产出
        previous_order = DispatchOrder.objects.filter(
            production_order=self.production_order,
            sequence=self.sequence - 1
        ).first()
        
        if not previous_order:
            return False
        
        # 检查前一工序的已完成数量是否足够
        return previous_order.completed_quantity > 0

    def split(self, split_quantity: int) -> 'DispatchOrder':
        """拆分派工单

        派工单默认可拆分，除非生产数量为1

        Args:
            split_quantity: 拆分出的子工单数量
            
        Returns:
            DispatchOrder: 创建的子工单
        """
        with transaction.atomic():
            # 验证拆分数量（生产数量为1时不可拆分）
            if self.quantity == 1:
                raise ValueError("生产数量为1时不可拆分")
            
            if split_quantity >= self.quantity:
                raise ValueError("拆分数量必须小于原工单数量")
            
            remaining = self.quantity - self.completed_quantity
            if split_quantity > remaining:
                raise ValueError("拆分数量不能超过剩余未生产数量")
            
            # 创建子工单
            child_order = DispatchOrder.objects.create(
                production_order=self.production_order,
                process=self.process,
                sequence=self.sequence,
                quantity=split_quantity,
                status=self.status,
                parent=self,
                is_child=True
            )
            
            # 更新父工单数量
            self.quantity -= split_quantity
            self.is_parent = True
            self.save()
            
            return child_order

    def report(self, report_quantity: int) -> 'ProductionReport':
        """生产报工

        Args:
            report_quantity: 报工数量
            
        Returns:
            ProductionReport: 创建的报工记录
        """
        with transaction.atomic():
            # 验证报工数量
            remaining = self.quantity - self.completed_quantity
            if report_quantity > remaining:
                raise ValueError("报工数量不能超过剩余生产数量")
            
            # 创建报工记录
            report = ProductionReport.objects.create(
                dispatch_order=self,
                quantity=report_quantity,
                work_time=datetime.timedelta(hours=0)  # 暂时设为0，实际应从前端获取
            )
            
            # 更新已完成数量
            self.completed_quantity += report_quantity
            
            # 检查是否完成
            if self.completed_quantity >= self.quantity:
                self.status = self.Status.COMPLETED
                self.completed_quantity = self.quantity
            
            self.save()
            
            # 同步父工单状态
            if self.parent:
                self.sync_parent_status()
            
            # 触发下一工序可用
            self.trigger_next_process()
            
            return report

    def sync_parent_status(self) -> None:
        """递归同步父工单状态

        支持多级父子关系，从最底层子工单向上递归同步
        """
        if not self.parent:
            return
        
        parent = self.parent
        
        # 计算所有子工单的已完成数量之和
        children = DispatchOrder.objects.filter(parent=parent)
        total_completed = sum(c.completed_quantity for c in children)
        parent.completed_quantity = total_completed
        
        # 检查是否全部完成
        if all(c.status == self.Status.COMPLETED for c in children):
            parent.status = self.Status.COMPLETED
        
        parent.save()
        
        # 递归向上同步
        parent.sync_parent_status()

    def trigger_next_process(self) -> None:
        """触发下一工序可用"""
        # 获取下一工序的派工单
        next_order = DispatchOrder.objects.filter(
            production_order=self.production_order,
            sequence=self.sequence + 1
        ).first()
        
        if next_order and next_order.status == self.Status.WAITING_PREVIOUS:
            next_order.status = self.Status.PENDING
            next_order.save()


class ProductionReport(CoreModel):
    """生产报工模型"""

    code = models.CharField(max_length=100, unique=True, verbose_name="生产报工编码")
    dispatch_order = models.ForeignKey(DispatchOrder, on_delete=models.SET_NULL, null=True, related_name="production_reports", verbose_name="工序派工单")
    quantity = models.PositiveIntegerField(verbose_name="报工数量")
    work_time = models.DurationField(verbose_name="工作时间")
    report_date = models.DateField(verbose_name="报工日期", auto_now_add=True)


class QualityCheckOrder(CoreModel):
    """质检任务单模型"""

    class Type(models.TextChoices):
        """质检任务单类型"""

        FIRST = "first", "首检"
        PROCESS = "process", "过程检"
        COMPLETION = "completion", "完工检"

    class Status(models.TextChoices):
        """质检任务单状态"""

        PENDING = "pending", "待质检"
        PROGRESS = "progress", "质检中"
        COMPLETED = "completed", "已质检"

    FIRST_CHECK_PERCENTAGE = 10  # 首检比例 x=10%
    PROCESS_CHECK_INTERVAL = 30  # 过程检间隔 y=30%

    code = models.CharField(max_length=100, unique=True, verbose_name="质检任务单编码")
    type = models.CharField(max_length=10, verbose_name="质检任务单类型", choices=Type.choices, default=Type.PROCESS)
    status = models.CharField(max_length=20, verbose_name="状态", choices=Status.choices, default=Status.PENDING)
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.SET_NULL, null=True, related_name="quality_check_orders", verbose_name="生产任务单")
    product = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="quality_check_orders", verbose_name="产品")
    quantity = models.PositiveIntegerField(verbose_name="质检数量")
    qualified_quantity = models.PositiveIntegerField(verbose_name="合格品数量", default=0)
    unqualified_quantity = models.PositiveIntegerField(verbose_name="不合格品数量", default=0)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存质检任务单，自动生成编号.

        编号格式：QC-8位日期-4位序列号
        示例：QC-20250313-0001

        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if not self.code:
            self.code = generate_date_sequence_code(
                model_class=QualityCheckOrder,
                prefix="QC",
            )
        super().save(*args, **kwargs)

    @classmethod
    def auto_create_checks(cls, production_order: ProductionOrder, total_quantity: int) -> list:
        """根据生产数量自动创建质检任务

        Args:
            production_order: 生产任务单
            total_quantity: 总生产数量
            
        Returns:
            list: 创建的质检任务列表
        """
        with transaction.atomic():
            checks = []
            
            # 1. 首检：前10%的产品
            first_check_qty = max(1, int(total_quantity * cls.FIRST_CHECK_PERCENTAGE / 100))
            checks.append(cls.objects.create(
                production_order=production_order,
                product=production_order.product,
                type=cls.Type.FIRST,
                quantity=first_check_qty,
                status=cls.Status.PENDING
            ))
            
            # 2. 过程检：每隔30%的产品
            interval = max(1, int(total_quantity * cls.PROCESS_CHECK_INTERVAL / 100))
            for i in range(interval, total_quantity, interval):
                process_check_qty = min(interval, total_quantity - i)
                checks.append(cls.objects.create(
                    production_order=production_order,
                    product=production_order.product,
                    type=cls.Type.PROCESS,
                    quantity=process_check_qty,
                    status=cls.Status.PENDING
                ))
            
            # 3. 完工检：所有产品
            checks.append(cls.objects.create(
                production_order=production_order,
                product=production_order.product,
                type=cls.Type.COMPLETION,
                quantity=total_quantity,
                status=cls.Status.PENDING
            ))
            
            logger.info("已为生产任务单 %s 创建了 %d 个质检任务", production_order.code, len(checks))
            return checks
