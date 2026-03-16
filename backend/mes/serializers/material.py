"""物料序列化器模块

该模块包含物料和单位相关的序列化器类，用于处理物料和单位数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.materials import Material, Unit
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class UnitSerializer(serializers.ModelSerializer):
    """单位序列化器

    用于序列化单位模型数据，返回单位的基本信息。
    """

    class Meta:
        model = Unit
        fields = [
            "id",
            "code",
            "name",
            "description",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class MaterialSerializer(serializers.ModelSerializer):
    """物料序列化器

    用于序列化物料模型数据，返回物料的基本信息，包含嵌套的单位信息。
    """

    unit = UnitSerializer(read_only=True)

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "description",
            "unit",
            "is_production",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


# ==================== Swagger 文档序列化器 ====================


class UnitListRequestSerializer(serializers.Serializer):
    """单位列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="单位名称过滤")
    code = serializers.CharField(required=False, help_text="单位编码过滤")


@extend_schema_serializer(many=False)
class UnitListResponseSerializer(SuccessResponseSerializer):
    """单位列表响应序列化器"""

    data = serializers.ListField(child=UnitSerializer(), help_text="单位列表")


class UnitDetailResponseSerializer(DetailResponseSerializer):
    """单位详情响应序列化器"""

    data = UnitSerializer(help_text="单位详细信息")


class UnitCreateRequestSerializer(serializers.Serializer):
    """单位创建请求序列化器"""

    code = serializers.CharField(required=True, help_text="单位编码")
    name = serializers.CharField(required=True, help_text="单位名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="单位描述")


class UnitUpdateRequestSerializer(serializers.Serializer):
    """单位更新请求序列化器"""

    code = serializers.CharField(required=False, help_text="单位编码")
    name = serializers.CharField(required=False, help_text="单位名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="单位描述")


class MaterialListRequestSerializer(serializers.Serializer):
    """物料列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="物料名称过滤")
    code = serializers.CharField(required=False, help_text="物料编码过滤")


@extend_schema_serializer(many=False)
class MaterialListResponseSerializer(SuccessResponseSerializer):
    """物料列表响应序列化器"""

    data = serializers.ListField(child=MaterialSerializer(), help_text="物料列表")


class MaterialDetailResponseSerializer(DetailResponseSerializer):
    """物料详情响应序列化器"""

    data = MaterialSerializer(help_text="物料详细信息")


class MaterialCreateRequestSerializer(serializers.Serializer):
    """物料创建请求序列化器"""

    code = serializers.CharField(required=True, help_text="物料编码")
    name = serializers.CharField(required=True, help_text="物料名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="物料描述")
    unit_id = serializers.IntegerField(required=False, allow_null=True, help_text="单位ID")
    is_production = serializers.BooleanField(required=False, default=False, help_text="是否为产成品")


class MaterialUpdateRequestSerializer(serializers.Serializer):
    """物料更新请求序列化器"""

    code = serializers.CharField(required=False, help_text="物料编码")
    name = serializers.CharField(required=False, help_text="物料名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="物料描述")
    unit_id = serializers.IntegerField(required=False, allow_null=True, help_text="单位ID")
    is_production = serializers.BooleanField(required=False, help_text="是否为产成品")
