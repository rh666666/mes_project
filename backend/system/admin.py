"""System 模块的 Django Admin 配置"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from system.models import Dept, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户模型 Admin 配置

    扩展 Django 内置 UserAdmin，添加自定义字段。
    """

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("个人信息", {"fields": ("name", "phone", "email", "avatar", "signature")}),
        ("权限", {"fields": ("is_active", "is_staff", "is_superuser", "role", "groups", "user_permissions")}),
        ("重要日期", {"fields": ("last_login", "date_joined")}),
        ("审计信息", {"fields": ("dept", "creator", "modifier", "create_datetime", "update_datetime")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "name", "password1", "password2", "role"),
            },
        ),
    )
    list_display = ("username", "name", "phone", "role", "is_staff", "is_active", "create_datetime")
    list_filter = ("is_staff", "is_superuser", "is_active", "role", "create_datetime")
    search_fields = ("username", "name", "phone", "email")
    ordering = ("-create_datetime",)
    readonly_fields = ("creator", "modifier", "create_datetime", "update_datetime")
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Dept)
class DeptAdmin(admin.ModelAdmin):
    """部门模型 Admin 配置"""

    list_display = ("code", "name", "parent", "creator", "create_datetime")
    list_filter = ("create_datetime",)
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("creator", "modifier", "create_datetime", "update_datetime")
    fieldsets = (
        (None, {"fields": ("code", "name", "parent")}),
        ("审计信息", {"fields": ("creator", "modifier", "create_datetime", "update_datetime")}),
    )
