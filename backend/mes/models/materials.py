from django.db import models

from system.models import CoreModel


class Unit(CoreModel):
    """单位模型"""

    code = models.CharField(max_length=100, unique=True, verbose_name="单位编码")
    name = models.CharField(max_length=100, verbose_name="单位名称")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "单位"
        verbose_name_plural = "单位"


class Material(CoreModel):
    """物料模型"""

    code = models.CharField(max_length=100, unique=True, verbose_name="物料编码")
    name = models.CharField(max_length=100, verbose_name="物料名称")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, related_name="materials", verbose_name="单位")
    is_production = models.BooleanField(default=False, verbose_name="是否为产成品")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "物料"
        verbose_name_plural = "物料"
