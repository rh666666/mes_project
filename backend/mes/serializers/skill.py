"""技能序列化器模块

该模块包含技能相关的序列化器类，用于处理技能数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from mes.models.skills import DeviceSkill, Skill, UserSkill
from utils import DetailResponseSerializer, SuccessResponseSerializer

# ==================== 业务序列化器 ====================


class SkillSerializer(serializers.ModelSerializer):
    """技能序列化器

    用于序列化技能模型数据，返回技能的基本信息。
    """

    type_display = serializers.CharField(source="get_type_display", read_only=True, help_text="技能类型显示名称")

    class Meta:
        model = Skill
        fields = [
            "id",
            "code",
            "name",
            "type",
            "type_display",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class UserSkillSerializer(serializers.ModelSerializer):
    """用户技能序列化器

    用于序列化用户技能关联数据。
    """

    skill_name = serializers.CharField(source="skill.name", read_only=True, help_text="技能名称")
    skill_code = serializers.CharField(source="skill.code", read_only=True, help_text="技能编码")
    user_name = serializers.CharField(source="user.name", read_only=True, help_text="用户名称")

    class Meta:
        model = UserSkill
        fields = [
            "id",
            "user",
            "user_name",
            "skill",
            "skill_code",
            "skill_name",
            "create_datetime",
        ]
        read_only_fields = ["id"]


class DeviceSkillSerializer(serializers.ModelSerializer):
    """设备技能序列化器

    用于序列化设备技能关联数据。
    """

    skill_name = serializers.CharField(source="skill.name", read_only=True, help_text="技能名称")
    skill_code = serializers.CharField(source="skill.code", read_only=True, help_text="技能编码")
    device_name = serializers.CharField(source="device.name", read_only=True, help_text="设备名称")

    class Meta:
        model = DeviceSkill
        fields = [
            "id",
            "device",
            "device_name",
            "skill",
            "skill_code",
            "skill_name",
            "create_datetime",
        ]
        read_only_fields = ["id"]


# ==================== Swagger 文档序列化器 ====================


class SkillListRequestSerializer(serializers.Serializer):
    """技能列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="技能名称过滤")
    code = serializers.CharField(required=False, help_text="技能编码过滤")
    type = serializers.CharField(required=False, help_text="技能类型过滤")


@extend_schema_serializer(many=False)
class SkillListResponseSerializer(SuccessResponseSerializer):
    """技能列表响应序列化器"""

    data = serializers.ListField(child=SkillSerializer(), help_text="技能列表")


class SkillDetailResponseSerializer(DetailResponseSerializer):
    """技能详情响应序列化器"""

    data = SkillSerializer(help_text="技能详细信息")


class SkillCreateRequestSerializer(serializers.Serializer):
    """技能创建请求序列化器"""

    code = serializers.CharField(required=True, max_length=100, help_text="技能编码")
    name = serializers.CharField(required=True, max_length=100, help_text="技能名称")
    type = serializers.ChoiceField(choices=Skill.Type.choices, required=False, default=Skill.Type.USER, help_text="技能类型")


class SkillUpdateRequestSerializer(serializers.Serializer):
    """技能更新请求序列化器"""

    code = serializers.CharField(required=False, max_length=100, help_text="技能编码")
    name = serializers.CharField(required=False, max_length=100, help_text="技能名称")
    type = serializers.ChoiceField(choices=Skill.Type.choices, required=False, help_text="技能类型")


class UserSkillListRequestSerializer(serializers.Serializer):
    """用户技能列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    user = serializers.IntegerField(required=False, help_text="用户ID过滤")
    skill = serializers.IntegerField(required=False, help_text="技能ID过滤")


@extend_schema_serializer(many=False)
class UserSkillListResponseSerializer(SuccessResponseSerializer):
    """用户技能列表响应序列化器"""

    data = serializers.ListField(child=UserSkillSerializer(), help_text="用户技能列表")


class UserSkillCreateRequestSerializer(serializers.Serializer):
    """用户技能创建请求序列化器"""

    user = serializers.IntegerField(required=True, help_text="用户ID")
    skill = serializers.IntegerField(required=True, help_text="技能ID")


class DeviceSkillListRequestSerializer(serializers.Serializer):
    """设备技能列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    device = serializers.IntegerField(required=False, help_text="设备ID过滤")
    skill = serializers.IntegerField(required=False, help_text="技能ID过滤")


@extend_schema_serializer(many=False)
class DeviceSkillListResponseSerializer(SuccessResponseSerializer):
    """设备技能列表响应序列化器"""

    data = serializers.ListField(child=DeviceSkillSerializer(), help_text="设备技能列表")


class DeviceSkillCreateRequestSerializer(serializers.Serializer):
    """设备技能创建请求序列化器"""

    device = serializers.IntegerField(required=True, help_text="设备ID")
    skill = serializers.IntegerField(required=True, help_text="技能ID")
