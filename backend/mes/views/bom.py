"""BOM 视图模块

该模块包含物料清单相关的视图集，处理物料清单和物料清单详情的增删改查等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models.bom import BillOfMaterial, BOMDetail
from mes.models.materials import Material
from mes.serializers.bom import (
    BillOfMaterialCreateRequestSerializer,
    BillOfMaterialDetailResponseSerializer,
    BillOfMaterialListRequestSerializer,
    BillOfMaterialListResponseSerializer,
    BillOfMaterialSerializer,
    BillOfMaterialUpdateRequestSerializer,
    BOMDetailCreateRequestSerializer,
    BOMDetailListRequestSerializer,
    BOMDetailListResponseSerializer,
    BOMDetailSerializer,
    BOMTreeResponseSerializer,
)
from utils import DetailResponse, ErrorResponse, SuccessResponse

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """自定义管理员权限类

    检查用户是否为管理员（is_staff、is_superuser 或 role="admin"）
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == "admin")


class BillOfMaterialViewSet(viewsets.ViewSet):
    """物料清单视图集

    处理物料清单的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取物料清单列表",
        description="获取物料清单列表，支持分页和按物料、版本过滤",
        parameters=[BillOfMaterialListRequestSerializer],
        responses={
            200: OpenApiResponse(response=BillOfMaterialListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["物料清单"],
    )
    def list(self, request: Request) -> Response:
        """获取物料清单列表

        Args:
            request: 包含 page、limit 和可选 material、version 过滤条件的请求

        Returns:
            Response: 分页物料清单列表
        """
        serializer = BillOfMaterialListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        material_filter = serializer.validated_data.get("material")
        version_filter = serializer.validated_data.get("version")

        queryset = BillOfMaterial.objects.all().order_by("-create_datetime")

        if material_filter:
            queryset = queryset.filter(material_id=material_filter)
        if version_filter:
            queryset = queryset.filter(version=version_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        boms = queryset[start:end]

        return SuccessResponse(data=BillOfMaterialSerializer(boms, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取物料清单详情",
        description="根据物料清单ID获取物料清单详细信息",
        responses={
            200: OpenApiResponse(response=BillOfMaterialDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="物料清单不存在"),
        },
        tags=["物料清单"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取物料清单详情

        Args:
            request: 请求对象
            pk: 物料清单ID

        Returns:
            Response: 物料清单详细信息
        """
        try:
            bom = BillOfMaterial.objects.get(id=pk)
        except BillOfMaterial.DoesNotExist:
            return ErrorResponse(msg="物料清单不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=BillOfMaterialSerializer(bom).data)

    @extend_schema(
        summary="创建物料清单",
        description="创建新物料清单",
        request=BillOfMaterialCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=BillOfMaterialDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误或物料不存在"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["物料清单"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建物料清单

        Args:
            request: 包含 material、version、is_active、description 的创建请求

        Returns:
            Response: 创建的物料清单信息
        """
        serializer = BillOfMaterialCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        material_id = serializer.validated_data["material"]
        version = serializer.validated_data["version"]
        is_active = serializer.validated_data.get("is_active", True)
        description = serializer.validated_data.get("description", "")

        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            bom = BillOfMaterial.objects.create(
                material=material,
                version=version,
                is_active=is_active,
                description=description,
            )
            logger.info("物料清单已创建: 物料=%s, 版本=%s", material.code, version)
        except Exception as e:
            logger.error("创建物料清单失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=BillOfMaterialSerializer(bom).data)

    @extend_schema(
        summary="更新物料清单",
        description="更新物料清单信息",
        request=BillOfMaterialUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=BillOfMaterialDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误或物料不存在"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="物料清单不存在"),
        },
        tags=["物料清单"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新物料清单

        Args:
            request: 包含 material、version、is_active、description 的更新请求
            pk: 物料清单ID

        Returns:
            Response: 更新后的物料清单信息
        """
        try:
            bom = BillOfMaterial.objects.get(id=pk)
        except BillOfMaterial.DoesNotExist:
            return ErrorResponse(msg="物料清单不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = BillOfMaterialUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        material_id = serializer.validated_data.get("material")
        version = serializer.validated_data.get("version")
        is_active = serializer.validated_data.get("is_active")
        description = serializer.validated_data.get("description")

        if material_id is not None:
            try:
                material = Material.objects.get(id=material_id)
                bom.material = material
            except Material.DoesNotExist:
                return ErrorResponse(msg="物料不存在", status=status.HTTP_400_BAD_REQUEST)

        if version is not None:
            bom.version = version

        if is_active is not None:
            bom.is_active = is_active

        if description is not None:
            bom.description = description

        try:
            bom.save()
            logger.info("物料清单已更新: ID=%s", pk)
        except Exception as e:
            logger.error("更新物料清单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=BillOfMaterialSerializer(bom).data)

    @extend_schema(
        summary="删除物料清单",
        description="删除指定物料清单",
        responses={
            200: OpenApiResponse(response=BillOfMaterialDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="物料清单不存在"),
        },
        tags=["物料清单"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除物料清单

        Args:
            request: 请求对象
            pk: 物料清单ID

        Returns:
            Response: 删除结果
        """
        try:
            bom = BillOfMaterial.objects.get(id=pk)
        except BillOfMaterial.DoesNotExist:
            return ErrorResponse(msg="物料清单不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            material_code = bom.material.code if bom.material else "Unknown"
            bom.delete()
            logger.info("物料清单已删除: 物料=%s, ID=%s", material_code, pk)
        except Exception as e:
            logger.error("删除物料清单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")

    @extend_schema(
        summary="获取BOM树形结构",
        description="根据物料清单ID获取完整的BOM树形结构",
        responses={
            200: OpenApiResponse(response=BOMTreeResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="物料清单不存在"),
        },
        tags=["物料清单"],
    )
    def tree(self, request: Request, pk: int) -> Response:
        """获取BOM树形结构

        Args:
            request: 请求对象
            pk: 物料清单ID

        Returns:
            Response: BOM树形结构
        """
        try:
            bom = BillOfMaterial.objects.get(id=pk)
        except BillOfMaterial.DoesNotExist:
            return ErrorResponse(msg="物料清单不存在", status=status.HTTP_404_NOT_FOUND)

        from mes.serializers.bom import BOMTreeSerializer

        serializer = BOMTreeSerializer(bom)
        return DetailResponse(data=serializer.data)


class BOMDetailViewSet(viewsets.ViewSet):
    """物料清单详情视图集

    处理物料清单详情的增删查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取物料清单详情列表",
        description="获取物料清单详情列表，支持分页和按物料清单、物料过滤",
        parameters=[BOMDetailListRequestSerializer],
        responses={
            200: OpenApiResponse(response=BOMDetailListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["物料清单详情"],
    )
    def list(self, request: Request) -> Response:
        """获取物料清单详情列表

        Args:
            request: 包含 page、limit 和可选 bom、material 过滤条件的请求

        Returns:
            Response: 分页物料清单详情列表
        """
        serializer = BOMDetailListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        bom_filter = serializer.validated_data.get("bom")
        material_filter = serializer.validated_data.get("material")

        queryset = BOMDetail.objects.all().order_by("-create_datetime")

        if bom_filter:
            queryset = queryset.filter(bom_id=bom_filter)
        if material_filter:
            queryset = queryset.filter(material_id=material_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        details = queryset[start:end]

        return SuccessResponse(data=BOMDetailSerializer(details, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="创建物料清单详情",
        description="创建新物料清单详情",
        request=BOMDetailCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponse, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误或物料清单/物料不存在"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["物料清单详情"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建物料清单详情

        Args:
            request: 包含 bom、material、sub_bom、quantity 的创建请求

        Returns:
            Response: 创建的物料清单详情信息
        """
        serializer = BOMDetailCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        bom_id = serializer.validated_data["bom"]
        material_id = serializer.validated_data["material"]
        sub_bom_id = serializer.validated_data.get("sub_bom")
        quantity = serializer.validated_data["quantity"]

        try:
            bom = BillOfMaterial.objects.get(id=bom_id)
        except BillOfMaterial.DoesNotExist:
            return ErrorResponse(msg="物料清单不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_400_BAD_REQUEST)

        sub_bom = None
        if sub_bom_id:
            try:
                sub_bom = BillOfMaterial.objects.get(id=sub_bom_id)
            except BillOfMaterial.DoesNotExist:
                return ErrorResponse(msg="子物料清单不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            detail = BOMDetail.objects.create(
                bom=bom,
                material=material,
                sub_bom=sub_bom,
                quantity=quantity,
            )
            logger.info("物料清单详情已创建: 物料清单ID=%s, 物料ID=%s", bom_id, material_id)
        except Exception as e:
            logger.error("创建物料清单详情失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=BOMDetailSerializer(detail).data)

    @extend_schema(
        summary="删除物料清单详情",
        description="删除指定物料清单详情",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="物料清单详情不存在"),
        },
        tags=["物料清单详情"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除物料清单详情

        Args:
            request: 请求对象
            pk: 物料清单详情ID

        Returns:
            Response: 删除结果
        """
        try:
            detail = BOMDetail.objects.get(id=pk)
        except BOMDetail.DoesNotExist:
            return ErrorResponse(msg="物料清单详情不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            detail.delete()
            logger.info("物料清单详情已删除: ID=%s", pk)
        except Exception as e:
            logger.error("删除物料清单详情 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")
