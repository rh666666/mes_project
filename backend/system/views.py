"""用户认证和个人信息视图模块"""

from __future__ import annotations

import logging
import re
import uuid

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from utils import DetailResponse, ErrorResponse, ErrorResponseSerializer, SuccessResponse

from .models import Dept
from .serializers import (
    AvatarUploadRequestSerializer,
    AvatarUploadResponseSerializer,
    DeptCreateRequestSerializer,
    DeptDetailResponseSerializer,
    DeptListRequestSerializer,
    DeptListResponseSerializer,
    DeptSerializer,
    DeptUpdateRequestSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    LogoutRequestSerializer,
    LogoutResponseSerializer,
    RegisterRequestSerializer,
    RegisterResponseSerializer,
    UserAdminUpdateRequestSerializer,
    UserListRequestSerializer,
    UserListResponseSerializer,
    UserProfileResponseSerializer,
    UserProfileUpdateRequestSerializer,
    UserProfileUpdateResponseSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    自定义管理员权限类

    检查用户是否为管理员（is_staff、is_superuser 或 role="admin"）
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == "admin")


class AuthViewSet(viewsets.ViewSet):
    """认证视图集

    处理用户登录、注销和注册等认证相关操作。
    """

    @extend_schema(
        summary="用户登录",
        description="使用用户名和密码进行登录，返回 JWT 令牌和 CSRF 令牌。登录后旧令牌将失效。",
        request=LoginRequestSerializer,
        responses={
            200: OpenApiResponse(response=LoginResponseSerializer, description="登录成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="请求参数错误"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="认证失败"),
        },
        tags=["认证"],
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request: Request) -> Response:
        """用户登录

        Args:
            request: 包含 username 和 password 的登录请求

        Returns:
            Response: 包含 access_token、refresh_token 和 csrf_token 的响应
        """
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)

        if user is None:
            return ErrorResponse(msg="用户名或密码错误", status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        # 将用户之前的 refresh token 加入黑名单（如果存在）
        # 注意：这需要客户端在登录时提供旧的 refresh token
        old_refresh_token = request.data.get("old_refresh")
        if old_refresh_token:
            try:
                token = RefreshToken(old_refresh_token)
                token.blacklist()
            except Exception:
                pass  # 忽略旧令牌无效的情况

        refresh = RefreshToken.for_user(user)

        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "csrf_token": request.META.get("CSRF_COOKIE"),
        }
        return DetailResponse(data=data)

    @extend_schema(
        summary="用户注销",
        description="注销当前登录用户，清除会话并使 JWT 令牌失效",
        request=LogoutRequestSerializer,
        responses={
            200: OpenApiResponse(response=LogoutResponseSerializer, description="注销成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="注销失败"),
        },
        tags=["认证"],
    )
    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[IsAuthenticated])
    def logout(self, request: Request) -> Response:
        """用户注销

        Args:
            request: 注销请求，包含 refresh token

        Returns:
            Response: 注销成功或失败的响应
        """
        serializer = LogoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data.get("refresh")

        try:
            # 将 refresh token 加入黑名单
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            logout(request)
            return DetailResponse(data=None, msg="退出成功")
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="用户注册",
        description="创建新用户账号，用户名和密码为必填项，密码需8-22位且包含字母和数字",
        request=RegisterRequestSerializer,
        responses={
            200: OpenApiResponse(response=RegisterResponseSerializer, description="注册成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="注册失败，参数错误或用户已存在"),
        },
        tags=["认证"],
    )
    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request: Request) -> Response:
        """用户注册

        Args:
            request: 包含 username、password、email 和可选 name 的注册请求

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

        # 密码强度校验
        if len(password) < 8 or len(password) > 22:
            return ErrorResponse(msg="密码长度必须在 8-22 位之间", status=status.HTTP_400_BAD_REQUEST)

        if not re.search(r"[a-zA-Z]", password):
            return ErrorResponse(msg="密码必须包含至少一个字母", status=status.HTTP_400_BAD_REQUEST)

        if not re.search(r"\d", password):
            return ErrorResponse(msg="密码必须包含至少一个数字", status=status.HTTP_400_BAD_REQUEST)

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

        return DetailResponse(data=UserSerializer(user).data)


class DeptViewSet(viewsets.ViewSet):
    """部门视图集

    处理部门的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取部门列表",
        description="获取部门列表，支持分页和按名称过滤",
        parameters=[DeptListRequestSerializer],
        responses={
            200: OpenApiResponse(response=DeptListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["部门"],
    )
    def list(self, request: Request) -> Response:
        """获取部门列表

        Args:
            request: 包含 page、limit 和可选 name 过滤条件的请求

        Returns:
            Response: 分页部门列表
        """
        serializer = DeptListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")

        queryset = Dept.objects.all().order_by("id")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        depts = queryset[start:end]

        return SuccessResponse(data=DeptSerializer(depts, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取部门详情",
        description="根据部门ID获取部门详细信息",
        responses={
            200: OpenApiResponse(response=DeptDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="部门不存在"),
        },
        tags=["部门"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取部门详情

        Args:
            request: 请求对象
            pk: 部门ID

        Returns:
            Response: 部门详细信息
        """
        try:
            dept = Dept.objects.get(id=pk)
        except Dept.DoesNotExist:
            return ErrorResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=DeptSerializer(dept).data)

    @extend_schema(
        summary="创建部门",
        description="创建新部门，code 必须唯一",
        request=DeptCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DeptDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或部门编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["部门"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建部门

        Args:
            request: 包含 code、name 和可选 parent 的创建请求

        Returns:
            Response: 创建的部门信息
        """
        serializer = DeptCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]
        parent_id = serializer.validated_data.get("parent")

        if Dept.objects.filter(code=code).exists():
            return ErrorResponse(msg="部门编码已存在", status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id is not None:
            try:
                parent = Dept.objects.get(id=parent_id)
            except Dept.DoesNotExist:
                return ErrorResponse(msg="父级部门不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            dept = Dept.objects.create(code=code, name=name, parent=parent)
            logger.info("部门已创建: %s (编码: %s)", name, code)
        except Exception as e:
            logger.error("创建部门失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=DeptSerializer(dept).data)

    @extend_schema(
        summary="更新部门",
        description="更新部门信息，code 必须唯一",
        request=DeptUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DeptDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或部门编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="部门不存在"),
        },
        tags=["部门"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新部门

        Args:
            request: 包含 code、name 和/或 parent 的更新请求
            pk: 部门ID

        Returns:
            Response: 更新后的部门信息
        """
        try:
            dept = Dept.objects.get(id=pk)
        except Dept.DoesNotExist:
            return ErrorResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = DeptUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")
        parent_id = serializer.validated_data.get("parent")

        if code is not None and code != dept.code:
            if Dept.objects.filter(code=code).exists():
                return ErrorResponse(msg="部门编码已存在", status=status.HTTP_400_BAD_REQUEST)
            dept.code = code

        if name is not None:
            dept.name = name

        if parent_id is not None:
            if parent_id == pk:
                return ErrorResponse(msg="不能将自己设为父级部门", status=status.HTTP_400_BAD_REQUEST)
            try:
                parent = Dept.objects.get(id=parent_id)
                dept.parent = parent
            except Dept.DoesNotExist:
                return ErrorResponse(msg="父级部门不存在", status=status.HTTP_400_BAD_REQUEST)
        elif "parent" in request.data and parent_id is None:
            dept.parent = None

        try:
            dept.save()
            logger.info("部门已更新: %s (ID: %s)", dept.name, pk)
        except Exception as e:
            logger.error("更新部门 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=DeptSerializer(dept).data)

    @extend_schema(
        summary="删除部门",
        description="删除指定部门",
        responses={
            200: OpenApiResponse(response=DeptDetailResponseSerializer, description="删除成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="删除失败，部门下存在子部门或用户"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="部门不存在"),
        },
        tags=["部门"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除部门

        Args:
            request: 请求对象
            pk: 部门ID

        Returns:
            Response: 删除结果
        """
        try:
            dept = Dept.objects.get(id=pk)
        except Dept.DoesNotExist:
            return ErrorResponse(msg="部门不存在", status=status.HTTP_404_NOT_FOUND)

        if dept.children.exists():
            return ErrorResponse(msg="该部门下存在子部门，无法删除", status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        if User.objects.filter(dept=dept).exists():
            return ErrorResponse(msg="该部门下存在用户，无法删除", status=status.HTTP_400_BAD_REQUEST)

        try:
            dept_name = dept.name
            dept.delete()
            logger.info("部门已删除: %s (ID: %s)", dept_name, pk)
        except Exception as e:
            logger.error("删除部门 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class UserViewSet(viewsets.ViewSet):
    """用户视图集

    处理用户信息查询和修改操作，包括当前用户操作和管理员操作。
    """

    def get_permissions(self):
        """根据操作类型返回不同的权限类"""
        if self.action in ["list", "admin_update"]:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="获取用户信息",
        description="获取当前登录用户的详细信息",
        methods=["GET"],
        responses={
            200: OpenApiResponse(response=UserProfileResponseSerializer, description="获取成功"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="未认证"),
        },
        tags=["用户"],
    )
    @extend_schema(
        summary="更新用户信息",
        description="更新当前登录用户的基本信息（昵称、邮箱、手机号、个性签名）",
        methods=["PUT"],
        request=UserProfileUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileUpdateResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或邮箱已被使用"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="未认证"),
        },
        tags=["用户"],
    )
    @transaction.atomic
    @action(detail=False, methods=["get", "put"], url_path="me")
    def me(self, request: Request) -> Response:
        """获取或更新当前用户信息

        Args:
            request: 认证后的请求对象

        Returns:
            Response: 包含用户详细信息的响应
        """
        user = request.user

        if request.method == "GET":
            return DetailResponse(data=UserSerializer(user).data)

        # PUT 请求处理更新
        data = request.data
        User = get_user_model()

        # 普通用户只能修改基本信息，不允许修改 role 和 dept
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        signature = data.get("signature")

        if name is None or email is None or phone is None:
            return ErrorResponse(msg="name、email 和 phone 字段都必须提供", status=status.HTTP_400_BAD_REQUEST)

        if email != user.email and User.objects.filter(email=email).exclude(id=user.id).exists():
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

        return DetailResponse(data=UserSerializer(user).data)

    @extend_schema(
        summary="上传头像",
        description="上传用户头像图片文件",
        request=AvatarUploadRequestSerializer,
        responses={
            200: OpenApiResponse(response=AvatarUploadResponseSerializer, description="上传成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="未上传文件或上传失败"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="未认证"),
        },
        tags=["用户"],
    )
    @action(detail=False, methods=["post"], url_path="me/avatar")
    def upload_avatar(self, request: Request) -> Response:
        """上传用户头像

        Args:
            request: 包含 avatar 文件的上传请求

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

        return DetailResponse(data=UserSerializer(user).data)

    @extend_schema(
        summary="获取用户列表",
        description="管理员可获取用户列表，支持分页和过滤",
        parameters=[UserListRequestSerializer],
        responses={
            200: OpenApiResponse(response=UserListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["用户"],
    )
    def list(self, request: Request) -> Response:
        """获取用户列表（管理员）

        Args:
            request: 包含 page、limit 和可选过滤条件的请求

        Returns:
            Response: 分页用户列表
        """
        serializer = UserListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        search_filter = serializer.validated_data.get("search")
        role_filter = serializer.validated_data.get("role")
        dept_filter = serializer.validated_data.get("dept")

        User = get_user_model()
        queryset = User.objects.all().order_by("id")

        # 应用过滤条件
        if search_filter:
            queryset = queryset.filter(
                Q(username__icontains=search_filter) | Q(name__icontains=search_filter)
            )
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        if dept_filter:
            queryset = queryset.filter(dept_id=dept_filter)

        # 计算分页
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        users = queryset[start:end]

        return SuccessResponse(data=UserSerializer(users, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="管理员更新用户信息",
        description="管理员可更新任意用户的 role 和 dept 字段",
        request=UserAdminUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileUpdateResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="用户不存在"),
        },
        tags=["用户"],
    )
    @action(detail=True, methods=["put"], url_path="admin-update")
    def admin_update(self, request: Request, pk: int) -> Response:
        """管理员更新用户 role 和 dept

        Args:
            request: 包含 role 和/或 dept 的更新请求
            pk: 目标用户 ID

        Returns:
            Response: 更新后的用户信息或错误响应
        """
        User = get_user_model()

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return ErrorResponse(msg="用户不存在", status=status.HTTP_404_NOT_FOUND)

        data = request.data
        role = data.get("role")
        dept_id = data.get("dept")

        if role is not None:
            user.role = role

        if dept_id is not None:
            try:
                dept = Dept.objects.get(id=dept_id)
                user.dept = dept
            except Dept.DoesNotExist:
                return ErrorResponse(msg="部门不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            user.save()
        except Exception as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=UserSerializer(user).data)

