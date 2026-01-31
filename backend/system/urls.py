"""system 应用 URL 配置"""

from django.urls import path
from .views import CustomLoginView, CustomLogoutView, CustomRegisterView, UserProfileView, UserAvatarView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'),
    path('register/', CustomRegisterView.as_view(), name='custom_register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('upload_avatar/', UserAvatarView.as_view(), name='user_upload_avatar'),
]
