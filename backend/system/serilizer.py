"""用户序列化器模块

该模块包含用户相关的序列化器类，用于处理用户数据的序列化和反序列化。
"""

from rest_framework import serializers
from .models import User as SystemUser


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器

    用于序列化用户模型数据，返回用户的基本信息。
    """
    class Meta:
        model = SystemUser
        fields = ['id', 'username', 'email', 'name', 'phone', 'role', 'signature']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器

    用于处理用户创建请求，包含密码字段并确保密码被正确哈希存储。
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


    class Meta:
        model = SystemUser
        fields = ['username', 'password', 'email', 'name', 'phone', 'role']

    def create(self, validated_data):
        """创建新用户

        Args:
            validated_data: 验证后的用户数据

        Returns:
            User: 创建的用户实例
        """
        user = SystemUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            name=validated_data.get('name', ''),
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', '')
        )
        return user
