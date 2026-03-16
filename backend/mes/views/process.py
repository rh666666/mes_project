"""工序视图模块

该模块包含工序相关的视图集，处理工序、工序技能需求、工艺路线、
工艺路线详情的增删改查等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models.processes import Process, ProcessRoute, ProcessRouteDetail, ProcessSkillRequired
from mes.serializers.process import (
    ProcessCreateRequestSerializer,
    ProcessDetailResponseSerializer,
    ProcessListRequestSerializer,
    ProcessListResponseSerializer,
    ProcessRouteCreateRequestSerializer,
    ProcessRouteDetailCreateRequestSerializer,
    ProcessRouteDetailListRequestSerializer,
    ProcessRouteDetailListResponseSerializer,
    ProcessRouteDetailResponseSerializer,
    ProcessRouteDetailSerializer,
    ProcessRouteListRequestSerializer,
    ProcessRouteListResponseSerializer,
    ProcessRouteSerializer,
    ProcessRouteUpdateRequestSerializer,
    ProcessSerializer,
    ProcessSkillRequiredCreateRequestSerializer,
    ProcessSkillRequiredListRequestSerializer,
    ProcessSkillRequiredListResponseSerializer,
    ProcessSkillRequiredSerializer,
    ProcessUpdateRequestSerializer,
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


class ProcessViewSet(viewsets.ViewSet):
    """工序视图集

    处理工序的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取工序列表",
        description="获取工序列表，支持分页和按名称、编码过滤",
        parameters=[ProcessListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProcessListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工序"],
    )
    def list(self, request: Request) -> Response:
        """获取工序列表

        Args:
            request: 包含 page、limit 和可选 name、code 过滤条件的请求

        Returns:
            Response: 分页工序列表
        """
        serializer = ProcessListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        name_filter = serializer.validated_data.get("name")
        code_filter = serializer.validated_data.get("code")

        queryset = Process.objects.all().order_by("-create_datetime")

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
        if code_filter:
            queryset = queryset.filter(code__icontains=code_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        processes = queryset[start:end]

        return SuccessResponse(data=ProcessSerializer(processes, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取工序详情",
        description="根据工序ID获取工序详细信息",
        responses={
            200: OpenApiResponse(response=ProcessDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工序不存在"),
        },
        tags=["工序"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取工序详情

        Args:
            request: 请求对象
            pk: 工序ID

        Returns:
            Response: 工序详细信息
        """
        try:
            process = Process.objects.get(id=pk)
        except Process.DoesNotExist:
            return ErrorResponse(msg="工序不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=ProcessSerializer(process).data)

    @extend_schema(
        summary="创建工序",
        description="创建新工序，code 必须唯一",
        request=ProcessCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProcessDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或工序编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工序"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建工序

        Args:
            request: 包含 code、name、description 的创建请求

        Returns:
            Response: 创建的工序信息
        """
        serializer = ProcessCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        name = serializer.validated_data["name"]
        description = serializer.validated_data.get("description", "")

        if Process.objects.filter(code=code).exists():
            return ErrorResponse(msg="工序编码已存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            process = Process.objects.create(code=code, name=name, description=description)
            logger.info("工序已创建: %s (编码: %s)", name, code)
        except Exception as e:
            logger.error("创建工序失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessSerializer(process).data)

    @extend_schema(
        summary="更新工序",
        description="更新工序信息，code 必须唯一",
        request=ProcessUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProcessDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或工序编码已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工序不存在"),
        },
        tags=["工序"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新工序

        Args:
            request: 包含 code、name、description 的更新请求
            pk: 工序ID

        Returns:
            Response: 更新后的工序信息
        """
        try:
            process = Process.objects.get(id=pk)
        except Process.DoesNotExist:
            return ErrorResponse(msg="工序不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = ProcessUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get("code")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")

        if code is not None and code != process.code:
            if Process.objects.filter(code=code).exists():
                return ErrorResponse(msg="工序编码已存在", status=status.HTTP_400_BAD_REQUEST)
            process.code = code

        if name is not None:
            process.name = name

        if description is not None:
            process.description = description

        try:
            process.save()
            logger.info("工序已更新: %s (ID: %s)", process.name, pk)
        except Exception as e:
            logger.error("更新工序 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessSerializer(process).data)

    @extend_schema(
        summary="删除工序",
        description="删除指定工序",
        responses={
            200: OpenApiResponse(response=ProcessDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工序不存在"),
        },
        tags=["工序"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除工序

        Args:
            request: 请求对象
            pk: 工序ID

        Returns:
            Response: 删除结果
        """
        try:
            process = Process.objects.get(id=pk)
        except Process.DoesNotExist:
            return ErrorResponse(msg="工序不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            process_name = process.name
            process.delete()
            logger.info("工序已删除: %s (ID: %s)", process_name, pk)
        except Exception as e:
            logger.error("删除工序 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class ProcessSkillRequiredViewSet(viewsets.ViewSet):
    """工序技能需求视图集

    处理工序技能需求关联的增删查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取工序技能需求列表",
        description="获取工序技能需求关联列表，支持分页和按工序、技能过滤",
        parameters=[ProcessSkillRequiredListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProcessSkillRequiredListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工序技能需求"],
    )
    def list(self, request: Request) -> Response:
        """获取工序技能需求列表

        Args:
            request: 包含 page、limit 和可选 process、skill 过滤条件的请求

        Returns:
            Response: 分页工序技能需求列表
        """
        serializer = ProcessSkillRequiredListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        process_filter = serializer.validated_data.get("process")
        skill_filter = serializer.validated_data.get("skill")

        queryset = ProcessSkillRequired.objects.all().order_by("-create_datetime")

        if process_filter:
            queryset = queryset.filter(process_id=process_filter)
        if skill_filter:
            queryset = queryset.filter(skill_id=skill_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        process_skills = queryset[start:end]

        return SuccessResponse(
            data=ProcessSkillRequiredSerializer(process_skills, many=True).data,
            page=page,
            limit=limit,
            total=total,
        )

    @extend_schema(
        summary="创建工序技能需求关联",
        description="为工序分配技能需求",
        request=ProcessSkillRequiredCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或关联已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工序技能需求"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建工序技能需求关联

        Args:
            request: 包含 process、skill 的创建请求

        Returns:
            Response: 创建的工序技能需求关联信息
        """
        serializer = ProcessSkillRequiredCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        process_id = serializer.validated_data["process"]
        skill_id = serializer.validated_data["skill"]

        if ProcessSkillRequired.objects.filter(process_id=process_id, skill_id=skill_id).exists():
            return ErrorResponse(msg="该工序已需要此技能", status=status.HTTP_400_BAD_REQUEST)

        try:
            process_skill = ProcessSkillRequired.objects.create(process_id=process_id, skill_id=skill_id)
            logger.info("工序技能需求关联已创建: 工序ID=%s, 技能ID=%s", process_id, skill_id)
        except Exception as e:
            logger.error("创建工序技能需求关联失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessSkillRequiredSerializer(process_skill).data)

    @extend_schema(
        summary="删除工序技能需求关联",
        description="删除指定的工序技能需求关联",
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="关联不存在"),
        },
        tags=["工序技能需求"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除工序技能需求关联

        Args:
            request: 请求对象
            pk: 工序技能需求关联ID

        Returns:
            Response: 删除结果
        """
        try:
            process_skill = ProcessSkillRequired.objects.get(id=pk)
        except ProcessSkillRequired.DoesNotExist:
            return ErrorResponse(msg="工序技能需求关联不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            process_skill.delete()
            logger.info("工序技能需求关联已删除: ID=%s", pk)
        except Exception as e:
            logger.error("删除工序技能需求关联 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class ProcessRouteViewSet(viewsets.ViewSet):
    """工艺路线视图集

    处理工艺路线的增删改查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取工艺路线列表",
        description="获取工艺路线列表，支持分页和按物料过滤",
        parameters=[ProcessRouteListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProcessRouteListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工艺路线"],
    )
    def list(self, request: Request) -> Response:
        """获取工艺路线列表

        Args:
            request: 包含 page、limit 和可选 material 过滤条件的请求

        Returns:
            Response: 分页工艺路线列表
        """
        serializer = ProcessRouteListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        material_filter = serializer.validated_data.get("material")

        queryset = ProcessRoute.objects.all().order_by("-create_datetime")

        if material_filter:
            queryset = queryset.filter(material_id=material_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        process_routes = queryset[start:end]

        return SuccessResponse(
            data=ProcessRouteSerializer(process_routes, many=True).data,
            page=page,
            limit=limit,
            total=total,
        )

    @extend_schema(
        summary="获取工艺路线详情",
        description="根据工艺路线ID获取工艺路线详细信息",
        responses={
            200: OpenApiResponse(response=ProcessRouteDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工艺路线不存在"),
        },
        tags=["工艺路线"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取工艺路线详情

        Args:
            request: 请求对象
            pk: 工艺路线ID

        Returns:
            Response: 工艺路线详细信息
        """
        try:
            process_route = ProcessRoute.objects.get(id=pk)
        except ProcessRoute.DoesNotExist:
            return ErrorResponse(msg="工艺路线不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=ProcessRouteSerializer(process_route).data)

    @extend_schema(
        summary="创建工艺路线",
        description="创建新工艺路线，同一物料的 version 必须唯一",
        request=ProcessRouteCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProcessRouteDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或该物料的工艺路线版本已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工艺路线"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建工艺路线

        Args:
            request: 包含 material、version、description 的创建请求

        Returns:
            Response: 创建的工艺路线信息
        """
        from mes.models.materials import Material

        serializer = ProcessRouteCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        material_id = serializer.validated_data["material"]
        version = serializer.validated_data["version"]
        description = serializer.validated_data.get("description", "")

        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return ErrorResponse(msg="物料不存在", status=status.HTTP_400_BAD_REQUEST)

        if ProcessRoute.objects.filter(material=material, version=version).exists():
            return ErrorResponse(msg="该物料的工艺路线版本已存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            process_route = ProcessRoute.objects.create(material=material, version=version, description=description)
            logger.info("工艺路线已创建: 物料=%s, 版本=%s", material.code, version)
        except Exception as e:
            logger.error("创建工艺路线失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessRouteSerializer(process_route).data)

    @extend_schema(
        summary="更新工艺路线",
        description="更新工艺路线信息，同一物料的 version 必须唯一",
        request=ProcessRouteUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProcessRouteDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或该物料的工艺路线版本已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工艺路线不存在"),
        },
        tags=["工艺路线"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新工艺路线

        Args:
            request: 包含 version、description 的更新请求
            pk: 工艺路线ID

        Returns:
            Response: 更新后的工艺路线信息
        """
        try:
            process_route = ProcessRoute.objects.get(id=pk)
        except ProcessRoute.DoesNotExist:
            return ErrorResponse(msg="工艺路线不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = ProcessRouteUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        version = serializer.validated_data.get("version")
        description = serializer.validated_data.get("description")

        if version is not None and version != process_route.version:
            if ProcessRoute.objects.filter(material=process_route.material, version=version).exists():
                return ErrorResponse(msg="该物料的工艺路线版本已存在", status=status.HTTP_400_BAD_REQUEST)
            process_route.version = version

        if description is not None:
            process_route.description = description

        try:
            process_route.save()
            logger.info("工艺路线已更新: 物料=%s, 版本=%s (ID: %s)", process_route.material.code, process_route.version, pk)
        except Exception as e:
            logger.error("更新工艺路线 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessRouteSerializer(process_route).data)

    @extend_schema(
        summary="删除工艺路线",
        description="删除指定工艺路线",
        responses={
            200: OpenApiResponse(response=ProcessRouteDetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="工艺路线不存在"),
        },
        tags=["工艺路线"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除工艺路线

        Args:
            request: 请求对象
            pk: 工艺路线ID

        Returns:
            Response: 删除结果
        """
        try:
            process_route = ProcessRoute.objects.get(id=pk)
        except ProcessRoute.DoesNotExist:
            return ErrorResponse(msg="工艺路线不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            material_code = process_route.material.code
            process_route_version = process_route.version
            process_route.delete()
            logger.info("工艺路线已删除: 物料=%s, 版本=%s (ID: %s)", material_code, process_route_version, pk)
        except Exception as e:
            logger.error("删除工艺路线 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")


class ProcessRouteDetailViewSet(viewsets.ViewSet):
    """工艺路线详情视图集

    处理工艺路线详情关联的增删查操作，仅管理员可操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取工艺路线详情列表",
        description="获取工艺路线详情关联列表，支持分页和按工艺路线、工序过滤",
        parameters=[ProcessRouteDetailListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProcessRouteDetailListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工艺路线详情"],
    )
    def list(self, request: Request) -> Response:
        """获取工艺路线详情列表

        Args:
            request: 包含 page、limit 和可选 process_route、process 过滤条件的请求

        Returns:
            Response: 分页工艺路线详情列表
        """
        serializer = ProcessRouteDetailListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        process_route_filter = serializer.validated_data.get("process_route")
        process_filter = serializer.validated_data.get("process")

        queryset = ProcessRouteDetail.objects.all().order_by("process_route", "sequence")

        if process_route_filter:
            queryset = queryset.filter(process_route_id=process_route_filter)
        if process_filter:
            queryset = queryset.filter(process_id=process_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        route_details = queryset[start:end]

        return SuccessResponse(
            data=ProcessRouteDetailSerializer(route_details, many=True).data,
            page=page,
            limit=limit,
            total=total,
        )

    @extend_schema(
        summary="创建工艺路线详情关联",
        description="为工艺路线添加工序",
        request=ProcessRouteDetailCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="参数错误或关联已存在"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
        },
        tags=["工艺路线详情"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建工艺路线详情关联

        Args:
            request: 包含 process_route、process、sequence 的创建请求

        Returns:
            Response: 创建的工艺路线详情关联信息
        """
        serializer = ProcessRouteDetailCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        process_route_id = serializer.validated_data["process_route"]
        process_id = serializer.validated_data["process"]
        sequence = serializer.validated_data["sequence"]

        if ProcessRouteDetail.objects.filter(
            process_route_id=process_route_id, process_id=process_id
        ).exists():
            return ErrorResponse(msg="该工艺路线已包含此工序", status=status.HTTP_400_BAD_REQUEST)

        try:
            route_detail = ProcessRouteDetail.objects.create(
                process_route_id=process_route_id, process_id=process_id, sequence=sequence
            )
            logger.info("工艺路线详情关联已创建: 工艺路线ID=%s, 工序ID=%s, 顺序=%s", process_route_id, process_id, sequence)
        except Exception as e:
            logger.error("创建工艺路线详情关联失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProcessRouteDetailSerializer(route_detail).data)

    @extend_schema(
        summary="删除工艺路线详情关联",
        description="删除指定的工艺路线详情关联",
        responses={
            200: OpenApiResponse(response=DetailResponseSerializer, description="删除成功"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="无权限"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="关联不存在"),
        },
        tags=["工艺路线详情"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除工艺路线详情关联

        Args:
            request: 请求对象
            pk: 工艺路线详情关联ID

        Returns:
            Response: 删除结果
        """
        try:
            route_detail = ProcessRouteDetail.objects.get(id=pk)
        except ProcessRouteDetail.DoesNotExist:
            return ErrorResponse(msg="工艺路线详情关联不存在", status=status.HTTP_404_NOT_FOUND)

        try:
            route_detail.delete()
            logger.info("工艺路线详情关联已删除: ID=%s", pk)
        except Exception as e:
            logger.error("删除工艺路线详情关联 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")
