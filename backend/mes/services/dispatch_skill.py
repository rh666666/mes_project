"""派工单工序技能校验服务。"""

from __future__ import annotations

from django.db.models import Count, F, Q, QuerySet

from mes.models.orders import DispatchOrder
from mes.models.processes import ProcessSkillRequired
from mes.models.skills import Skill, UserSkill

SKILL_MISMATCH_MSG = "您不具备该工序所需技能，无法抢单"
SKILL_MISMATCH_VIEW_MSG = "您不具备该工序所需技能，无法查看该派工单"


def _get_user_skill_ids(user_id: int) -> list[int]:
    """获取用户持有的用户类技能 ID 列表。

    Args:
        user_id: 用户 ID

    Returns:
        list[int]: 技能 ID 列表
    """
    return list(
        UserSkill.objects.filter(
            user_id=user_id,
            skill__type=Skill.Type.USER,
        )
        .values_list("skill_id", flat=True)
        .distinct()
    )


def user_meets_process_skills(user_id: int, process_id: int | None) -> bool:
    """判断用户是否满足工序所需的全部技能（AND）。

    工序未配置技能时视为无门槛；process_id 为空时不可满足。

    Args:
        user_id: 用户 ID
        process_id: 工序 ID

    Returns:
        bool: 是否满足技能要求
    """
    if process_id is None:
        return False

    required = set(
        ProcessSkillRequired.objects.filter(process_id=process_id).values_list(
            "skill_id",
            flat=True,
        )
    )
    if not required:
        return True

    held = set(
        UserSkill.objects.filter(
            user_id=user_id,
            skill_id__in=required,
            skill__type=Skill.Type.USER,
        ).values_list("skill_id", flat=True)
    )
    return required <= held


def filter_queryset_by_user_skills(
    queryset: QuerySet[DispatchOrder],
    user_id: int,
) -> QuerySet[DispatchOrder]:
    """按用户技能过滤派工单 QuerySet（数据库层 annotate + filter）。

    规则：工序所需技能须为用户技能子集；工序未绑技能则全员可见；
    process 为空的派工单排除。

    Args:
        queryset: 待过滤的派工单 QuerySet
        user_id: 用户 ID

    Returns:
        QuerySet[DispatchOrder]: 过滤后的 QuerySet
    """
    user_skill_ids = _get_user_skill_ids(user_id)

    if not user_skill_ids:
        return queryset.annotate(
            required_skill_count=Count("process__required_skills", distinct=True),
        ).filter(
            process_id__isnull=False,
            required_skill_count=0,
        )

    return queryset.annotate(
        required_skill_count=Count("process__required_skills", distinct=True),
        matched_skill_count=Count(
            "process__required_skills",
            filter=Q(process__required_skills__skill_id__in=user_skill_ids),
            distinct=True,
        ),
    ).filter(
        process_id__isnull=False,
    ).filter(
        Q(required_skill_count=0) | Q(matched_skill_count=F("required_skill_count")),
    )
