from django.contrib import admin

from mes.models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status")
    search_fields = ("code", "name")
    list_filter = ("status",)