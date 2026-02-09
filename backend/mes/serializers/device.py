"""设备序列化器模块

该模块包含设备相关的序列化器类，用于处理设备数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.devices import Device
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class DeviceSerializer(serializers.ModelSerializer):
    """设备序列化器

    用于序列化设备模型数据，返回设备的基本信息。
    """

    class Meta:
        model = Device
        fields = [
            "id",
            "code",
            "name",
            "status",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id", "status"]


class StatusField(serializers.ChoiceField):
    """状态字段序列化器

    用于序列化和反序列化设备状态字段，支持Device.Status.choices枚举。
    """

    def __init__(self, **kwargs):
        super().__init__(choices=Device.Status.choices, **kwargs)


# ==================== Swagger 文档序列化器 ====================


class DeviceListRequestSerializer(serializers.Serializer):
    """设备列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="设备名称过滤")
    status = serializers.CharField(required=False, help_text="设备状态过滤")


@extend_schema_serializer(many=False)
class DeviceListResponseSerializer(SuccessResponseSerializer):
    """设备列表响应序列化器"""

    data = serializers.ListField(child=DeviceSerializer(), help_text="设备列表")


class DeviceDetailResponseSerializer(DetailResponseSerializer):
    """设备详情响应序列化器"""

    data = DeviceSerializer(help_text="设备详细信息")


class DeviceCreateRequestSerializer(serializers.Serializer):
    """设备创建请求序列化器"""

    code = serializers.CharField(required=True, help_text="设备编码")
    name = serializers.CharField(required=True, help_text="设备名称")


class DeviceUpdateRequestSerializer(serializers.Serializer):
    """设备更新请求序列化器"""

    code = serializers.CharField(required=False, help_text="设备编码")
    name = serializers.CharField(required=False, help_text="设备名称")


