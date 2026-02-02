"""当前用户线程本地存储模块

用于在中间件和模型之间传递当前请求用户，实现审计字段自动填充。
"""

import threading

_local = threading.local()


def get_current_user():
    """获取当前线程中的当前用户

    Returns:
        User|None: 当前认证用户，未登录或无请求上下文时返回 None
    """
    return getattr(_local, "user", None)


def set_current_user(user):
    """设置当前线程的当前用户

    Args:
        user: 当前请求用户
    """
    _local.user = user


def clear_current_user():
    """清除当前线程的用户信息"""
    _local.user = None
