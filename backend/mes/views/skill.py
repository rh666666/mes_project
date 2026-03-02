"""技能视图模块

该模块包含技能相关的视图集，处理技能、用户技能、设备技能的增删改查等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models.skills import DeviceSkill, Skill, UserSkill
from mes.serializers.skill import (
    DeviceSkillCreateRequestSerializer,
    DeviceSkillListRequestSerializer,
    DeviceSkillListResponseSerializer,
    DeviceSkillSerializer,
    SkillCreateRequestSerializer,
    SkillDetailResponseSerializer,
    SkillListRequestSerializer,
    SkillListResponseSerializer,
    SkillSerializer,
    SkillUpdateRequestSerializer,
    UserSkillCreateRequestSerializer,
    UserSkillListRequestSerializer,
    UserSkillListResponseSerializer,
    UserSkillSerializer,
)
from utils import DetailResponse, DetailResponseSerializer, ErrorResponse, ErrorResponseSerializer, SuccessResponse

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """自定义管理员权限类

    检查用户是否为管理员（is_staff、is_superuser 或 role="admin"）
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == "admin")


class SkillViewSet(viewsets.ViewSet):
    """技能视图集

    处理技能的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取技能列表",
        description="获取技能列表，支持分页和按名称、编码、类型过滤",
        parameters=[SkillListRequestSerializer],
        responses={
            200: OpenApiResponse(response=SkillListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["技能"],
    )
    def list(self, request: Request) -> Response:
        """获取技能列表

        Args:
            request: 包含 page、limit 和可选 name、code、type 过滤条件的请求

        Returns:
            Response: 分页技能列表
        """
        serializer = SkillListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")
        code_filter = serializer.validated_data.get("code")
        type_filter = serializer.validated_data.get("type")

        queryset = Skill.objects.all().order_by("-create_datetime")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
        if code_filter:
            queryset = queryset.filter(code__icontains=code_filter)
        if type_filter:
            queryset = queryset.filter(type=type_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        skills = queryset[start:end]

        return SuccessResponse(data=SkillSerializer(skills, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取技能详情",
        description="根据技能ID获取技能详细信息",
        responses={
            200: OpenApiResponse(response=SkillDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="技能不存在"),
        },
        tags=["技能"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取技能详情

        Args:
            request: 请求对象
            pk: 技能ID

        Returns:
            Response: 技能详细信息
        """
        try:
            skill = Skill.objects.get(id=pk)
        except Skill.DoesNotExist:
            return ErrorResponse(msg="技能不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=SkillSerializer(skill).data)

    @extend_schema(
        summary="创建技能",
        description="创建新技能，code 必须唯一",
        request=SkillCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=SkillDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或技能编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["技能"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建技能

        Args:
            request: 包含 code、name、type 的创建请求

        Returns:
            Response: 创建的技能信息
        """
        serializer = SkillCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]
        skill_type = serializer.validated_data.get("type", Skill.Type.USER)

        if Skill.objects.filter(code=code).exists():
            return ErrorResponse(msg="技能编码已存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            skill = Skill.objects.create(code=code, name=name, type=skill_type)
            logger.info("技能已创建: %s (编码: %s, 类型: %s)", name, code, skill_type)
        except Exception as e:
            logger.error("创建技能失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=SkillSerializer(skill).data)

    @extend_schema(
        summary="更新技能",
        description="更新技能信息，code 必须唯一",
        request=SkillUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=SkillDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或技能编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="技能不存在"),
        },
        tags=["技能"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新技能

        Args:
            request: 包含 code、name、type 的更新请求
            pk: 技能ID

        Returns:
            Response: 更新后的技能信息
        """
        try:
            skill = Skill.objects.get(id=pk)
        except Skill.DoesNotExist:
            return ErrorResponse(msg="技能不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = SkillUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")
        skill_type = serializer.validated_data.get("type")

        if code is not None and code != skill.code:
            if Skill.objects.filter(code=code).exists():
                return ErrorResponse(msg="技能编码已存在", status=status.HTTP_400_BAD_REQUEST)
            skill.code = code

        if name is not None:
            skill.name = name

        if skill_type is not None:
            skill.type = skill_type

        try:
            skill.save()
            logger.info("技能已更新: %s (ID: %s)", skill.name, pk)
        except Exception as e:
            logger.error("更新技能 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=SkillSerializer(skill).data)

    @extend_schema(
        summary="删除技能",
        description="删除指定技能",
        responses={
            200: OpenApiResponse(response=SkillDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="技能不存在"),
        },
        tags=["技能"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除技能

        Args:
            request: 请求对象
            pk: 技能ID

        Returns:
            Response: 删除结果
        """
        try:
            skill = Skill.objects.get(id=pk)
        except Skill.DoesNotExist:
            return ErrorResponse(msg="技能不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            skill_name = skill.name
            skill.delete()
            logger.info("技能已删除: %s (ID: %s)", skill_name, pk)
        except Exception as e:
            logger.error("删除技能 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class UserSkillViewSet(viewsets.ViewSet):
    """用户技能视图集

    处理用户技能关联的增删查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取用户技能列表",
        description="获取用户技能关联列表，支持分页和按用户、技能过滤",
        parameters=[UserSkillListRequestSerializer],
        responses={
            200: OpenApiResponse(response=UserSkillListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["用户技能"],
    )
    def list(self, request: Request) -> Response:
        """获取用户技能列表

        Args:
            request: 包含 page、limit 和可选 user、skill 过滤条件的请求

        Returns:
            Response: 分页用户技能列表
        """
        serializer = UserSkillListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        user_filter = serializer.validated_data.get("user")
        skill_filter = serializer.validated_data.get("skill")

        queryset = UserSkill.objects.all().order_by("-create_datetime")

        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        if skill_filter:
            queryset = queryset.filter(skill_id=skill_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        user_skills = queryset[start:end]

        return SuccessResponse(data=UserSkillSerializer(user_skills, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="创建用户技能关联",
        description="为用户分配技能",
        request=UserSkillCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或关联已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["用户技能"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建用户技能关联

        Args:
            request: 包含 user、skill 的创建请求

        Returns:
            Response: 创建的用户技能关联信息
        """
        serializer = UserSkillCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user"]
        skill_id = serializer.validated_data["skill"]

        if UserSkill.objects.filter(user_id=user_id, skill_id=skill_id).exists():
            return ErrorResponse(msg="该用户已拥有此技能", status=status.HTTP_400_BAD_REQUEST)

        try:
            user_skill = UserSkill.objects.create(user_id=user_id, skill_id=skill_id)
            logger.info("用户技能关联已创建: 用户ID=%s, 技能ID=%s", user_id, skill_id)
        except Exception as e:
            logger.error("创建用户技能关联失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=UserSkillSerializer(user_skill).data)

    @extend_schema(
        summary="删除用户技能关联",
        description="删除指定的用户技能关联",
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="关联不存在"),
        },
        tags=["用户技能"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除用户技能关联

        Args:
            request: 请求对象
            pk: 用户技能关联ID

        Returns:
            Response: 删除结果
        """
        try:
            user_skill = UserSkill.objects.get(id=pk)
        except UserSkill.DoesNotExist:
            return ErrorResponse(msg="用户技能关联不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            user_skill.delete()
            logger.info("用户技能关联已删除: ID=%s", pk)
        except Exception as e:
            logger.error("删除用户技能关联 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class DeviceSkillViewSet(viewsets.ViewSet):
    """设备技能视图集

    处理设备技能关联的增删查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取设备技能列表",
        description="获取设备技能关联列表，支持分页和按设备、技能过滤",
        parameters=[DeviceSkillListRequestSerializer],
        responses={
            200: OpenApiResponse(response=DeviceSkillListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["设备技能"],
    )
    def list(self, request: Request) -> Response:
        """获取设备技能列表

        Args:
            request: 包含 page、limit 和可选 device、skill 过滤条件的请求

        Returns:
            Response: 分页设备技能列表
        """
        serializer = DeviceSkillListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        device_filter = serializer.validated_data.get("device")
        skill_filter = serializer.validated_data.get("skill")

        queryset = DeviceSkill.objects.all().order_by("-create_datetime")

        if device_filter:
            queryset = queryset.filter(device_id=device_filter)
        if skill_filter:
            queryset = queryset.filter(skill_id=skill_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        device_skills = queryset[start:end]

        return SuccessResponse(data=DeviceSkillSerializer(device_skills, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="创建设备技能关联",
        description="为设备分配技能",
        request=DeviceSkillCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或关联已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["设备技能"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建设备技能关联

        Args:
            request: 包含 device、skill 的创建请求

        Returns:
            Response: 创建的设备技能关联信息
        """
        serializer = DeviceSkillCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        device_id = serializer.validated_data["device"]
        skill_id = serializer.validated_data["skill"]

        if DeviceSkill.objects.filter(device_id=device_id, skill_id=skill_id).exists():
            return ErrorResponse(msg="该设备已拥有此技能", status=status.HTTP_400_BAD_REQUEST)

        try:
            device_skill = DeviceSkill.objects.create(device_id=device_id, skill_id=skill_id)
            logger.info("设备技能关联已创建: 设备ID=%s, 技能ID=%s", device_id, skill_id)
        except Exception as e:
            logger.error("创建设备技能关联失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=DeviceSkillSerializer(device_skill).data)

    @extend_schema(
        summary="删除设备技能关联",
        description="删除指定的设备技能关联",
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="关联不存在"),
        },
        tags=["设备技能"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除设备技能关联

        Args:
            request: 请求对象
            pk: 设备技能关联ID

        Returns:
            Response: 删除结果
        """
        try:
            device_skill = DeviceSkill.objects.get(id=pk)
        except DeviceSkill.DoesNotExist:
            return ErrorResponse(msg="设备技能关联不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            device_skill.delete()
            logger.info("设备技能关联已删除: ID=%s", pk)
        except Exception as e:
            logger.error("删除设备技能关联 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")
