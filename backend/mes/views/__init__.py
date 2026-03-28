"""MES 视图模块

该模块包含 MES 应用相关的所有视图集。
"""

from .bom import BillOfMaterialViewSet, BOMDetailViewSet
from .device import DeviceViewSet
from .material import MaterialViewSet, UnitViewSet
from .orders import DispatchOrderViewSet, ProductionOrderViewSet, ProductionReportViewSet, QualityCheckOrderViewSet
from .process import ProcessRouteDetailViewSet, ProcessRouteViewSet, ProcessSkillRequiredViewSet, ProcessViewSet
from .skill import DeviceSkillViewSet, SkillViewSet, UserSkillViewSet

__all__ = [
    "BOMDetailViewSet",
    "BillOfMaterialViewSet",
    "DeviceSkillViewSet",
    "DeviceViewSet",
    "DispatchOrderViewSet",
    "MaterialViewSet",
    "ProcessRouteDetailViewSet",
    "ProcessRouteViewSet",
    "ProcessSkillRequiredViewSet",
    "ProcessViewSet",
    "ProductionOrderViewSet",
    "ProductionReportViewSet",
    "QualityCheckOrderViewSet",
    "SkillViewSet",
    "UnitViewSet",
    "UserSkillViewSet",
]
