"""用户认证和个人信息视图模块"""

from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from utils import DetailResponse, ErrorResponse


class LoginView(APIView):
    """登录视图"""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """用户登录

        Args:
            request: 包含 username 和 password 的登录请求
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 包含 access_token、refresh_token 和 csrf_token 的响应
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return ErrorResponse(msg="用户名和密码不能为空", status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return ErrorResponse(msg="用户名或密码错误", status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        refresh = RefreshToken.for_user(user)

        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "csrf_token": request.META.get("CSRF_COOKIE"),
        }
        return DetailResponse(data=data)


class LogoutView(APIView):
    """注销视图"""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """用户注销

        Args:
            request: 注销请求
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 注销成功或失败的响应
        """
        try:
            logout(request)
            return DetailResponse(data=None, msg="退出成功")
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """注册视图"""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """用户注册

        Args:
            request: 包含 username、password、email 和可选 name 的注册请求
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 包含新创建用户信息的响应
        """
        User = get_user_model()

        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")

        if not username or not password:
            return ErrorResponse(msg="用户名和密码不能为空", status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return ErrorResponse(msg="用户名已存在", status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return ErrorResponse(msg="邮箱已被注册", status=status.HTTP_400_BAD_REQUEST)

        if not name:
            name = f"用户_{uuid.uuid4().hex[:8]}"

        try:
            user = User.objects.create_user(
                username=username,
                email=email or "",
                password=password,
                name=name,
            )
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
            }
        }
        return DetailResponse(data=data)


class UserProfileView(APIView):
    """用户个人信息视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """获取当前用户信息

        Args:
            request: 认证后的请求对象
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 包含用户详细信息的响应
        """
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar.url if user.avatar else None,
            "role": user.role,
            "signature": user.signature,
        }
        return DetailResponse(data=data)

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """更新用户基本信息（昵称、邮箱、手机号、个性签名）

        Args:
            request: 包含 name、email、phone 和可选 signature 的更新请求
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 更新后的用户信息或错误响应
        """
        User = get_user_model()

        user = request.user
        data = request.data

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        signature = data.get("signature")

        if name is None or email is None or phone is None:
            return ErrorResponse(msg="name、email 和 phone 字段都必须提供", status=status.HTTP_400_BAD_REQUEST)

        if email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return ErrorResponse(msg="邮箱已被其他用户使用", status=status.HTTP_400_BAD_REQUEST)

        user.name = name
        user.email = email
        user.phone = phone

        if signature is not None:
            user.signature = signature

        try:
            user.save()
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar.url if user.avatar else None,
            "role": user.role,
            "signature": user.signature,
        }
        return DetailResponse(data=data)


class UserAvatarView(APIView):
    """用户头像上传视图"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """上传用户头像

        Args:
            request: 包含 avatar 文件的上传请求
            *args: 可变位置参数
            **kwargs: 可变关键字参数

        Returns:
            Response: 包含更新后用户信息的响应
        """
        user = request.user
        avatar = request.FILES.get("avatar")

        if not avatar:
            return ErrorResponse(msg="请上传头像文件", status=status.HTTP_400_BAD_REQUEST)

        user.avatar = avatar

        try:
            user.save()
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar.url if user.avatar else None,
            "role": user.role,
            "signature": user.signature,
        }
        return DetailResponse(data=data)
