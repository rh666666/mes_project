"""工单 序列化器模块

该模块包含工单相关的序列化器类，用于处理工单数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.orders import DispatchOrder, ProductionOrder, ProductionReport, QualityCheckOrder
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class ProductionOrderSerializer(serializers.ModelSerializer):
    """生产任务单序列化器

    用于序列化生产任务单模型数据，返回生产任务单的基本信息。
    """

    product_code = serializers.CharField(source="product.code", read_only=True, help_text="产品编码")
    product_name = serializers.CharField(source="product.name", read_only=True, help_text="产品名称")
    status_display = serializers.CharField(source="get_status_display", read_only=True, help_text="状态显示")
    material_requirements = serializers.SerializerMethodField(help_text="原材料需求")
    dispatch_order_count = serializers.IntegerField(source="dispatch_orders.count", read_only=True, help_text="派工单数量")
    completed_dispatch_count = serializers.SerializerMethodField(help_text="已完成派工单数量")

    def get_material_requirements(self, obj):
        """获取原材料需求"""
        requirements = obj.calculate_material_requirements()
        return {
            str(m_id): {
                "material_code": info["material"].code,
                "material_name": info["material"].name,
                "quantity": info["quantity"]
            }
            for m_id, info in requirements.items()
        }

    def get_completed_dispatch_count(self, obj):
        """获取已完成派工单数量"""
        return obj.dispatch_orders.filter(status=DispatchOrder.Status.COMPLETED).count()

    class Meta:
        model = ProductionOrder
        fields = [
            "id",
            "code",
            "product",
            "product_code",
            "product_name",
            "quantity",
            "status",
            "status_display",
            "process_route",
            "material_requirements",
            "dispatch_order_count",
            "completed_dispatch_count",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class DispatchOrderSerializer(serializers.ModelSerializer):
    """工序派工单序列化器

    用于序列化工序派工单模型数据，返回工序派工单的基本信息。
    """

    production_order_code = serializers.CharField(source="production_order.code", read_only=True, help_text="生产任务单编码")
    process_code = serializers.CharField(source="process.code", read_only=True, help_text="工序编码")
    process_name = serializers.CharField(source="process.name", read_only=True, help_text="工序名称")
    operator_name = serializers.CharField(source="operator.name", read_only=True, help_text="接单人姓名")
    device_code = serializers.CharField(source="device.code", read_only=True, help_text="设备编码")
    status_display = serializers.CharField(source="get_status_display", read_only=True, help_text="状态显示")
    is_reachable = serializers.BooleanField(read_only=True, help_text="是否可派发")
    parent_code = serializers.CharField(source="parent.code", read_only=True, help_text="父工单编码")
    children_count = serializers.IntegerField(source="children.count", read_only=True, help_text="子工单数量")

    class Meta:
        model = DispatchOrder
        fields = [
            "id",
            "code",
            "production_order",
            "production_order_code",
            "process",
            "process_code",
            "process_name",
            "sequence",
            "operator",
            "operator_name",
            "device",
            "device_code",
            "quantity",
            "completed_quantity",
            "status",
            "status_display",
            "is_reachable",
            "parent",
            "parent_code",
            "is_parent",
            "is_child",
            "children_count",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = ["id"]


class ProductionReportSerializer(serializers.ModelSerializer):
    """生产报工序列化器

    用于序列化生产报工模型数据，返回生产报工的基本信息。
    """

    dispatch_order_code = serializers.CharField(source="dispatch_order.code", read_only=True, help_text="工序派工单编码")
    process_name = serializers.CharField(source="dispatch_order.process.name", read_only=True, help_text="工序名称")

    class Meta:
        model = ProductionReport
        fields = [
            "id",
            "code",
            "dispatch_order",
            "dispatch_order_code",
            "process_name",
            "quantity",
            "work_time",
            "report_date",
            "create_datetime",
        ]
        read_only_fields = ["id"]


class QualityCheckOrderSerializer(serializers.ModelSerializer):
    """质检任务单序列化器

    用于序列化质检任务单模型数据，返回质检任务单的基本信息。
    """

    production_order_code = serializers.CharField(source="production_order.code", read_only=True, help_text="生产任务单编码")
    product_code = serializers.CharField(source="product.code", read_only=True, help_text="产品编码")
    product_name = serializers.CharField(source="product.name", read_only=True, help_text="产品名称")
    type_display = serializers.CharField(source="get_type_display", read_only=True, help_text="类型显示")
    status_display = serializers.CharField(source="get_status_display", read_only=True, help_text="状态显示")

    class Meta:
        model = QualityCheckOrder
        fields = [
            "id",
            "code",
            "type",
            "type_display",
            "status",
            "status_display",
            "production_order",
            "production_order_code",
            "product",
            "product_code",
            "product_name",
            "quantity",
            "qualified_quantity",
            "unqualified_quantity",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = ["id"]


# ==================== Swagger 文档序列化器 ====================


class ProductionOrderListRequestSerializer(serializers.Serializer):
    """生产任务单列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    product = serializers.IntegerField(required=False, help_text="产品ID过滤")
    status = serializers.CharField(required=False, help_text="状态过滤")


@extend_schema_serializer(many=False)
class ProductionOrderListResponseSerializer(SuccessResponseSerializer):
    """生产任务单列表响应序列化器"""

    data = serializers.ListField(child=ProductionOrderSerializer(), help_text="生产任务单列表")


class ProductionOrderDetailResponseSerializer(DetailResponseSerializer):
    """生产任务单详情响应序列化器"""

    data = ProductionOrderSerializer(help_text="生产任务单详细信息")


class ProductionOrderCreateRequestSerializer(serializers.Serializer):
    """生产任务单创建请求序列化器"""

    product = serializers.IntegerField(required=True, help_text="产品ID")
    quantity = serializers.IntegerField(required=True, min_value=1, help_text="生产数量")
    process_route = serializers.IntegerField(required=True, help_text="工艺路线ID")
    description = serializers.CharField(required=False, allow_blank=True, help_text="描述")


class ProductionOrderUpdateRequestSerializer(serializers.Serializer):
    """生产任务单更新请求序列化器"""

    product = serializers.IntegerField(required=False, help_text="产品ID")
    quantity = serializers.IntegerField(required=False, min_value=1, help_text="生产数量")
    process_route = serializers.IntegerField(required=False, help_text="工艺路线ID")
    description = serializers.CharField(required=False, allow_blank=True, help_text="描述")


class DispatchOrderListRequestSerializer(serializers.Serializer):
    """工序派工单列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    production_order = serializers.IntegerField(required=False, help_text="生产任务单ID过滤")
    process = serializers.IntegerField(required=False, help_text="工序ID过滤")
    status = serializers.CharField(required=False, help_text="状态过滤")
    mine = serializers.BooleanField(
        required=False,
        default=False,
        help_text="为 true 时仅返回当前用户接单的工单（管理员亦生效，用于「我的工单」）",
    )


@extend_schema_serializer(many=False)
class DispatchOrderListResponseSerializer(SuccessResponseSerializer):
    """工序派工单列表响应序列化器"""

    data = serializers.ListField(child=DispatchOrderSerializer(), help_text="工序派工单列表")


class DispatchOrderDetailResponseSerializer(DetailResponseSerializer):
    """工序派工单详情响应序列化器"""

    data = DispatchOrderSerializer(help_text="工序派工单详细信息")


class DispatchOrderGrabRequestSerializer(serializers.Serializer):
    """员工抢单请求序列化器"""

    quantity = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="抢单数量；不传则按剩余可生产数量全部抢单",
    )

    def validate(self, attrs: dict) -> dict:
        """校验抢单数量不超过剩余可生产数量。

        Args:
            attrs: 请求字段

        Returns:
            dict: 含解析后的 quantity、remaining
        """
        dispatch_order = self.context.get("dispatch_order")
        if not dispatch_order:
            return attrs

        remaining = dispatch_order.quantity - dispatch_order.completed_quantity
        if remaining < 1:
            raise serializers.ValidationError("该工单无可抢数量")

        quantity = attrs.get("quantity") or remaining
        if quantity > remaining:
            raise serializers.ValidationError({"quantity": "抢单数量不能超过剩余生产数量"})
        if quantity < remaining:
            if remaining == 1:
                raise serializers.ValidationError({"quantity": "剩余数量为1，须全部抢单"})
            if dispatch_order.quantity == 1:
                raise serializers.ValidationError({"quantity": "生产数量为1时不可部分抢单"})

        attrs["quantity"] = quantity
        attrs["remaining"] = remaining
        return attrs


class DispatchOrderSplitRequestSerializer(serializers.Serializer):
    """派工单拆分请求序列化器"""

    split_quantity = serializers.IntegerField(min_value=1, help_text="拆分出的子工单数量")

    def validate_split_quantity(self, value):
        """验证拆分数量"""
        dispatch_order = self.context.get('dispatch_order')
        if dispatch_order:
            if dispatch_order.quantity == 1:
                raise serializers.ValidationError("生产数量为1时不可拆分")
            if value >= dispatch_order.quantity:
                raise serializers.ValidationError("拆分数量必须小于原工单数量")
            remaining = dispatch_order.quantity - dispatch_order.completed_quantity
            if value > remaining:
                raise serializers.ValidationError("拆分数量不能超过剩余未生产数量")
        return value


class ProductionReportListRequestSerializer(serializers.Serializer):
    """生产报工列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    dispatch_order = serializers.IntegerField(required=False, help_text="工序派工单ID过滤")


@extend_schema_serializer(many=False)
class ProductionReportListResponseSerializer(SuccessResponseSerializer):
    """生产报工列表响应序列化器"""

    data = serializers.ListField(child=ProductionReportSerializer(), help_text="生产报工列表")


class ProductionReportCreateRequestSerializer(serializers.Serializer):
    """生产报工创建请求序列化器"""

    dispatch_order_id = serializers.IntegerField(required=True, help_text="工序派工单ID")
    quantity = serializers.IntegerField(min_value=1, required=True, help_text="报工数量（允许累计超过计划数量）")
    work_time = serializers.DurationField(required=True, help_text="工作时间")


class QualityCheckOrderListRequestSerializer(serializers.Serializer):
    """质检任务单列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    production_order = serializers.IntegerField(required=False, help_text="生产任务单ID过滤")
    type = serializers.CharField(required=False, help_text="类型过滤")


@extend_schema_serializer(many=False)
class QualityCheckOrderListResponseSerializer(SuccessResponseSerializer):
    """质检任务单列表响应序列化器"""

    data = serializers.ListField(child=QualityCheckOrderSerializer(), help_text="质检任务单列表")


class QualityCheckOrderSubmitResultRequestSerializer(serializers.Serializer):
    """质检结果提交请求序列化器"""

    qualified_quantity = serializers.IntegerField(required=True, min_value=0, help_text="合格品数量")
    unqualified_quantity = serializers.IntegerField(required=True, min_value=0, help_text="不合格品数量")

    def validate(self, data):
        """验证质检数量"""
        qualified = data.get('qualified_quantity', 0)
        unqualified = data.get('unqualified_quantity', 0)
        quality_check_order = self.context.get('quality_check_order')
        
        if quality_check_order:
            total = qualified + unqualified
            if total != quality_check_order.quantity:
                raise serializers.ValidationError("合格品数量与不合格品数量之和必须等于质检数量")
        
        return data
