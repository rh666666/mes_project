"""响应序列化器基类模块

提供响应序列化器基类，用于 Swagger 文档生成。
基类仅包含 code 和 msg，data 由各业务序列化器自行定义。
"""

from rest_framework import serializers


class SuccessResponseSerializer(serializers.Serializer):
    """成功响应序列化器基类（带分页）

    继承此类后需自行定义 data 字段。
    包含 code, msg, page, limit, total 字段。
    """

    code = serializers.IntegerField(help_text="响应码，成功为 2000")
    msg = serializers.CharField(help_text="响应消息")
    page = serializers.IntegerField(help_text="当前页码")
    limit = serializers.IntegerField(help_text="每页数量")
    total = serializers.IntegerField(help_text="总数量")


class DetailResponseSerializer(serializers.Serializer):
    """详情响应序列化器基类（不带分页）

    继承此类后需自行定义 data 字段。
    包含 code, msg 字段。
    """

    code = serializers.IntegerField(help_text="响应码，成功为 2000")
    msg = serializers.CharField(help_text="响应消息")


class ErrorResponseSerializer(serializers.Serializer):
    """错误响应序列化器"""

    code = serializers.IntegerField(help_text="错误码")
    data = serializers.CharField(help_text="错误数据", allow_null=True)
    msg = serializers.CharField(help_text="错误消息")
