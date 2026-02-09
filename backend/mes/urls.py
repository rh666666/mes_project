"""MES 应用 URL 配置"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceViewSet

# 创建路由器
router = DefaultRouter()

# 注册视图集
# DeviceViewSet - 设备相关 (增删改查、状态选项)
router.register(r"devices", DeviceViewSet, basename="devices")

urlpatterns = [
    path("", include(router.urls)),
]
