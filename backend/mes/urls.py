"""MES 应用 URL 配置"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceSkillViewSet, DeviceViewSet, SkillViewSet, UserSkillViewSet

# 创建路由器
router = DefaultRouter()

# 注册视图集
# DeviceViewSet - 设备相关 (增删改查、状态选项)
router.register(r"devices", DeviceViewSet, basename="devices")
# SkillViewSet - 技能相关 (增删改查)
router.register(r"skills", SkillViewSet, basename="skills")

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

urlpatterns = [
    # 用户技能关联路由 /skills/users/ - 必须放在 router.urls 之前
    path("skills/users/", include(user_skill_patterns)),
    # 设备技能关联路由 /skills/devices/ - 必须放在 router.urls 之前
    path("skills/devices/", include(device_skill_patterns)),
    # 路由器 URL - 放在最后，避免与上面的子路由冲突
    path("", include(router.urls)),
]
