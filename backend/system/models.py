"""用户模型模块"""

import os
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CoreModel(models.Model):
    """核心标准抽象模型，包含审计字段

    可直接继承使用，增加审计字段。
    覆盖字段时，字段名称请勿修改，必须统一审计字段名称。
    """

    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name="creator_query", null=True, verbose_name="创建人", help_text="创建人", on_delete=models.SET_NULL, db_constraint=False)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    dept_belong_id = models.CharField(max_length=255, help_text="数据归属部门", null=True, blank=True, verbose_name="数据归属部门")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = "核心模型"
        verbose_name_plural = verbose_name


def user_avatar_path(instance, filename):
    """生成用户头像的存储路径

    Args:
        instance: User 模型实例
        filename: 原始文件名

    Returns:
        str: 文件路径，格式为 avatars/user_{id}_{random}.{ext}
    """
    ext = os.path.splitext(filename)[1].lower()
    random_str = uuid.uuid4().hex[:8]
    new_filename = f"user_{instance.id}_{random_str}{ext}"
    return os.path.join("avatars", new_filename)


class User(AbstractUser, CoreModel):
    """用户模型 - 扩展Django内置用户模型"""

    name = models.CharField(max_length=150, verbose_name="姓名")
    phone = models.CharField(max_length=100, verbose_name="手机号", blank=True, null=True)
    role = models.CharField(max_length=100, verbose_name="角色", blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_path, verbose_name="头像", blank=True, null=True)
    signature = models.TextField(verbose_name="个性签名", blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def save(self, *args, **kwargs):
        if self.name and not self.first_name:
            parts = self.name.split(" ", 1)
            self.first_name = parts[0]
            if len(parts) > 1:
                self.last_name = parts[1]
        super().save(*args, **kwargs)


class Dept(CoreModel):
    """部门模型"""

    code = models.CharField(max_length=100, verbose_name="部门编码", unique=True)
    name = models.CharField(max_length=100, verbose_name="部门名称")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="父级部门")

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
