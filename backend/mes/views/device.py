"""设备视图模块

该模块包含设备相关的视图集，处理设备的增删改查等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models import Device
from mes.serializers.device import (
    DeviceCreateRequestSerializer,
    DeviceDetailResponseSerializer,
    DeviceListRequestSerializer,
    DeviceListResponseSerializer,
    DeviceSerializer,
    DeviceUpdateRequestSerializer,
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


class DeviceViewSet(viewsets.ViewSet):
    """设备视图集

    处理设备的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取设备列表",
        description="获取设备列表，支持分页和按名称、状态过滤",
        parameters=[DeviceListRequestSerializer],
        responses={
            200: OpenApiResponse(response=DeviceListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["设备"],
    )
    def list(self, request: Request) -> Response:
        """获取设备列表

        Args:
            request: 包含 page、limit 和可选 name、status 过滤条件的请求

        Returns:
            Response: 分页设备列表
        """
        serializer = DeviceListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")
        status_filter = serializer.validated_data.get("status")

        queryset = Device.objects.all().order_by("-create_datetime")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        devices = queryset[start:end]

        return SuccessResponse(data=DeviceSerializer(devices, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取设备详情",
        description="根据设备ID获取设备详细信息",
        responses={
            200: OpenApiResponse(response=DeviceDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="设备不存在"),
        },
        tags=["设备"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取设备详情

        Args:
            request: 请求对象
            pk: 设备ID

        Returns:
            Response: 设备详细信息
        """
        try:
            device = Device.objects.get(id=pk)
        except Device.DoesNotExist:
            return ErrorResponse(msg="设备不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=DeviceSerializer(device).data)

    @extend_schema(
        summary="创建设备",
        description="创建新设备，code 必须唯一",
        request=DeviceCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DeviceDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或设备编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["设备"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建设备

        Args:
            request: 包含 code、name 的创建请求

        Returns:
            Response: 创建的设备信息
        """
        serializer = DeviceCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]

        if Device.objects.filter(code=code).exists():
            return ErrorResponse(msg="设备编码已存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.create(code=code, name=name, status=Device.Status.IDLE)
            logger.info("设备已创建: %s (编码: %s)", name, code)
        except Exception as e:
            logger.error("创建设备失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=DeviceSerializer(device).data)

    @extend_schema(
        summary="更新设备",
        description="更新设备信息，code 必须唯一",
        request=DeviceUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DeviceDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或设备编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="设备不存在"),
        },
        tags=["设备"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新设备

        Args:
            request: 包含 code、name 的更新请求
            pk: 设备ID

        Returns:
            Response: 更新后的设备信息
        """
        try:
            device = Device.objects.get(id=pk)
        except Device.DoesNotExist:
            return ErrorResponse(msg="设备不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = DeviceUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")

        if code is not None and code != device.code:
            if Device.objects.filter(code=code).exists():
                return ErrorResponse(msg="设备编码已存在", status=status.HTTP_400_BAD_REQUEST)
            device.code = code

        if name is not None:
            device.name = name

        try:
            device.save()
            logger.info("设备已更新: %s (ID: %s)", device.name, pk)
        except Exception as e:
            logger.error("更新设备 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=DeviceSerializer(device).data)

    @extend_schema(
        summary="删除设备",
        description="删除指定设备",
        responses={
            200: OpenApiResponse(response=DeviceDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="设备不存在"),
        },
        tags=["设备"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除设备

        Args:
            request: 请求对象
            pk: 设备ID

        Returns:
            Response: 删除结果
        """
        try:
            device = Device.objects.get(id=pk)
        except Device.DoesNotExist:
            return ErrorResponse(msg="设备不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            device_name = device.name
            device.delete()
            logger.info("设备已删除: %s (ID: %s)", device_name, pk)
        except Exception as e:
            logger.error("删除设备 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")
