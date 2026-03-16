"""MES 视图模块

该模块包含 MES 应用相关的所有视图集。
"""

from .device import DeviceViewSet
from .material import MaterialViewSet, UnitViewSet
from .process import ProcessRouteDetailViewSet, ProcessRouteViewSet, ProcessSkillRequiredViewSet, ProcessViewSet
from .skill import DeviceSkillViewSet, SkillViewSet, UserSkillViewSet

__all__ = [
    "DeviceSkillViewSet",
    "DeviceViewSet",
    "MaterialViewSet",
    "ProcessRouteDetailViewSet",
    "ProcessRouteViewSet",
    "ProcessSkillRequiredViewSet",
    "ProcessViewSet",
    "SkillViewSet",
    "UnitViewSet",
    "UserSkillViewSet",
]
