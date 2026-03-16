"""工序序列化器模块

该模块包含工序相关的序列化器类，用于处理工序数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.processes import Process, ProcessRoute, ProcessRouteDetail, ProcessSkillRequired
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class ProcessSerializer(serializers.ModelSerializer):
    """工序序列化器

    用于序列化工序模型数据，返回工序的基本信息。
    """

    class Meta:
        model = Process
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


class ProcessSkillRequiredSerializer(serializers.ModelSerializer):
    """工序技能需求序列化器

    用于序列化工序技能需求关联数据。
    """

    process_name = serializers.CharField(source="process.name", read_only=True, help_text="工序名称")
    process_code = serializers.CharField(source="process.code", read_only=True, help_text="工序编码")
    skill_name = serializers.CharField(source="skill.name", read_only=True, help_text="技能名称")
    skill_code = serializers.CharField(source="skill.code", read_only=True, help_text="技能编码")

    class Meta:
        model = ProcessSkillRequired
        fields = [
            "id",
            "process",
            "process_code",
            "process_name",
            "skill",
            "skill_code",
            "skill_name",
            "create_datetime",
        ]
        read_only_fields = ["id"]


class ProcessRouteSerializer(serializers.ModelSerializer):
    """工艺路线序列化器

    用于序列化工艺路线模型数据，返回工艺路线的基本信息。
    """

    material_code = serializers.CharField(source="material.code", read_only=True, help_text="物料编码")
    material_name = serializers.CharField(source="material.name", read_only=True, help_text="物料名称")

    class Meta:
        model = ProcessRoute
        fields = [
            "id",
            "material",
            "material_code",
            "material_name",
            "version",
            "description",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class ProcessRouteDetailSerializer(serializers.ModelSerializer):
    """工艺路线详情序列化器

    用于序列化工艺路线详情关联数据。
    """

    material_name = serializers.CharField(source="process_route.material.name", read_only=True, help_text="物料名称")
    process_route_version = serializers.CharField(source="process_route.version", read_only=True, help_text="工艺路线版本")
    process_name = serializers.CharField(source="process.name", read_only=True, help_text="工序名称")
    process_code = serializers.CharField(source="process.code", read_only=True, help_text="工序编码")

    class Meta:
        model = ProcessRouteDetail
        fields = [
            "id",
            "process_route",
            "material_name",
            "process_route_version",
            "process",
            "process_code",
            "process_name",
            "sequence",
            "create_datetime",
        ]
        read_only_fields = ["id"]


# ==================== Swagger 文档序列化器 ====================


class ProcessListRequestSerializer(serializers.Serializer):
    """工序列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="工序名称过滤")
    code = serializers.CharField(required=False, help_text="工序编码过滤")


@extend_schema_serializer(many=False)
class ProcessListResponseSerializer(SuccessResponseSerializer):
    """工序列表响应序列化器"""

    data = serializers.ListField(child=ProcessSerializer(), help_text="工序列表")


class ProcessDetailResponseSerializer(DetailResponseSerializer):
    """工序详情响应序列化器"""

    data = ProcessSerializer(help_text="工序详细信息")


class ProcessCreateRequestSerializer(serializers.Serializer):
    """工序创建请求序列化器"""

    code = serializers.CharField(required=True, max_length=100, help_text="工序编码")
    name = serializers.CharField(required=True, max_length=100, help_text="工序名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="工序描述")


class ProcessUpdateRequestSerializer(serializers.Serializer):
    """工序更新请求序列化器"""

    code = serializers.CharField(required=False, max_length=100, help_text="工序编码")
    name = serializers.CharField(required=False, max_length=100, help_text="工序名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="工序描述")


class ProcessSkillRequiredListRequestSerializer(serializers.Serializer):
    """工序技能需求列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    process = serializers.IntegerField(required=False, help_text="工序ID过滤")
    skill = serializers.IntegerField(required=False, help_text="技能ID过滤")


@extend_schema_serializer(many=False)
class ProcessSkillRequiredListResponseSerializer(SuccessResponseSerializer):
    """工序技能需求列表响应序列化器"""

    data = serializers.ListField(child=ProcessSkillRequiredSerializer(), help_text="工序技能需求列表")


class ProcessSkillRequiredCreateRequestSerializer(serializers.Serializer):
    """工序技能需求创建请求序列化器"""

    process = serializers.IntegerField(required=True, help_text="工序ID")
    skill = serializers.IntegerField(required=True, help_text="技能ID")


class ProcessRouteListRequestSerializer(serializers.Serializer):
    """工艺路线列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    material = serializers.IntegerField(required=False, help_text="物料ID过滤")


@extend_schema_serializer(many=False)
class ProcessRouteListResponseSerializer(SuccessResponseSerializer):
    """工艺路线列表响应序列化器"""

    data = serializers.ListField(child=ProcessRouteSerializer(), help_text="工艺路线列表")


class ProcessRouteDetailResponseSerializer(DetailResponseSerializer):
    """工艺路线详情响应序列化器"""

    data = ProcessRouteSerializer(help_text="工艺路线详细信息")


class ProcessRouteCreateRequestSerializer(serializers.Serializer):
    """工艺路线创建请求序列化器"""

    material = serializers.IntegerField(required=True, help_text="物料ID")
    version = serializers.CharField(required=True, max_length=50, help_text="版本")
    description = serializers.CharField(required=False, allow_blank=True, help_text="工艺路线描述")


class ProcessRouteUpdateRequestSerializer(serializers.Serializer):
    """工艺路线更新请求序列化器"""

    version = serializers.CharField(required=False, max_length=50, help_text="版本")
    description = serializers.CharField(required=False, allow_blank=True, help_text="工艺路线描述")


class ProcessRouteDetailListRequestSerializer(serializers.Serializer):
    """工艺路线详情列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    process_route = serializers.IntegerField(required=False, help_text="工艺路线ID过滤")
    process = serializers.IntegerField(required=False, help_text="工序ID过滤")


@extend_schema_serializer(many=False)
class ProcessRouteDetailListResponseSerializer(SuccessResponseSerializer):
    """工艺路线详情列表响应序列化器"""

    data = serializers.ListField(child=ProcessRouteDetailSerializer(), help_text="工艺路线详情列表")


class ProcessRouteDetailCreateRequestSerializer(serializers.Serializer):
    """工艺路线详情创建请求序列化器"""

    process_route = serializers.IntegerField(required=True, help_text="工艺路线ID")
    process = serializers.IntegerField(required=True, help_text="工序ID")
    sequence = serializers.IntegerField(required=True, min_value=1, help_text="工序顺序")
