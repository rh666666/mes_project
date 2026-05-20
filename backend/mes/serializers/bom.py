"""BOM 序列化器模块

该模块包含物料清单相关的序列化器类，用于处理物料清单数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.bom import BillOfMaterial, BOMDetail
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class BillOfMaterialSerializer(serializers.ModelSerializer):
    """物料清单序列化器

    用于序列化物料清单模型数据，返回物料清单的基本信息。
    """

    material_code = serializers.CharField(source="material.code", read_only=True, help_text="物料编码")
    material_name = serializers.CharField(source="material.name", read_only=True, help_text="物料名称")
    details_count = serializers.IntegerField(source="bom_details.count", read_only=True, help_text="详情数量")

    class Meta:
        model = BillOfMaterial
        fields = [
            "id",
            "material",
            "material_code",
            "material_name",
            "version",
            "is_active",
            "description",
            "details_count",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class BOMDetailSerializer(serializers.ModelSerializer):
    """物料清单详情序列化器

    用于序列化物料清单详情模型数据，返回详情的基本信息。
    """

    bom_code = serializers.CharField(source="bom.material.code", read_only=True, help_text="物料清单编码")
    material_code = serializers.CharField(source="material.code", read_only=True, help_text="物料编码")
    material_name = serializers.CharField(source="material.name", read_only=True, help_text="物料名称")
    sub_bom_version = serializers.CharField(source="sub_bom.version", read_only=True, allow_null=True, help_text="子物料 BOM 版本")

    class Meta:
        model = BOMDetail
        fields = [
            "id",
            "bom",
            "bom_code",
            "material",
            "material_code",
            "material_name",
            "sub_bom",
            "sub_bom_version",
            "quantity",
            "create_datetime",
        ]
        read_only_fields = ["id"]


class BOMDetailTreeSerializer(serializers.ModelSerializer):
    """BOM 详情树形结构序列化器

    用于展示 BOM 详情的树形结构。
    """

    material_info = serializers.SerializerMethodField(help_text="物料信息")
    children = serializers.SerializerMethodField(help_text="子BOM")

    def get_material_info(self, obj):
        """获取物料信息"""
        return {
            "id": obj.material.id if obj.material else None,
            "code": obj.material.code if obj.material else None,
            "name": obj.material.name if obj.material else None,
            "quantity": obj.quantity,
        }

    def get_children(self, obj):
        """获取子BOM"""
        if obj.sub_bom:
            details = obj.sub_bom.bom_details.all()
            return BOMDetailTreeSerializer(details, many=True).data
        return []

    class Meta:
        model = BOMDetail
        fields = ["material_info", "children"]


class BOMTreeSerializer(serializers.ModelSerializer):
    """BOM 树形结构序列化器

    用于展示 BOM 的完整树形结构。
    """

    material_info = serializers.SerializerMethodField(help_text="物料信息")
    children = serializers.SerializerMethodField(help_text="子BOM")

    def get_material_info(self, obj):
        """获取物料信息"""
        return {
            "id": obj.material.id if obj.material else None,
            "code": obj.material.code if obj.material else None,
            "name": obj.material.name if obj.material else None,
        }

    def get_children(self, obj):
        """获取子BOM"""
        details = obj.bom_details.all()
        return BOMDetailTreeSerializer(details, many=True).data

    class Meta:
        model = BillOfMaterial
        fields = ["id", "material_info", "version", "children"]


# ==================== Swagger 文档序列化器 ====================


class BillOfMaterialListRequestSerializer(serializers.Serializer):
    """物料清单列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    material = serializers.IntegerField(required=False, help_text="物料ID过滤")
    version = serializers.CharField(required=False, help_text="版本过滤")
    search = serializers.CharField(required=False, help_text="搜索物料编码、名称或版本")


@extend_schema_serializer(many=False)
class BillOfMaterialListResponseSerializer(SuccessResponseSerializer):
    """物料清单列表响应序列化器"""

    data = serializers.ListField(child=BillOfMaterialSerializer(), help_text="物料清单列表")


class BillOfMaterialDetailResponseSerializer(DetailResponseSerializer):
    """物料清单详情响应序列化器"""

    data = BillOfMaterialSerializer(help_text="物料清单详细信息")


class BillOfMaterialCreateRequestSerializer(serializers.Serializer):
    """物料清单创建请求序列化器"""

    material = serializers.IntegerField(required=True, help_text="物料ID")
    version = serializers.CharField(required=True, max_length=10, help_text="版本")
    is_active = serializers.BooleanField(required=False, default=True, help_text="是否启用")
    description = serializers.CharField(required=False, allow_blank=True, help_text="描述")


class BillOfMaterialUpdateRequestSerializer(serializers.Serializer):
    """物料清单更新请求序列化器"""

    material = serializers.IntegerField(required=False, help_text="物料ID")
    version = serializers.CharField(required=False, max_length=10, help_text="版本")
    is_active = serializers.BooleanField(required=False, help_text="是否启用")
    description = serializers.CharField(required=False, allow_blank=True, help_text="描述")


class BOMDetailListRequestSerializer(serializers.Serializer):
    """物料清单详情列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    bom = serializers.IntegerField(required=False, help_text="物料清单ID过滤")
    material = serializers.IntegerField(required=False, help_text="物料ID过滤")


@extend_schema_serializer(many=False)
class BOMDetailListResponseSerializer(SuccessResponseSerializer):
    """物料清单详情列表响应序列化器"""

    data = serializers.ListField(child=BOMDetailSerializer(), help_text="物料清单详情列表")


class BOMDetailCreateRequestSerializer(serializers.Serializer):
    """物料清单详情创建请求序列化器"""

    bom = serializers.IntegerField(required=True, help_text="物料清单ID")
    material = serializers.IntegerField(required=True, help_text="物料ID")
    sub_bom = serializers.IntegerField(required=False, allow_null=True, help_text="子物料清单ID（须为子物料名下的 BOM）")
    quantity = serializers.IntegerField(required=True, min_value=1, help_text="数量")


class BOMTreeResponseSerializer(DetailResponseSerializer):
    """BOM 树形结构响应序列化器"""

    data = BOMTreeSerializer(help_text="BOM 树形结构")
