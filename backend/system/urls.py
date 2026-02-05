"""system 应用 URL 配置"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, DeptViewSet, UserViewSet

# 创建路由器
router = DefaultRouter()

# 注册视图集
# AuthViewSet - 认证相关 (登录、注销、注册)
router.register(r"", AuthViewSet, basename="auth")

# UserViewSet - 用户相关 (获取/更新个人信息、上传头像、管理员功能)
router.register(r"users", UserViewSet, basename="users")

# DeptViewSet - 部门相关 (增删改查)
router.register(r"depts", DeptViewSet, basename="depts")

urlpatterns = [
    path("", include(router.urls)),
]
