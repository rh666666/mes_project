"""编码生成器工具模块.

提供基于日期和序列号的自动编码生成功能，支持并发安全。
"""

from datetime import datetime

from django.db import models, transaction


def generate_date_sequence_code(
    model_class: models.Model,
    prefix: str,
    date_format: str = "%Y%m%d",
    sequence_length: int = 4,
    code_field: str = "code",
) -> str:
    """生成基于日期和序列号的编码.

    编码格式：{前缀}-{日期}-{序列号}
    示例：PO-20250313-0001

    Args:
        model_class: 模型类，用于查询最大序列号
        prefix: 编码前缀（如 "PO", "DO"）
        date_format: 日期格式，默认为 "%Y%m%d"（8位日期）
        sequence_length: 序列号位数，默认为 4
        code_field: 编码字段名，默认为 "code"

    Returns:
        str: 生成的编码

    Raises:
        ValueError: 当参数无效时

    Example:
        >>> from mes.models.orders import ProductionOrder
        >>> code = generate_date_sequence_code(
        ...     model_class=ProductionOrder,
        ...     prefix="PO",
        ... )
        >>> print(code)  # PO-20250313-0001
    """
    if not prefix:
        raise ValueError("prefix cannot be empty")
    if sequence_length < 1:
        raise ValueError("sequence_length must be at least 1")

    date_str = datetime.now().strftime(date_format)
    prefix_str = f"{prefix}-{date_str}-"
    sequence_format = f"{{:0{sequence_length}d}}"

    with transaction.atomic():
        filter_kwargs = {f"{code_field}__startswith": prefix_str}
        queryset = model_class.objects.filter(**filter_kwargs).select_for_update()

        max_sequence = 0
        for code_value in queryset.values_list(code_field, flat=True):
            if not code_value or len(code_value) < sequence_length:
                continue
            try:
                max_sequence = max(max_sequence, int(code_value[-sequence_length:]))
            except (ValueError, TypeError):
                continue

        sequence = max_sequence + 1
        return f"{prefix_str}{sequence_format.format(sequence)}"
