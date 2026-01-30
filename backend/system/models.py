"""用户模型模块"""

from django.db import models


class User(models.Model):
    """用户模型"""

    username = models.CharField(max_length=100, verbose_name="用户名")
    password = models.CharField(max_length=100, verbose_name="密码")
    email = models.EmailField(max_length=100, verbose_name="邮箱")
    phone = models.CharField(max_length=100, verbose_name="手机号")
    role = models.CharField(max_length=100, verbose_name="角色")
    name = models.CharField(max_length=100, verbose_name="姓名")
    signature = models.TextField(verbose_name="个性签名", blank=True, null=True)
