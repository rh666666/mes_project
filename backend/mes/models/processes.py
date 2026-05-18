from django.db import models

from system.models import CoreModel

from .bom import BillOfMaterial
from .materials import Material
from .skills import Skill


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
        indexes = [
            models.Index(fields=["process"], name="mes_psr_process_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["process", "skill"],
                name="mes_psr_process_skill_uniq",
            ),
        ]


class ProcessRoute(CoreModel):
    """工艺路线模型"""

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="process_routes", verbose_name="物料")
    version = models.CharField(max_length=50, verbose_name="版本")
    is_active = models.BooleanField(verbose_name="是否生效", default=True)

    def __str__(self):
        return f"{self.material.code} - {self.version}"

    class Meta:
        verbose_name = "工艺路线"
        verbose_name_plural = "工艺路线"
        unique_together = ["material", "version"]

    def get_start_nodes(self):
        """获取入度为0的起始节点列表"""
        nodes = list(self.nodes.all())
        if not nodes:
            return []
        to_node_ids = set(self.edges.values_list("to_node_id", flat=True))
        return [node for node in nodes if node.id not in to_node_ids]

    def get_topological_nodes(self):
        """按有向边拓扑排序返回节点列表（含层级）"""
        nodes = list(self.nodes.all())
        if not nodes:
            return []

        node_map = {node.id: node for node in nodes}
        in_degree = {node.id: 0 for node in nodes}
        graph = {node.id: [] for node in nodes}

        for edge in self.edges.select_related("from_node", "to_node"):
            from_id = edge.from_node_id
            to_id = edge.to_node_id
            if from_id in graph and to_id in in_degree:
                graph[from_id].append(to_id)
                in_degree[to_id] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        ordered = []
        level_map = dict.fromkeys(queue, 1)

        while queue:
            current = queue.pop(0)
            ordered.append((node_map[current], level_map.get(current, 1)))
            for nxt in graph[current]:
                level_map[nxt] = max(level_map.get(nxt, 1), level_map.get(current, 1) + 1)
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        # 存在环时补齐未入序节点，避免业务崩溃
        if len(ordered) < len(nodes):
            ordered_ids = {node.id for node, _ in ordered}
            for node in nodes:
                if node.id not in ordered_ids:
                    ordered.append((node, 1))

        return ordered


class ProcessRouteNode(CoreModel):
    """工艺路线节点模型"""

    process_route = models.ForeignKey(ProcessRoute, on_delete=models.CASCADE, related_name="nodes", verbose_name="工艺路线")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="route_nodes", verbose_name="工序")
    process_bom = models.ForeignKey(
        BillOfMaterial, on_delete=models.SET_NULL, null=True, blank=True, related_name="route_nodes", verbose_name="工序物料清单"
    )
    node_key = models.CharField(max_length=64, verbose_name="节点唯一键")

    def __str__(self):
        return f"{self.process_route_id}:{self.node_key}"

    class Meta:
        verbose_name = "工艺路线节点"
        verbose_name_plural = "工艺路线节点"
        unique_together = [("process_route", "node_key")]
        ordering = ["process_route", "id"]


class ProcessRouteEdge(CoreModel):
    """工艺路线边模型"""

    process_route = models.ForeignKey(ProcessRoute, on_delete=models.CASCADE, related_name="edges", verbose_name="工艺路线")
    from_node = models.ForeignKey(
        ProcessRouteNode, on_delete=models.CASCADE, related_name="out_edges", verbose_name="起始节点"
    )
    to_node = models.ForeignKey(ProcessRouteNode, on_delete=models.CASCADE, related_name="in_edges", verbose_name="目标节点")
    priority = models.PositiveIntegerField(default=1, verbose_name="分支优先级")

    def __str__(self):
        return f"{self.process_route_id}:{self.from_node_id}->{self.to_node_id}"

    class Meta:
        verbose_name = "工艺路线边"
        verbose_name_plural = "工艺路线边"
        unique_together = [("process_route", "from_node", "to_node")]
        ordering = ["process_route", "id"]


class ProcessRouteDetail(CoreModel):
    """工艺路线详情模型"""

    process_route = models.ForeignKey(ProcessRoute, on_delete=models.CASCADE, related_name="details", verbose_name="工艺路线")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="routes", verbose_name="工序")
    sequence = models.PositiveIntegerField(verbose_name="工序顺序")
    process_bom = models.ForeignKey(BillOfMaterial, on_delete=models.SET_NULL, null=True, related_name="routes", verbose_name="工序物料清单")

    def __str__(self):
        return f"{self.process_route.code} - {self.process.code}"

    class Meta:
        verbose_name = "工艺路线详情"
        verbose_name_plural = "工艺路线详情"
        ordering = ["process_route", "sequence"]
