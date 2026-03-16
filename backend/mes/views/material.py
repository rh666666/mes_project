"""物料视图模块

该模块包含物料和单位相关的视图集，处理物料和单位的增删改查等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models import Material, Unit
from mes.serializers.material import (
    MaterialCreateRequestSerializer,
    MaterialDetailResponseSerializer,
    MaterialListRequestSerializer,
    MaterialListResponseSerializer,
    MaterialSerializer,
    MaterialUpdateRequestSerializer,
    UnitCreateRequestSerializer,
    UnitDetailResponseSerializer,
    UnitListRequestSerializer,
    UnitListResponseSerializer,
    UnitSerializer,
    UnitUpdateRequestSerializer,
)
from utils import DetailResponse, ErrorResponse, ErrorResponseSerializer, SuccessResponse

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    自定义管理员权限类

    检查用户是否为管理员（is_staff、is_superuser 或 role="admin"）
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == "admin")


class UnitViewSet(viewsets.ViewSet):
    """单位视图集

    处理单位的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取单位列表",
        description="获取单位列表，支持分页和按名称、编码过滤",
        parameters=[UnitListRequestSerializer],
        responses={
            200: OpenApiResponse(response=UnitListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["单位"],
    )
    def list(self, request: Request) -> Response:
        """获取单位列表

        Args:
            request: 包含 page、limit 和可选 name、code 过滤条件的请求

        Returns:
            Response: 分页单位列表
        """
        serializer = UnitListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")
        code_filter = serializer.validated_data.get("code")

        queryset = Unit.objects.all().order_by("-create_datetime")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
        if code_filter:
            queryset = queryset.filter(code__icontains=code_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        units = queryset[start:end]

        return SuccessResponse(data=UnitSerializer(units, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取单位详情",
        description="根据单位ID获取单位详细信息",
        responses={
            200: OpenApiResponse(response=UnitDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="单位不存在"),
        },
        tags=["单位"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取单位详情

        Args:
            request: 请求对象
            pk: 单位ID

        Returns:
            Response: 单位详细信息
        """
        try:
            unit = Unit.objects.get(id=pk)
        except Unit.DoesNotExist:
            return ErrorResponse(msg="单位不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=UnitSerializer(unit).data)

    @extend_schema(
        summary="创建单位",
        description="创建新单位，code 必须唯一",
        request=UnitCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=UnitDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或单位编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["单位"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建单位

        Args:
            request: 包含 code、name、description 的创建请求

        Returns:
            Response: 创建的单位信息
        """
        serializer = UnitCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]
        description = serializer.validated_data.get("description")

        if Unit.objects.filter(code=code).exists():
            return ErrorResponse(msg="单位编码已存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            unit = Unit.objects.create(code=code, name=name, description=description)
            logger.info("单位已创建: %s (编码: %s)", name, code)
        except Exception as e:
            logger.error("创建单位失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=UnitSerializer(unit).data)

    @extend_schema(
        summary="更新单位",
        description="更新单位信息，code 必须唯一",
        request=UnitUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=UnitDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或单位编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="单位不存在"),
        },
        tags=["单位"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新单位

        Args:
            request: 包含 code、name、description 的更新请求
            pk: 单位ID

        Returns:
            Response: 更新后的单位信息
        """
        try:
            unit = Unit.objects.get(id=pk)
        except Unit.DoesNotExist:
            return ErrorResponse(msg="单位不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = UnitUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")

        if code is not None and code != unit.code:
            if Unit.objects.filter(code=code).exists():
                return ErrorResponse(msg="单位编码已存在", status=status.HTTP_400_BAD_REQUEST)
            unit.code = code

        if name is not None:
            unit.name = name

        if description is not None:
            unit.description = description

        try:
            unit.save()
            logger.info("单位已更新: %s (ID: %s)", unit.name, pk)
        except Exception as e:
            logger.error("更新单位 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=UnitSerializer(unit).data)

    @extend_schema(
        summary="删除单位",
        description="删除指定单位",
        responses={
            200: OpenApiResponse(response=UnitDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="单位不存在"),
        },
        tags=["单位"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除单位

        Args:
            request: 请求对象
            pk: 单位ID

        Returns:
            Response: 删除结果
        """
        try:
            unit = Unit.objects.get(id=pk)
        except Unit.DoesNotExist:
            return ErrorResponse(msg="单位不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            unit_name = unit.name
            unit.delete()
            logger.info("单位已删除: %s (ID: %s)", unit_name, pk)
        except Exception as e:
            logger.error("删除单位 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class MaterialViewSet(viewsets.ViewSet):
    """物料视图集

    处理物料的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取物料列表",
        description="获取物料列表，支持分页和按名称、编码过滤",
        parameters=[MaterialListRequestSerializer],
        responses={
            200: OpenApiResponse(response=MaterialListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["物料"],
    )
    def list(self, request: Request) -> Response:
        """获取物料列表

        Args:
            request: 包含 page、limit 和可选 name、code 过滤条件的请求

        Returns:
            Response: 分页物料列表
        """
        serializer = MaterialListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")
        code_filter = serializer.validated_data.get("code")

        queryset = Material.objects.all().select_related("unit").order_by("-create_datetime")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
        if code_filter:
            queryset = queryset.filter(code__icontains=code_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        materials = queryset[start:end]

        return SuccessResponse(data=MaterialSerializer(materials, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取物料详情",
        description="根据物料ID获取物料详细信息",
        responses={
            200: OpenApiResponse(response=MaterialDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="物料不存在"),
        },
        tags=["物料"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取物料详情

        Args:
            request: 请求对象
            pk: 物料ID

        Returns:
            Response: 物料详细信息
        """
        try:
            material = Material.objects.select_related("unit").get(id=pk)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=MaterialSerializer(material).data)

    @extend_schema(
        summary="创建物料",
        description="创建新物料，code 必须唯一，可关联单位",
        request=MaterialCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=MaterialDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误、物料编码已存在或单位不存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["物料"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建物料

        Args:
            request: 包含 code、name、description、unit_id 的创建请求

        Returns:
            Response: 创建的物料信息
        """
        serializer = MaterialCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]
        description = serializer.validated_data.get("description")
        unit_id = serializer.validated_data.get("unit_id")
        is_production = serializer.validated_data.get("is_production", False)

        if Material.objects.filter(code=code).exists():
            return ErrorResponse(msg="物料编码已存在", status=status.HTTP_400_BAD_REQUEST)

        unit = None
        if unit_id is not None:
            try:
                unit = Unit.objects.get(id=unit_id)
            except Unit.DoesNotExist:
                return ErrorResponse(msg="单位不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            material = Material.objects.create(
                code=code, name=name, description=description, unit=unit, is_production=is_production
            )
            logger.info("物料已创建: %s (编码: %s)", name, code)
        except Exception as e:
            logger.error("创建物料失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=MaterialSerializer(material).data)

    @extend_schema(
        summary="更新物料",
        description="更新物料信息，code 必须唯一，可修改单位关联",
        request=MaterialUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=MaterialDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误、物料编码已存在或单位不存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="物料不存在"),
        },
        tags=["物料"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新物料

        Args:
            request: 包含 code、name、description、unit_id 的更新请求
            pk: 物料ID

        Returns:
            Response: 更新后的物料信息
        """
        try:
            material = Material.objects.get(id=pk)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = MaterialUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")
        unit_id = serializer.validated_data.get("unit_id")
        is_production = serializer.validated_data.get("is_production")

        if code is not None and code != material.code:
            if Material.objects.filter(code=code).exists():
                return ErrorResponse(msg="物料编码已存在", status=status.HTTP_400_BAD_REQUEST)
            material.code = code

        if name is not None:
            material.name = name

        if description is not None:
            material.description = description

        if is_production is not None:
            material.is_production = is_production

        if unit_id is not None:
            try:
                unit = Unit.objects.get(id=unit_id)
                material.unit = unit
            except Unit.DoesNotExist:
                return ErrorResponse(msg="单位不存在", status=status.HTTP_400_BAD_REQUEST)
        elif "unit_id" in request.data and unit_id is None:
            material.unit = None

        try:
            material.save()
            logger.info("物料已更新: %s (ID: %s)", material.name, pk)
        except Exception as e:
            logger.error("更新物料 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=MaterialSerializer(material).data)

    @extend_schema(
        summary="删除物料",
        description="删除指定物料",
        responses={
            200: OpenApiResponse(response=MaterialDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="物料不存在"),
        },
        tags=["物料"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除物料

        Args:
            request: 请求对象
            pk: 物料ID

        Returns:
            Response: 删除结果
        """
        try:
            material = Material.objects.get(id=pk)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            material_name = material.name
            material.delete()
            logger.info("物料已删除: %s (ID: %s)", material_name, pk)
        except Exception as e:
            logger.error("删除物料 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")
