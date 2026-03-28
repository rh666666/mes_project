"""MES 应用 URL 配置"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BillOfMaterialViewSet,
    BOMDetailViewSet,
    DeviceSkillViewSet,
    DeviceViewSet,
    DispatchOrderViewSet,
    MaterialViewSet,
    ProcessRouteDetailViewSet,
    ProcessRouteViewSet,
    ProcessSkillRequiredViewSet,
    ProcessViewSet,
    ProductionOrderViewSet,
    ProductionReportViewSet,
    QualityCheckOrderViewSet,
    SkillViewSet,
    UnitViewSet,
    UserSkillViewSet,
)

# 创建路由器
router = DefaultRouter()

# 注册视图集
# UnitViewSet - 单位相关 (增删改查)
router.register(r"units", UnitViewSet, basename="units")
# MaterialViewSet - 物料相关 (增删改查)
router.register(r"materials", MaterialViewSet, basename="materials")
# DeviceViewSet - 设备相关 (增删改查、状态选项)
router.register(r"devices", DeviceViewSet, basename="devices")
# SkillViewSet - 技能相关 (增删改查)
router.register(r"skills", SkillViewSet, basename="skills")
# ProcessViewSet - 工序相关 (增删改查)
router.register(r"processes", ProcessViewSet, basename="processes")
# ProcessRouteViewSet - 工艺路线相关 (增删改查)
router.register(r"process-routes", ProcessRouteViewSet, basename="process-routes")
# BillOfMaterialViewSet - 物料清单相关 (增删改查、树形结构)
router.register(r"boms", BillOfMaterialViewSet, basename="boms")
# ProductionOrderViewSet - 生产任务单相关 (增删改查、下发、取消)
router.register(r"production-orders", ProductionOrderViewSet, basename="production-orders")
# DispatchOrderViewSet - 工序派工单相关 (查询、派工、抢单、报工等)
router.register(r"dispatch-orders", DispatchOrderViewSet, basename="dispatch-orders")
# ProductionReportViewSet - 生产报工相关 (查询)
router.register(r"production-reports", ProductionReportViewSet, basename="production-reports")
# QualityCheckOrderViewSet - 质检任务单相关 (查询、提交结果)
router.register(r"quality-check-orders", QualityCheckOrderViewSet, basename="quality-check-orders")

# 用户技能关联子路由
user_skill_patterns = [
    path("", UserSkillViewSet.as_view({"get": "list", "post": "create"}), name="user-skills-list"),
    path("<int:pk>/", UserSkillViewSet.as_view({"delete": "destroy"}), name="user-skills-detail"),
]

# 设备技能关联子路由
device_skill_patterns = [
    path("", DeviceSkillViewSet.as_view({"get": "list", "post": "create"}), name="device-skills-list"),
    path("<int:pk>/", DeviceSkillViewSet.as_view({"delete": "destroy"}), name="device-skills-detail"),
]

# 工序技能需求关联子路由
process_skill_patterns = [
    path("", ProcessSkillRequiredViewSet.as_view({"get": "list", "post": "create"}), name="process-skills-list"),
    path("<int:pk>/", ProcessSkillRequiredViewSet.as_view({"delete": "destroy"}), name="process-skills-detail"),
]

# 工艺路线详情关联子路由
process_route_detail_patterns = [
    path("", ProcessRouteDetailViewSet.as_view({"get": "list", "post": "create"}), name="process-route-details-list"),
    path("<int:pk>/", ProcessRouteDetailViewSet.as_view({"delete": "destroy"}), name="process-route-details-detail"),
]

# BOM详情关联子路由
bom_detail_patterns = [
    path("", BOMDetailViewSet.as_view({"get": "list", "post": "create"}), name="bom-details-list"),
    path("<int:pk>/", BOMDetailViewSet.as_view({"delete": "destroy"}), name="bom-details-detail"),
]

urlpatterns = [
    # 用户技能关联路由 /skills/users/ - 必须放在 router.urls 之前
    path("skills/users/", include(user_skill_patterns)),
    # 设备技能关联路由 /skills/devices/ - 必须放在 router.urls 之前
    path("skills/devices/", include(device_skill_patterns)),
    # 工序技能需求关联路由 /processes/skills/ - 必须放在 router.urls 之前
    path("processes/skills/", include(process_skill_patterns)),
    # 工艺路线详情关联路由 /process-routes/details/ - 必须放在 router.urls 之前
    path("process-routes/details/", include(process_route_detail_patterns)),
    # BOM详情关联路由 /boms/details/ - 必须放在 router.urls 之前
    path("boms/details/", include(bom_detail_patterns)),
    # 路由器 URL - 放在最后，避免与上面的子路由冲突
    path("", include(router.urls)),
]
