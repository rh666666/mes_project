"""system 应用 URL 配置"""

from django.urls import path
from .views import CustomLoginView, CustomLogoutView, CustomRegisterView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'),
    path('register/', CustomRegisterView.as_view(), name='custom_register'),
]
