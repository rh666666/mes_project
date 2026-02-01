"""system 应用 URL 配置"""

from django.urls import path
from .views import LoginView, LogoutView, RegisterView, UserProfileView, UserAvatarView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("upload_avatar/", UserAvatarView.as_view(), name="user_upload_avatar"),
]
