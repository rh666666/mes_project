"""系统模型模块"""

import uuid
from pathlib import Path

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
    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="%(class)s_creator",
        related_query_name="%(class)s_creator_query",
        null=True,
        verbose_name="创建人",
        help_text="创建人",
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    modifier = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="%(class)s_modifier",
        related_query_name="%(class)s_modifier_query",
        null=True,
        verbose_name="修改人",
        help_text="修改人",
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    dept = models.ForeignKey(
        to="system.Dept",
        related_name="%(class)s_dept",
        related_query_name="%(class)s_dept_query",
        null=True,
        verbose_name="数据归属部门",
        help_text="数据归属部门",
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = "核心模型"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        """保存模型时自动更新 creator、modifier 和 update_datetime

        通过线程本地存储自动获取当前请求用户，无需手动传入。
        """
        from django.utils import timezone

        from utils.current_user import get_current_user

        current_user = get_current_user()

        if current_user and current_user.is_authenticated:
            if self._state.adding:
                # 创建时设置 creator
                self.creator = current_user
            else:
                # 更新时设置 modifier
                self.modifier = current_user
                self.update_datetime = timezone.now()

        super().save(*args, **kwargs)


def user_avatar_path(instance, filename):
    """生成用户头像的存储路径

    Args:
        instance: User 模型实例
        filename: 原始文件名

    Returns:
        str: 文件路径，格式为 avatars/user_{id}_{random}.{ext}
    """
    filepath = Path(filename)
    ext = filepath.suffix.lower()
    random_str = uuid.uuid4().hex[:8]
    new_filename = f"user_{instance.id}_{random_str}{ext}"
    return str(Path("avatars") / new_filename)


class User(AbstractUser, CoreModel):
    """用户模型 - 扩展Django内置用户模型"""

    class Role(models.TextChoices):
        """用户角色"""

        ADMIN = "admin", "管理员"
        USER = "user", "普通用户"

    name = models.CharField(max_length=150, verbose_name="姓名")
    phone = models.CharField(max_length=100, verbose_name="手机号", blank=True, null=True)
    role = models.CharField(max_length=100, verbose_name="角色", blank=True, null=True, choices=Role.choices, default=Role.USER)
    avatar = models.ImageField(upload_to=user_avatar_path, verbose_name="头像", blank=True, null=True)
    signature = models.TextField(verbose_name="个性签名", blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return f"{self.username} - {self.name}"

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
    parent = models.ForeignKey("self", related_name="children", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="父级部门")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
