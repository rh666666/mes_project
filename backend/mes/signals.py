"""MES 模块信号处理器.

本模块包含工单数据异常时的自动废弃信号处理逻辑。
当关联数据被删除时，相关工单将自动标记为废弃状态。
"""

import logging
from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver

from mes.models.materials import Material
from mes.models.orders import DispatchOrder, ProductionOrder
from mes.models.processes import Process, ProcessRoute

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Material)
def obsolete_production_orders_on_material_delete(
    sender: type[Material],
    instance: Material,
    **kwargs: Any,
) -> None:
    """当产品被删除时，废弃关联的生产任务单.

    Args:
        sender: 发送信号的模型类
        instance: 被删除的物料实例
        **kwargs: 额外参数
    """
    obsolete_count = ProductionOrder.objects.filter(
        product=None,
    ).exclude(
        status__in=[
            ProductionOrder.Status.COMPLETED,
            ProductionOrder.Status.OBSOLETE,
        ],
    ).update(status=ProductionOrder.Status.OBSOLETE)

    if obsolete_count > 0:
        logger.info(
            "Material %s deleted, obsoleted %s production orders",
            instance.code,
            obsolete_count,
        )


@receiver(post_delete, sender=ProcessRoute)
def obsolete_production_orders_on_process_route_delete(
    sender: type[ProcessRoute],
    instance: ProcessRoute,
    **kwargs: Any,
) -> None:
    """当工艺路线被删除时，废弃关联的生产任务单.

    Args:
        sender: 发送信号的模型类
        instance: 被删除的工艺路线实例
        **kwargs: 额外参数
    """
    obsolete_count = ProductionOrder.objects.filter(
        process_route=None,
    ).exclude(
        status__in=[
            ProductionOrder.Status.COMPLETED,
            ProductionOrder.Status.OBSOLETE,
        ],
    ).update(status=ProductionOrder.Status.OBSOLETE)

    if obsolete_count > 0:
        logger.info(
            "ProcessRoute %s deleted, obsoleted %s production orders",
            instance,
            obsolete_count,
        )


@receiver(post_delete, sender=Process)
def obsolete_dispatch_orders_on_process_delete(
    sender: type[Process],
    instance: Process,
    **kwargs: Any,
) -> None:
    """当工序被删除时，废弃关联的工序派工单.

    Args:
        sender: 发送信号的模型类
        instance: 被删除的工序实例
        **kwargs: 额外参数
    """
    obsolete_count = DispatchOrder.objects.filter(
        process=None,
    ).exclude(
        status__in=[
            DispatchOrder.Status.COMPLETED,
            DispatchOrder.Status.OBSOLETE,
        ],
    ).update(status=DispatchOrder.Status.OBSOLETE)

    if obsolete_count > 0:
        logger.info(
            "Process %s deleted, obsoleted %s dispatch orders",
            instance.code,
            obsolete_count,
        )


@receiver(post_delete, sender=ProductionOrder)
def obsolete_dispatch_orders_on_production_order_delete(
    sender: type[ProductionOrder],
    instance: ProductionOrder,
    **kwargs: Any,
) -> None:
    """当生产任务单被删除时，废弃关联的工序派工单.

    Args:
        sender: 发送信号的模型类
        instance: 被删除的生产任务单实例
        **kwargs: 额外参数
    """
    obsolete_count = DispatchOrder.objects.filter(
        production_order=None,
    ).exclude(
        status__in=[
            DispatchOrder.Status.COMPLETED,
            DispatchOrder.Status.OBSOLETE,
        ],
    ).update(status=DispatchOrder.Status.OBSOLETE)

    if obsolete_count > 0:
        logger.info(
            "ProductionOrder %s deleted, obsoleted %s dispatch orders",
            instance.code,
            obsolete_count,
        )
