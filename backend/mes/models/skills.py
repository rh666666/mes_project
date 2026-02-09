from django.db import models

from system.models import CoreModel


class Skill(CoreModel):
    """技能模型"""

    class Type(models.TextChoices):
        """技能类型"""

        USER = "user", "用户技能"
        DEVICE = "device", "设备技能"

    code = models.CharField(max_length=100, verbose_name="技能编码", unique=True)
    name = models.CharField(max_length=100, verbose_name="技能名称")
    type = models.CharField(max_length=10, verbose_name="技能类型", choices=Type.choices, default=Type.USER, db_index=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "技能"
        verbose_name_plural = "技能"


class UserSkill(CoreModel):
    """用户技能模型"""

    user = models.ForeignKey("system.User", on_delete=models.CASCADE, verbose_name="用户")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name="技能")

    def __str__(self):
        return f"{self.user.name} - {self.skill.name}"

    class Meta:
        verbose_name = "用户技能"
        verbose_name_plural = "用户技能"


class DeviceSkill(CoreModel):
    """设备技能模型"""

    device = models.ForeignKey("Device", on_delete=models.CASCADE, verbose_name="设备")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name="技能")

    def __str__(self):
        return f"{self.device.name} - {self.skill.name}"

    class Meta:
        verbose_name = "设备技能"
        verbose_name_plural = "设备技能"
