"""用户序列化器模块

该模块包含用户相关的序列化器类，用于处理用户数据的序列化和反序列化，
以及用于 Swagger 文档生成的请求/响应序列化器。
"""

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from utils import (
    DetailResponseSerializer,
    SuccessResponseSerializer,
)

from .models import Dept
from .models import User as SystemUser

# ==================== 业务序列化器 ====================


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器

    用于序列化用户模型数据，返回用户的基本信息。
    注意：明确指定字段以避免暴露敏感信息（如 password, is_superuser 等）。
    """

    class Meta:
        model = SystemUser
        fields = [
            "id",
            "username",
            "name",
            "email",
            "phone",
            "role",
            "avatar",
            "signature",
            "dept",
            "description",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
        ]
        read_only_fields = ["id"]


class RoleField(serializers.ChoiceField):
    """角色字段序列化器

    用于序列化和反序列化用户角色字段，支持Role.choices枚举。
    """

    def __init__(self, **kwargs):
        super().__init__(choices=SystemUser.Role.choices, **kwargs)


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器

    用于处理用户创建请求，包含密码字段并确保密码被正确哈希存储。
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = RoleField(required=False)

    class Meta:
        model = SystemUser
        fields = ["username", "password", "email", "name", "phone", "role", "avatar"]

    def create(self, validated_data):
        """创建新用户

        Args:
            validated_data: 验证后的用户数据

        Returns:
            User: 创建的用户实例
        """
        user = SystemUser.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            name=validated_data.get("name", ""),
            phone=validated_data.get("phone", ""),
            role=validated_data.get("role", ""),
            avatar=validated_data.get("avatar", None),
        )
        return user
    

class DeptSerializer(serializers.ModelSerializer):
    """部门序列化器"""

    class Meta:
        model = Dept
        fields = "__all__"
        read_only_fields = ["id"]
        
        
class DeptCreateSerializer(serializers.ModelSerializer):
    """部门创建序列化器"""

    class Meta:
        model = Dept
        fields = ["code", "name", "parent"]
        
    def create(self, validated_data):
        """创建新部门

        Args:
            validated_data: 验证后的部门数据

        Returns:
            Dept: 创建的部门实例
        """
        dept = Dept.objects.create(
            code=validated_data["code"],
            name=validated_data["name"],
            parent=validated_data.get("parent", None),
        )
        return dept


# ==================== Swagger 文档序列化器 ====================


class LoginRequestSerializer(serializers.Serializer):
    """登录请求序列化器"""

    username = serializers.CharField(required=True, help_text="用户名")
    password = serializers.CharField(required=True, help_text="密码", write_only=True)


class LoginResponseDataSerializer(serializers.Serializer):
    """登录响应数据序列化器"""

    access = serializers.CharField(help_text="访问令牌")
    refresh = serializers.CharField(help_text="刷新令牌")
    csrf_token = serializers.CharField(help_text="CSRF 令牌", allow_null=True)


class LoginResponseSerializer(DetailResponseSerializer):
    """登录响应序列化器"""

    data = LoginResponseDataSerializer(help_text="响应数据")


class RegisterRequestSerializer(serializers.Serializer):
    """注册请求序列化器"""

    username = serializers.CharField(required=True, help_text="用户名")
    password = serializers.CharField(required=True, help_text="密码", write_only=True)
    email = serializers.EmailField(required=False, help_text="邮箱", allow_blank=True)
    name = serializers.CharField(required=False, help_text="昵称", allow_blank=True)


class RegisterResponseSerializer(DetailResponseSerializer):
    """注册响应序列化器"""

    data = serializers.DictField(child=UserSerializer(), help_text="包含用户信息的响应数据")


class LogoutRequestSerializer(serializers.Serializer):
    """注销请求序列化器"""

    refresh = serializers.CharField(required=False, help_text="刷新令牌，用于加入黑名单")


class LogoutResponseSerializer(DetailResponseSerializer):
    """注销响应序列化器"""

    data = serializers.CharField(help_text="响应数据", allow_null=True)


class UserProfileResponseSerializer(DetailResponseSerializer):
    """用户资料响应序列化器"""

    data = UserSerializer(help_text="用户详细信息")


class UserProfileUpdateRequestSerializer(serializers.Serializer):
    """用户资料更新请求序列化器"""

    name = serializers.CharField(required=True, help_text="昵称")
    email = serializers.EmailField(required=True, help_text="邮箱")
    phone = serializers.CharField(required=True, help_text="手机号")
    signature = serializers.CharField(required=False, help_text="个性签名", allow_blank=True)
    role = RoleField(required=False, help_text="角色", allow_null=True)
    dept = serializers.IntegerField(required=False, help_text="数据归属部门 ID", allow_null=True)


class UserProfileUpdateResponseSerializer(DetailResponseSerializer):
    """用户资料更新响应序列化器"""

    data = UserSerializer(help_text="更新后的用户详细信息")


class AvatarUploadRequestSerializer(serializers.Serializer):
    """头像上传请求序列化器"""

    avatar = serializers.ImageField(
        required=True,
        help_text="头像图片文件，支持 jpg、jpeg、png、gif、webp 格式，最大 5MB",
    )

    def validate_avatar(self, value):
        """验证头像文件"""
        # 文件大小限制 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("头像文件大小不能超过 5MB")

        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("头像文件格式不支持，请上传 jpg、png、gif 或 webp 格式的图片")

        return value


class UserAdminUpdateRequestSerializer(serializers.Serializer):
    """管理员用户更新请求序列化器"""

    role = RoleField(required=False, help_text="角色")
    dept = serializers.IntegerField(required=False, help_text="数据归属部门 ID")


class UserListRequestSerializer(serializers.Serializer):
    """用户列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    username = serializers.CharField(required=False, help_text="用户名过滤")
    role = serializers.CharField(required=False, help_text="角色过滤")
    dept = serializers.IntegerField(required=False, help_text="部门ID过滤")


@extend_schema_serializer(many=False)
class UserListResponseSerializer(SuccessResponseSerializer):
    """用户列表响应序列化器"""

    data = serializers.ListField(child=UserSerializer(), help_text="用户列表")


class AvatarUploadResponseSerializer(DetailResponseSerializer):
    """头像上传响应序列化器"""

    data = UserSerializer(help_text="更新后的用户详细信息")


class DeptListRequestSerializer(serializers.Serializer):
    """部门列表请求序列化器"""

    page = serializers.IntegerField(required=False, default=1, min_value=1, help_text="页码")
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100, help_text="每页数量")
    name = serializers.CharField(required=False, help_text="部门名称过滤")


@extend_schema_serializer(many=False)
class DeptListResponseSerializer(SuccessResponseSerializer):
    """部门列表响应序列化器"""

    data = serializers.ListField(child=DeptSerializer(), help_text="部门列表")


class DeptDetailResponseSerializer(DetailResponseSerializer):
    """部门详情响应序列化器"""

    data = DeptSerializer(help_text="部门详细信息")


class DeptCreateRequestSerializer(serializers.Serializer):
    """部门创建请求序列化器"""

    code = serializers.CharField(required=True, help_text="部门编码")
    name = serializers.CharField(required=True, help_text="部门名称")
    parent = serializers.IntegerField(required=False, allow_null=True, help_text="父级部门ID")


class DeptUpdateRequestSerializer(serializers.Serializer):
    """部门更新请求序列化器"""

    code = serializers.CharField(required=False, help_text="部门编码")
    name = serializers.CharField(required=False, help_text="部门名称")
    parent = serializers.IntegerField(required=False, allow_null=True, help_text="父级部门ID")
