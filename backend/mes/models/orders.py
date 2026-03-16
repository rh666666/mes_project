import logging
from typing import Any

from django.db import models

from system.models import CoreModel
from utils import generate_date_sequence_code

from .materials import Material
from .processes import Process, ProcessRoute

logger = logging.getLogger(__name__)


class ProductionOrder(CoreModel):
    """生产任务单模型"""

    class Status(models.TextChoices):
        PENDING = "pending", "已创建"       # 生产任务单（生产订单）由管理员手动生成
        PUBLISHED = "published", "已下发"   # 管理员手动下发任务单，任务单自动拆分为工序派工单
        CANCELLED = "cancelled", "已取消"   # 管理员手动取消任务单，同时，对应的所有工序派工单也会被取消
        COMPLETED = "completed", "已完成"   # 当所有工序派工单完成后，任务单状态变更为已完成
        OBSOLETE = "obsolete", "已废弃"     # 数据异常时（如产品被删除，或工艺路线被删除等），任务单将自动废弃

    code = models.CharField(max_length=100, unique=True, verbose_name="生产任务单编码")
    product = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="production_orders", verbose_name="产品")
    quantity = models.PositiveIntegerField(verbose_name="生产数量")
    status = models.CharField(max_length=10, verbose_name="状态", choices=Status.choices, default=Status.PENDING)
    process_route = models.ForeignKey(ProcessRoute, on_delete=models.SET_NULL, null=True, related_name="production_orders", verbose_name="工艺路线")

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


class DispatchOrder(CoreModel):
    """工序派工单模型"""

    class Status(models.TextChoices):
        PENDING = "pending", "待抢单"       # 派工单创建后默认为待抢单状态
        DISPATCHED = "dispatched", "已派工" # 管理员手动将派工单派工后，状态变更为已派工
        GRABBED = "grabbed", "已抢单"       # 员工手动抢单后，状态变更为已抢单
        PAUSED = "paused", "已暂停"         # 员工手动暂停生产后，状态变更为已暂停
        CANCELLED = "cancelled", "已取消"   # 员工不可取消派工单，由管理员手动取消
        COMPLETED = "completed", "已完成"   # 生产完成（报工数量等于生产数量）
        OBSOLETE = "obsolete", "已废弃"     # 数据异常时（如工序被删除，或父级任务单被删除等），派工单将自动废弃

    code = models.CharField(max_length=100, unique=True, verbose_name="工序派工单编码")
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="生产任务单")
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, related_name="dispatch_orders", verbose_name="工序")
    quantity = models.PositiveIntegerField(verbose_name="生产数量")
    status = models.CharField(max_length=10, verbose_name="状态", choices=Status.choices, default=Status.PENDING)

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


class ProductionReport(CoreModel):
    """生产报工模型"""
    
    code = models.CharField(max_length=100, unique=True, verbose_name="生产报工编码")
    dispatch_order = models.ForeignKey(DispatchOrder, on_delete=models.SET_NULL, null=True, related_name="production_reports", verbose_name="工序派工单")
    quantity = models.PositiveIntegerField(verbose_name="报工数量")