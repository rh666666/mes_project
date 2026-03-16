from django.db import models

from mes.models.materials import Material
from mes.models.skills import Skill
from system.models import CoreModel


class Process(CoreModel):
    """工序模型"""

    code = models.CharField(max_length=100, unique=True, verbose_name="工序编码")
    name = models.CharField(max_length=100, verbose_name="工序名称")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "工序"
        verbose_name_plural = "工序"


class ProcessSkillRequired(CoreModel):
    """工序技能需求模型"""

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="required_skills", verbose_name="工序")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="required_by_processes", verbose_name="技能")

    def __str__(self):
        return f"{self.process.code} - {self.skill.code}"

    class Meta:
        verbose_name = "工序技能需求"
        verbose_name_plural = "工序技能需求"


class ProcessRoute(CoreModel):
    """工艺路线模型"""

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="process_routes", verbose_name="物料")
    version = models.CharField(max_length=50, verbose_name="版本")

    def __str__(self):
        return f"{self.material.code} - {self.version}"

    class Meta:
        verbose_name = "工艺路线"
        verbose_name_plural = "工艺路线"
        unique_together = ["material", "version"]


class ProcessRouteDetail(CoreModel):
    """工艺路线详情模型"""

    process_route = models.ForeignKey(ProcessRoute, on_delete=models.CASCADE, related_name="details", verbose_name="工艺路线")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="routes", verbose_name="工序")
    sequence = models.PositiveIntegerField(verbose_name="工序顺序")

    def __str__(self):
        return f"{self.process_route.code} - {self.process.code}"

    class Meta:
        verbose_name = "工艺路线详情"
        verbose_name_plural = "工艺路线详情"
        ordering = ["process_route", "sequence"]
