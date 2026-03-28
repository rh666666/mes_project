"""BOM 模型模块

该模块包含物料清单相关的模型。
"""

from django.db import models

from system.models import CoreModel

from .materials import Material


class BillOfMaterial(CoreModel):
    """物料清单模型

    其中，一个物料清单应包含最简（最直接的）子物料结构
    例如：
    产品A需要物料A和物料B
    而物料A需要物料C和物料D
    则产品A的物料清单应包含物料A、物料B，与物料C、物料D无关

    这样就可以形成一个递归的物料清单结构，每个物料清单只包含直接的子物料，不包含间接的子物料，最终可形成一个树形结构
    """

    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="bill_of_materials", verbose_name="物料")
    version = models.CharField(max_length=10, verbose_name="版本", default="1.0")
    is_active = models.BooleanField(verbose_name="是否启用", default=True)

    def __str__(self):
        material_code = self.material.code if self.material else "Unknown"
        return f"{material_code} - {self.version}"

    class Meta:
        verbose_name = "物料清单"
        verbose_name_plural = "物料清单"


class BOMDetail(CoreModel):
    """物料清单详情模型
    
    子bom仅当该物料存在bom时存在，默认为物料的第一个bom，可手动维护
    """

    bom = models.ForeignKey(BillOfMaterial, on_delete=models.SET_NULL, null=True, related_name="bom_details", verbose_name="物料清单")
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, related_name="bom_details", verbose_name="物料")
    sub_bom = models.ForeignKey(BillOfMaterial, on_delete=models.SET_NULL, null=True, related_name="sub_bom_details", verbose_name="子物料清单")
    quantity = models.PositiveIntegerField(verbose_name="数量")

    def __str__(self):
        bom_str = str(self.bom) if self.bom else "Unknown"
        material_code = self.material.code if self.material else "Unknown"
        return f"{bom_str} - {material_code}"

    class Meta:
        verbose_name = "物料清单详情"
        verbose_name_plural = "物料清单详情"
