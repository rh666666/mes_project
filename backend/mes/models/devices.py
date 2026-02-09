from django.db import models

from system.models import CoreModel


class Device(CoreModel):
    """设备模型"""

    class Status(models.TextChoices):
        """设备状态"""

        IDLE = "idle", "空闲中"
        RUNNING = "running", "运行中"
        ERROR = "error", "故障"

    code = models.CharField(max_length=100, verbose_name="设备编码", unique=True)
    name = models.CharField(max_length=100, verbose_name="设备名称", db_index=True)
    status = models.CharField(max_length=10, verbose_name="设备状态", choices=Status.choices, default=Status.IDLE, db_index=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"
