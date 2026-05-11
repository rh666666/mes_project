"""工单视图模块

该模块包含工单相关的视图集，处理生产任务单、工序派工单、生产报工和质检任务单等操作。
"""

from __future__ import annotations

import logging

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from mes.models.orders import DispatchOrder, ProductionOrder, ProductionReport, QualityCheckOrder
from mes.models.processes import ProcessRoute
from mes.serializers.orders import (
    DispatchOrderDetailResponseSerializer,
    DispatchOrderListRequestSerializer,
    DispatchOrderListResponseSerializer,
    DispatchOrderSerializer,
    DispatchOrderSplitRequestSerializer,
    ProductionOrderCreateRequestSerializer,
    ProductionOrderDetailResponseSerializer,
    ProductionOrderListRequestSerializer,
    ProductionOrderListResponseSerializer,
    ProductionOrderSerializer,
    ProductionOrderUpdateRequestSerializer,
    ProductionReportCreateRequestSerializer,
    ProductionReportListRequestSerializer,
    ProductionReportListResponseSerializer,
    ProductionReportSerializer,
    QualityCheckOrderListRequestSerializer,
    QualityCheckOrderListResponseSerializer,
    QualityCheckOrderSerializer,
    QualityCheckOrderSubmitResultRequestSerializer,
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


class ProductionOrderViewSet(viewsets.ViewSet):
    """生产任务单视图集

    处理生产任务单的增删改查、下发、取消等操作。
    """

    permission_classes = [IsAdmin]

    @extend_schema(
        summary="获取生产任务单列表",
        description="获取生产任务单列表，支持分页和按产品、状态过滤",
        parameters=[ProductionOrderListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProductionOrderListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["生产任务单"],
    )
    def list(self, request: Request) -> Response:
        """获取生产任务单列表

        Args:
            request: 包含 page、limit 和可选 product、status 过滤条件的请求

        Returns:
            Response: 分页生产任务单列表
        """
        serializer = ProductionOrderListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        product_filter = serializer.validated_data.get("product")
        status_filter = serializer.validated_data.get("status")

        queryset = ProductionOrder.objects.all().order_by("-create_datetime")

        if product_filter:
            queryset = queryset.filter(product_id=product_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        orders = queryset[start:end]

        return SuccessResponse(data=ProductionOrderSerializer(orders, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取生产任务单详情",
        description="根据生产任务单ID获取详细信息",
        responses={
            200: OpenApiResponse(response=ProductionOrderDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取生产任务单详情

        Args:
            request: 请求对象
            pk: 生产任务单ID

        Returns:
            Response: 生产任务单详细信息
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=ProductionOrderSerializer(order).data)

    @extend_schema(
        summary="创建生产任务单",
        description="创建新生产任务单",
        request=ProductionOrderCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProductionOrderDetailResponseSerializer, description="创建成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误或产品/工艺路线不存在"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["生产任务单"],
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        """创建生产任务单

        Args:
            request: 包含 product、quantity、process_route 的创建请求

        Returns:
            Response: 创建的生产任务单信息
        """
        serializer = ProductionOrderCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]
        process_route_id = serializer.validated_data["process_route"]
        description = serializer.validated_data.get("description", "")

        try:
            from mes.models.materials import Material
            product = Material.objects.get(id=product_id)
        except Exception:
            return ErrorResponse(msg="产品不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            process_route = ProcessRoute.objects.get(id=process_route_id)
        except ProcessRoute.DoesNotExist:
            return ErrorResponse(msg="工艺路线不存在", status=status.HTTP_400_BAD_REQUEST)

        try:
            order = ProductionOrder.objects.create(
                product=product,
                quantity=quantity,
                process_route=process_route,
                description=description,
            )
            logger.info("生产任务单已创建: 产品=%s, 数量=%d", product.code, quantity)
        except Exception as e:
            logger.error("创建生产任务单失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProductionOrderSerializer(order).data)

    @extend_schema(
        summary="更新生产任务单",
        description="更新生产任务单信息（仅允许更新未下发的任务单）",
        request=ProductionOrderUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=ProductionOrderDetailResponseSerializer, description="更新成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误或任务单已下发"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    @transaction.atomic
    def update(self, request: Request, pk: int) -> Response:
        """更新生产任务单

        Args:
            request: 包含 product、quantity、process_route 的更新请求
            pk: 生产任务单ID

        Returns:
            Response: 更新后的生产任务单信息
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        # 只允许更新未下发的任务单
        if order.status != ProductionOrder.Status.PENDING:
            return ErrorResponse(msg="只能更新未下发的任务单", status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductionOrderUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data.get("product")
        quantity = serializer.validated_data.get("quantity")
        process_route_id = serializer.validated_data.get("process_route")
        description = serializer.validated_data.get("description")

        if product_id is not None:
            try:
                from mes.models.materials import Material
                product = Material.objects.get(id=product_id)
                order.product = product
            except Exception:
                return ErrorResponse(msg="产品不存在", status=status.HTTP_400_BAD_REQUEST)

        if quantity is not None:
            order.quantity = quantity

        if process_route_id is not None:
            try:
                process_route = ProcessRoute.objects.get(id=process_route_id)
                order.process_route = process_route
            except ProcessRoute.DoesNotExist:
                return ErrorResponse(msg="工艺路线不存在", status=status.HTTP_400_BAD_REQUEST)

        if description is not None:
            order.description = description

        try:
            order.save()
            logger.info("生产任务单已更新: ID=%s", pk)
        except Exception as e:
            logger.error("更新生产任务单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=ProductionOrderSerializer(order).data)

    @extend_schema(
        summary="删除生产任务单",
        description="删除指定生产任务单（仅允许删除未下发的任务单）",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="删除成功"),
            400: OpenApiResponse(response=ErrorResponse, description="任务单已下发"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    @transaction.atomic
    def destroy(self, request: Request, pk: int) -> Response:
        """删除生产任务单

        Args:
            request: 请求对象
            pk: 生产任务单ID

        Returns:
            Response: 删除结果
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        # 只允许删除未下发的任务单
        if order.status != ProductionOrder.Status.PENDING:
            return ErrorResponse(msg="只能删除未下发的任务单", status=status.HTTP_400_BAD_REQUEST)

        try:
            order_code = order.code
            order.delete()
            logger.info("生产任务单已删除: 编码=%s, ID=%s", order_code, pk)
        except Exception as e:
            logger.error("删除生产任务单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

        return DetailResponse(data=None, msg="删除成功")

    @extend_schema(
        summary="下发生产任务单",
        description="下发生产任务单，自动拆分为工序派工单",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="下发成功"),
            400: OpenApiResponse(response=ErrorResponse, description="任务单状态不正确"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def publish(self, request: Request, pk: int) -> Response:
        """下发生产任务单

        Args:
            request: 请求对象
            pk: 生产任务单ID

        Returns:
            Response: 下发结果
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        if order.status != ProductionOrder.Status.PENDING:
            return ErrorResponse(msg="只能下发未下发的任务单", status=status.HTTP_400_BAD_REQUEST)

        try:
            dispatch_orders = order.publish()
            # 自动创建质检任务
            QualityCheckOrder.auto_create_checks(order, order.quantity)
            return DetailResponse(data={
                "production_order": ProductionOrderSerializer(order).data,
                "dispatch_orders_count": len(dispatch_orders)
            }, msg="下发成功")
        except Exception as e:
            logger.error("下发任务单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="取消生产任务单",
        description="取消生产任务单及所有关联派工单",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="取消成功"),
            400: OpenApiResponse(response=ErrorResponse, description="任务单状态不正确"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def cancel(self, request: Request, pk: int) -> Response:
        """取消生产任务单

        Args:
            request: 请求对象
            pk: 生产任务单ID

        Returns:
            Response: 取消结果
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        if order.status not in [ProductionOrder.Status.PENDING, ProductionOrder.Status.PUBLISHED]:
            return ErrorResponse(msg="只能取消未下发或已下发的任务单", status=status.HTTP_400_BAD_REQUEST)

        try:
            order.cancel()
            return DetailResponse(data=ProductionOrderSerializer(order).data, msg="取消成功")
        except Exception as e:
            logger.error("取消任务单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="获取原材料需求",
        description="根据生产任务单ID获取所需原材料数量",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产任务单不存在"),
        },
        tags=["生产任务单"],
    )
    @action(detail=True, methods=["get"])
    def material_requirements(self, request: Request, pk: int) -> Response:
        """获取原材料需求

        Args:
            request: 请求对象
            pk: 生产任务单ID

        Returns:
            Response: 原材料需求列表
        """
        try:
            order = ProductionOrder.objects.get(id=pk)
        except ProductionOrder.DoesNotExist:
            return ErrorResponse(msg="生产任务单不存在", status=status.HTTP_404_NOT_FOUND)

        requirements = order.calculate_material_requirements()
        return DetailResponse(data={
            str(m_id): {
                "material_code": info["material"].code,
                "material_name": info["material"].name,
                "quantity": info["quantity"]
            }
            for m_id, info in requirements.items()
        })


class DispatchOrderViewSet(viewsets.ViewSet):
    """工序派工单视图集

    处理工序派工单的查询、派工、抢单、开始、暂停、拆分、报工等操作。
    """

    def get_permissions(self):
        if self.action in ["grab", "start", "pause", "report"]:
            return [IsAuthenticated()]
        return [IsAdmin()]

    @extend_schema(
        summary="获取工序派工单列表",
        description="获取工序派工单列表，支持分页和按生产任务单、工序、状态过滤",
        parameters=[DispatchOrderListRequestSerializer],
        responses={
            200: OpenApiResponse(response=DispatchOrderListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["工序派工单"],
    )
    def list(self, request: Request) -> Response:
        """获取工序派工单列表

        Args:
            request: 包含 page、limit 和可选过滤条件的请求

        Returns:
            Response: 分页工序派工单列表
        """
        serializer = DispatchOrderListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        production_order_filter = serializer.validated_data.get("production_order")
        process_filter = serializer.validated_data.get("process")
        status_filter = serializer.validated_data.get("status")

        queryset = DispatchOrder.objects.all().order_by("-create_datetime")

        if production_order_filter:
            queryset = queryset.filter(production_order_id=production_order_filter)
        if process_filter:
            queryset = queryset.filter(process_id=process_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        orders = queryset[start:end]

        return SuccessResponse(data=DispatchOrderSerializer(orders, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取工序派工单详情",
        description="根据工序派工单ID获取详细信息",
        responses={
            200: OpenApiResponse(response=DispatchOrderDetailResponseSerializer, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取工序派工单详情

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 工序派工单详细信息
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=DispatchOrderSerializer(order).data)

    @extend_schema(
        summary="派工（管理员）",
        description="管理员手动派工",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="派工成功"),
            400: OpenApiResponse(response=ErrorResponse, description="派工单状态不正确"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"], url_path="dispatch")
    @transaction.atomic
    def manual_dispatch(self, request: Request, pk: int) -> Response:
        """派工（管理员）

        使用 manual_dispatch 作为方法名，避免覆盖 APIView.dispatch 导致路由分发异常。
        对外 URL 仍为 POST .../dispatch/（由 url_path 指定）。

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 派工结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        if order.status != DispatchOrder.Status.PENDING:
            return ErrorResponse(msg="只能派工待抢单状态的工单", status=status.HTTP_400_BAD_REQUEST)

        operator_id = request.data.get("operator")
        device_id = request.data.get("device")

        if operator_id:
            try:
                from system.models import User
                operator = User.objects.get(id=operator_id)
                order.operator = operator
            except Exception:
                return ErrorResponse(msg="指派的员工不存在", status=status.HTTP_400_BAD_REQUEST)

        if device_id:
            try:
                from mes.models.devices import Device
                device = Device.objects.get(id=device_id)
                order.device = device
            except Exception:
                return ErrorResponse(msg="指定的设备不存在", status=status.HTTP_400_BAD_REQUEST)

        order.status = DispatchOrder.Status.DISPATCHED
        order.save()

        logger.info("工序派工单已派工: ID=%s", pk)
        return DetailResponse(data=DispatchOrderSerializer(order).data, msg="派工成功")

    @extend_schema(
        summary="抢单（员工）",
        description="员工手动抢单",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="抢单成功"),
            400: OpenApiResponse(response=ErrorResponse, description="派工单状态不正确或不可抢单"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def grab(self, request: Request, pk: int) -> Response:
        """抢单（员工）

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 抢单结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        if order.status != DispatchOrder.Status.PENDING:
            return ErrorResponse(msg="只能抢待抢单状态的工单", status=status.HTTP_400_BAD_REQUEST)

        # 检查是否可派发（前一序产出足够）
        if not order.is_reachable:
            return ErrorResponse(msg="当前工序暂不可抢单，请等待前置工序完成", status=status.HTTP_400_BAD_REQUEST)

        # 检查是否是父工单（父工单不可接取）
        if order.is_parent:
            return ErrorResponse(msg="父工单不可接取，请接取子工单", status=status.HTTP_400_BAD_REQUEST)

        order.operator = request.user
        order.status = DispatchOrder.Status.GRABBED
        order.save()

        logger.info("工序派工单已抢单: ID=%s, 员工=%s", pk, request.user.name)
        return DetailResponse(data=DispatchOrderSerializer(order).data, msg="抢单成功")

    @extend_schema(
        summary="开始生产",
        description="员工开始生产；允许状态：已派工、已抢单、已暂停（已派工为管理员派工后的 dispatched）",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="开始生产成功"),
            400: OpenApiResponse(response=ErrorResponse, description="派工单状态不正确"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def start(self, request: Request, pk: int) -> Response:
        """开始生产

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 开始生产结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        # 检查是否是当前用户的工单
        if order.operator != request.user:
            return ErrorResponse(msg="只能开始自己的工单", status=status.HTTP_403_FORBIDDEN)

        # 已派工：管理员指派接单人后状态为 dispatched，须与抢单(grabbed)、暂停(paused)一样可以开工
        if order.status not in [
            DispatchOrder.Status.DISPATCHED,
            DispatchOrder.Status.GRABBED,
            DispatchOrder.Status.PAUSED,
        ]:
            return ErrorResponse(msg="只能开始已派工、已抢单或已暂停的工单", status=status.HTTP_400_BAD_REQUEST)

        order.status = DispatchOrder.Status.IN_PROGRESS
        order.save()

        logger.info("工序派工单开始生产: ID=%s", pk)
        return DetailResponse(data=DispatchOrderSerializer(order).data, msg="开始生产成功")

    @extend_schema(
        summary="暂停生产",
        description="员工暂停生产",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="暂停生产成功"),
            400: OpenApiResponse(response=ErrorResponse, description="派工单状态不正确"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def pause(self, request: Request, pk: int) -> Response:
        """暂停生产

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 暂停生产结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        # 检查是否是当前用户的工单
        if order.operator != request.user:
            return ErrorResponse(msg="只能暂停自己的工单", status=status.HTTP_403_FORBIDDEN)

        if order.status != DispatchOrder.Status.IN_PROGRESS:
            return ErrorResponse(msg="只能暂停生产中的工单", status=status.HTTP_400_BAD_REQUEST)

        order.status = DispatchOrder.Status.PAUSED
        order.save()

        logger.info("工序派工单暂停生产: ID=%s", pk)
        return DetailResponse(data=DispatchOrderSerializer(order).data, msg="暂停生产成功")

    @extend_schema(
        summary="拆分派工单",
        description="拆分派工单为子工单",
        request=DispatchOrderSplitRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponse, description="拆分成功"),
            400: OpenApiResponse(response=ErrorResponse, description="拆分参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def split(self, request: Request, pk: int) -> Response:
        """拆分派工单

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 拆分结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        serializer = DispatchOrderSplitRequestSerializer(data=request.data, context={"dispatch_order": order})
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        split_quantity = serializer.validated_data["split_quantity"]

        try:
            child_order = order.split(split_quantity)
            return DetailResponse(data={
                "parent_order": DispatchOrderSerializer(order).data,
                "child_order": DispatchOrderSerializer(child_order).data
            }, msg="拆分成功")
        except ValueError as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("拆分派工单 %s 失败: %s", pk, str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="生产报工",
        description="生产报工",
        request=ProductionReportCreateRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponse, description="报工成功"),
            400: OpenApiResponse(response=ErrorResponse, description="报工参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="工序派工单不存在"),
        },
        tags=["工序派工单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def report(self, request: Request, pk: int) -> Response:
        """生产报工

        Args:
            request: 请求对象
            pk: 工序派工单ID

        Returns:
            Response: 报工结果
        """
        try:
            order = DispatchOrder.objects.get(id=pk)
        except DispatchOrder.DoesNotExist:
            return ErrorResponse(msg="工序派工单不存在", status=status.HTTP_404_NOT_FOUND)

        # 检查是否是当前用户的工单
        if order.operator != request.user:
            return ErrorResponse(msg="只能报工自己的工单", status=status.HTTP_403_FORBIDDEN)

        if order.status not in [DispatchOrder.Status.IN_PROGRESS, DispatchOrder.Status.GRABBED]:
            return ErrorResponse(msg="只能报工生产中或已抢单的工单", status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductionReportCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        report_quantity = serializer.validated_data["quantity"]
        work_time = serializer.validated_data["work_time"]

        try:
            report = order.report(report_quantity)
            report.work_time = work_time
            report.save()
            return DetailResponse(data=ProductionReportSerializer(report).data, msg="报工成功")
        except ValueError as e:
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("报工失败: %s", str(e))
            return ErrorResponse(msg=str(e), status=status.HTTP_400_BAD_REQUEST)


class ProductionReportViewSet(viewsets.ViewSet):
    """生产报工视图集

    处理生产报工的查询和创建操作。
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="获取生产报工列表",
        description="获取生产报工列表，支持分页和按工序派工单过滤",
        parameters=[ProductionReportListRequestSerializer],
        responses={
            200: OpenApiResponse(response=ProductionReportListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["生产报工"],
    )
    def list(self, request: Request) -> Response:
        """获取生产报工列表

        Args:
            request: 包含 page、limit 和可选 dispatch_order 过滤条件的请求

        Returns:
            Response: 分页生产报工列表
        """
        serializer = ProductionReportListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        dispatch_order_filter = serializer.validated_data.get("dispatch_order")

        queryset = ProductionReport.objects.all().order_by("-create_datetime")

        if dispatch_order_filter:
            queryset = queryset.filter(dispatch_order_id=dispatch_order_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        reports = queryset[start:end]

        return SuccessResponse(data=ProductionReportSerializer(reports, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取生产报工详情",
        description="根据生产报工ID获取详细信息",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="生产报工不存在"),
        },
        tags=["生产报工"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取生产报工详情

        Args:
            request: 请求对象
            pk: 生产报工ID

        Returns:
            Response: 生产报工详细信息
        """
        try:
            report = ProductionReport.objects.get(id=pk)
        except ProductionReport.DoesNotExist:
            return ErrorResponse(msg="生产报工不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=ProductionReportSerializer(report).data)


class QualityCheckOrderViewSet(viewsets.ViewSet):
    """质检任务单视图集

    处理质检任务单的查询和结果提交操作。
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="获取质检任务单列表",
        description="获取质检任务单列表，支持分页和按生产任务单、类型过滤",
        parameters=[QualityCheckOrderListRequestSerializer],
        responses={
            200: OpenApiResponse(response=QualityCheckOrderListResponseSerializer, description="获取成功"),
            400: OpenApiResponse(response=ErrorResponse, description="参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
        },
        tags=["质检任务单"],
    )
    def list(self, request: Request) -> Response:
        """获取质检任务单列表

        Args:
            request: 包含 page、limit 和可选过滤条件的请求

        Returns:
            Response: 分页质检任务单列表
        """
        serializer = QualityCheckOrderListRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        page = serializer.validated_data.get("page", 1)
        limit = serializer.validated_data.get("limit", 10)
        production_order_filter = serializer.validated_data.get("production_order")
        type_filter = serializer.validated_data.get("type")

        queryset = QualityCheckOrder.objects.all().order_by("-create_datetime")

        if production_order_filter:
            queryset = queryset.filter(production_order_id=production_order_filter)
        if type_filter:
            queryset = queryset.filter(type=type_filter)

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        orders = queryset[start:end]

        return SuccessResponse(data=QualityCheckOrderSerializer(orders, many=True).data, page=page, limit=limit, total=total)

    @extend_schema(
        summary="获取质检任务单详情",
        description="根据质检任务单ID获取详细信息",
        responses={
            200: OpenApiResponse(response=DetailResponse, description="获取成功"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="质检任务单不存在"),
        },
        tags=["质检任务单"],
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        """获取质检任务单详情

        Args:
            request: 请求对象
            pk: 质检任务单ID

        Returns:
            Response: 质检任务单详细信息
        """
        try:
            order = QualityCheckOrder.objects.get(id=pk)
        except QualityCheckOrder.DoesNotExist:
            return ErrorResponse(msg="质检任务单不存在", status=status.HTTP_404_NOT_FOUND)

        return DetailResponse(data=QualityCheckOrderSerializer(order).data)

    @extend_schema(
        summary="提交质检结果",
        description="提交质检结果",
        request=QualityCheckOrderSubmitResultRequestSerializer,
        responses={
            200: OpenApiResponse(response=DetailResponse, description="提交成功"),
            400: OpenApiResponse(response=ErrorResponse, description="质检结果参数错误"),
            403: OpenApiResponse(response=ErrorResponse, description="无权限"),
            404: OpenApiResponse(response=ErrorResponse, description="质检任务单不存在"),
        },
        tags=["质检任务单"],
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit_result(self, request: Request, pk: int) -> Response:
        """提交质检结果

        Args:
            request: 请求对象
            pk: 质检任务单ID

        Returns:
            Response: 提交结果
        """
        try:
            order = QualityCheckOrder.objects.get(id=pk)
        except QualityCheckOrder.DoesNotExist:
            return ErrorResponse(msg="质检任务单不存在", status=status.HTTP_404_NOT_FOUND)

        if order.status != QualityCheckOrder.Status.PENDING:
            return ErrorResponse(msg="只能提交待质检的任务单", status=status.HTTP_400_BAD_REQUEST)

        serializer = QualityCheckOrderSubmitResultRequestSerializer(data=request.data, context={"quality_check_order": order})
        if not serializer.is_valid():
            return ErrorResponse(msg=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        qualified_quantity = serializer.validated_data["qualified_quantity"]
        unqualified_quantity = serializer.validated_data["unqualified_quantity"]

        order.qualified_quantity = qualified_quantity
        order.unqualified_quantity = unqualified_quantity
        order.status = QualityCheckOrder.Status.COMPLETED
        order.save()

        logger.info("质检任务单已提交结果: ID=%s, 合格=%d, 不合格=%d", pk, qualified_quantity, unqualified_quantity)
        return DetailResponse(data=QualityCheckOrderSerializer(order).data, msg="提交成功")
