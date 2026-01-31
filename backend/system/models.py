"""用户模型模块"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """用户模型 - 扩展Django内置用户模型"""

    name = models.CharField(max_length=150, verbose_name="姓名")
    phone = models.CharField(max_length=100, verbose_name="手机号", blank=True, null=True)
    role = models.CharField(max_length=100, verbose_name="角色", blank=True, null=True)
    signature = models.TextField(verbose_name="个性签名", blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def save(self, *args, **kwargs):
        if self.name and not self.first_name:
            parts = self.name.split(' ', 1)
            self.first_name = parts[0]
            if len(parts) > 1:
                self.last_name = parts[1]
        super().save(*args, **kwargs)
