import datetime
import logging
from typing import Any

from django.db import models, transaction
from django.db.models import Max, Sum

from system.models import CoreModel
from utils import generate_date_sequence_code

from .bom import BillOfMaterial
from .devices import Device
from .materials import Material
from .processes import Process, ProcessRoute

logger = logging.getLogger(__name__)


def _build_route_output_bom_map(process_route: ProcessRoute) -> dict[int, BillOfMaterial]:
    """构建工艺路线「产出物料 -> 工序 BOM」映射。

    每个节点的 process_bom.material 表示该工序产出物，对应该工序绑定的 BOM。

    Args:
        process_route: 工艺路线实例

    Returns:
        dict: {产出物料 ID: BillOfMaterial}
    """
    mapping: dict[int, BillOfMaterial] = {}
    nodes = process_route.nodes.select_related("process_bom", "process_bom__material")
    for node in nodes:
        bom = node.process_bom
        if bom and bom.material_id:
            mapping[bom.material_id] = bom
    return mapping


def _get_terminal_product_bom(process_route: ProcessRoute, product_id: int) -> BillOfMaterial | None:
    """获取末序节点上、产出为成品的 BOM。

    末序指工艺路线图中无出边的节点；成品 BOM 应绑定在末序且 BOM 所属物料为任务单产品。

    Args:
        process_route: 工艺路线实例
        product_id: 成品物料 ID

    Returns:
        BillOfMaterial | None: 末序成品 BOM，无法解析时返回 None
    """
    nodes = list(process_route.nodes.select_related("process_bom", "process_bom__material"))
    if not nodes:
        return None

    from_node_ids = set(process_route.edges.values_list("from_node_id", flat=True))
    sink_nodes = [node for node in nodes if node.id not in from_node_ids]
    if not sink_nodes:
        sink_nodes = nodes

    for node in sink_nodes:
        bom = node.process_bom
        if bom and bom.material_id == product_id:
            return bom

    for node in sink_nodes:
        if node.process_bom_id:
            logger.warning(
                "工艺路线 %s 末序 BOM 物料与产品不一致，回退使用首个末序 BOM",
                process_route.id,
            )
            return node.process_bom

    return None


def _explode_bom_to_leaf_requirements(
    output_quantity: int,
    bom: BillOfMaterial,
    material_to_bom: dict[int, BillOfMaterial],
    requirements: dict[int, dict[str, Any]],
    visited_output_materials: set[int] | None = None,
) -> None:
    """将指定产出数量按 BOM 向下展开，仅累加叶子物料需求。

    子项若在本工艺路线中有对应产出 BOM，则继续展开；否则若明细配置了 sub_bom 则展开子 BOM；
    否则视为叶子物料。

    Args:
        output_quantity: 待产出的 BOM 所属物料数量
        bom: 当前层级 BOM
        material_to_bom: 路线产出物料到 BOM 的映射
        requirements: 叶子物料累加器，就地修改
        visited_output_materials: 已访问的产出物料 ID，用于环检测
    """
    if output_quantity <= 0 or not bom:
        return

    visited = set(visited_output_materials or [])
    output_material_id = bom.material_id
    if output_material_id:
        if output_material_id in visited:
            logger.warning("BOM 展开检测到环，物料 ID=%s", output_material_id)
            return
        visited.add(output_material_id)

    details = bom.bom_details.select_related("material", "sub_bom").all()
    for detail in details:
        if not detail.material_id:
            continue
        needed_qty = output_quantity * detail.quantity
        child_route_bom = material_to_bom.get(detail.material_id)
        if child_route_bom:
            _explode_bom_to_leaf_requirements(
                needed_qty,
                child_route_bom,
                material_to_bom,
                requirements,
                visited,
            )
        elif detail.sub_bom_id:
            _explode_bom_to_leaf_requirements(
                needed_qty,
                detail.sub_bom,
                material_to_bom,
                requirements,
                visited,
            )
        else:
            material = detail.material
            mid = material.id
            if mid not in requirements:
                requirements[mid] = {"material": material, "quantity": 0}
            requirements[mid]["quantity"] += int(needed_qty)


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
        """计算所需原材料数量（仅叶子物料）。

        从工艺路线末序绑定的成品 BOM 出发，按生产数量向下展开；中间产物通过
        前序工序绑定的 BOM 继续展开，直至无对应产出 BOM 的物料作为叶子节点累加。

        Returns:
            dict: {material_id: {material: Material, quantity: int}}
        """
        route = self.process_route
        if not route or not self.product_id:
            return {}

        terminal_bom = _get_terminal_product_bom(route, self.product_id)
        if not terminal_bom:
            return {}

        material_to_bom = _build_route_output_bom_map(route)
        requirements: dict[int, dict[str, Any]] = {}
        _explode_bom_to_leaf_requirements(
            self.quantity,
            terminal_bom,
            material_to_bom,
            requirements,
        )
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
        COMPLETED = "completed", "已完成"  # 生产完成（累计报工数量达到或超过计划数量）
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

    def peel_remainder_to_pending_child(self) -> 'DispatchOrder | None':
        """将父工单剩余可生产数量拆为待抢子工单。

        用于部分抢单/派工后，使余量仍以子工单形式出现在抢单中心。

        Returns:
            DispatchOrder | None: 新建的待抢子工单；无剩余可生产数量时返回 None
        """
        peel_qty = self.quantity - self.completed_quantity
        if peel_qty < 1:
            return None

        child_order = DispatchOrder.objects.create(
            production_order=self.production_order,
            process=self.process,
            sequence=self.sequence,
            quantity=peel_qty,
            status=self.Status.PENDING,
            parent=self,
            is_child=True,
        )
        self.quantity = self.completed_quantity
        self.is_parent = True
        self.save()
        return child_order

    def report(
        self,
        report_quantity: int,
        work_time: datetime.timedelta | None = None,
    ) -> 'ProductionReport':
        """生产报工

        允许累计报工数量超过计划生产数量（溢出报工）；达到或超过计划数量时标记为已完成，
        已完成数量保留实际报工累计值。

        Args:
            report_quantity: 报工数量
            work_time: 工作时间，缺省为 0

        Returns:
            ProductionReport: 创建的报工记录
        """
        if work_time is None:
            work_time = datetime.timedelta(0)

        with transaction.atomic():
            # 创建报工记录（编号在 ProductionReport.save 中自动生成）
            report = ProductionReport.objects.create(
                dispatch_order=self,
                quantity=report_quantity,
                work_time=work_time,
            )
            
            # 更新已完成数量
            self.completed_quantity += report_quantity
            
            # 达到或超过计划数量时标记完成（不截断已完成数量）
            if self.completed_quantity >= self.quantity:
                self.status = self.Status.COMPLETED
            
            self.save()
            
            # 同步父工单状态
            if self.parent:
                self.sync_parent_status()
            
            # 触发下一工序可用
            self.trigger_next_process()

            # 末序报工达到进度阈值时创建质检任务
            QualityCheckOrder.create_checks_on_report(self, report_quantity)
            
            return report

    def is_last_sequence(self) -> bool:
        """判断当前派工单是否为生产任务单的末序工序。

        Returns:
            bool: 末序为 True
        """
        if not self.production_order_id:
            return False
        agg = DispatchOrder.objects.filter(
            production_order_id=self.production_order_id,
        ).aggregate(max_seq=Max("sequence"))
        max_seq = agg["max_seq"]
        return max_seq is not None and self.sequence == max_seq

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

    def save(self, *args: Any, **kwargs: Any) -> None:
        """保存生产报工，自动生成编号.

        编号格式：PR-8位日期-4位序列号
        示例：PR-20250518-0001

        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        from django.db import IntegrityError

        if self.code:
            super().save(*args, **kwargs)
            return

        max_retries = 5
        for attempt in range(max_retries):
            self.code = generate_date_sequence_code(
                model_class=ProductionReport,
                prefix="PR",
            )
            try:
                super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.code = ""
                if attempt >= max_retries - 1:
                    raise


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
    def _get_last_sequence_max(cls, production_order_id: int) -> int | None:
        """获取生产任务单末序工序的 sequence 值。

        Args:
            production_order_id: 生产任务单 ID

        Returns:
            int | None: 末序 sequence，无派工单时返回 None
        """
        agg = DispatchOrder.objects.filter(
            production_order_id=production_order_id,
        ).aggregate(max_seq=Max("sequence"))
        return agg["max_seq"]

    @classmethod
    def _get_last_sequence_reported_quantity(cls, production_order_id: int) -> int:
        """汇总末序派工单的全部报工数量。

        Args:
            production_order_id: 生产任务单 ID

        Returns:
            int: 末序累计报工数量
        """
        max_seq = cls._get_last_sequence_max(production_order_id)
        if max_seq is None:
            return 0
        agg = ProductionReport.objects.filter(
            dispatch_order__production_order_id=production_order_id,
            dispatch_order__sequence=max_seq,
        ).aggregate(total=Sum("quantity"))
        return int(agg["total"] or 0)

    @classmethod
    def _process_check_milestones(cls, total_quantity: int) -> list[int]:
        """计算过程检进度档位（产量百分比对应的累计件数）。

        Args:
            total_quantity: 生产任务单计划数量

        Returns:
            list[int]: 按升序排列的档位累计件数
        """
        interval = max(1, int(total_quantity * cls.PROCESS_CHECK_INTERVAL / 100))
        return list(range(interval, total_quantity, interval))

    @classmethod
    def create_checks_on_report(
        cls,
        dispatch_order: DispatchOrder,
        report_quantity: int,
    ) -> list["QualityCheckOrder"]:
        """末序报工后按生产进度阈值创建质检任务。

        首检：末序累计报工首次达到计划产量 10% 时生成。
        过程检：每跨过计划产量 30% 的增量档位时生成一条。
        完工检：当前报工的末序派工单状态变为已完成时生成，数量为剩余未检数量。

        Args:
            dispatch_order: 报工的工序派工单
            report_quantity: 本次报工数量

        Returns:
            list[QualityCheckOrder]: 本次新创建的质检任务列表
        """
        if not dispatch_order.is_last_sequence():
            return []

        production_order = dispatch_order.production_order
        if not production_order or not production_order.product_id:
            logger.warning(
                "报工未触发质检：生产任务单或产品缺失，派工单 %s",
                dispatch_order.id,
            )
            return []

        total_quantity = production_order.quantity
        new_cumulative = cls._get_last_sequence_reported_quantity(production_order.id)
        prev_cumulative = new_cumulative - report_quantity
        created: list[QualityCheckOrder] = []

        # 首检
        first_threshold = max(1, int(total_quantity * cls.FIRST_CHECK_PERCENTAGE / 100))
        if (
            prev_cumulative < first_threshold <= new_cumulative
            and not cls.objects.filter(
                production_order=production_order,
                type=cls.Type.FIRST,
            ).exists()
        ):
            first_check_qty = max(1, int(total_quantity * cls.FIRST_CHECK_PERCENTAGE / 100))
            created.append(
                cls.objects.create(
                    production_order=production_order,
                    product=production_order.product,
                    type=cls.Type.FIRST,
                    quantity=first_check_qty,
                    status=cls.Status.PENDING,
                )
            )

        # 过程检
        interval = max(1, int(total_quantity * cls.PROCESS_CHECK_INTERVAL / 100))
        milestones = cls._process_check_milestones(total_quantity)
        existing_process_count = cls.objects.filter(
            production_order=production_order,
            type=cls.Type.PROCESS,
        ).count()
        newly_crossed = [
            m
            for m in milestones
            if prev_cumulative < m <= new_cumulative
        ]
        for offset, milestone in enumerate(newly_crossed):
            idx = existing_process_count + offset
            if idx >= len(milestones):
                break
            process_check_qty = min(interval, total_quantity - milestone)
            created.append(
                cls.objects.create(
                    production_order=production_order,
                    product=production_order.product,
                    type=cls.Type.PROCESS,
                    quantity=process_check_qty,
                    status=cls.Status.PENDING,
                )
            )

        # 完工检
        if (
            dispatch_order.status == DispatchOrder.Status.COMPLETED
            and not cls.objects.filter(
                production_order=production_order,
                type=cls.Type.COMPLETION,
            ).exists()
        ):
            inspected_agg = cls.objects.filter(
                production_order=production_order,
            ).aggregate(total=Sum("quantity"))
            already_inspected = int(inspected_agg["total"] or 0)
            remainder = total_quantity - already_inspected
            if remainder > 0:
                created.append(
                    cls.objects.create(
                        production_order=production_order,
                        product=production_order.product,
                        type=cls.Type.COMPLETION,
                        quantity=remainder,
                        status=cls.Status.PENDING,
                    )
                )

        if created:
            logger.info(
                "报工触发质检：生产任务单 %s，新建 %d 条质检任务",
                production_order.code,
                len(created),
            )
        return created
