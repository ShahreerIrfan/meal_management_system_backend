from django.contrib import admin
from .models import AppPermission, MemberPermission


@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ("codename", "label", "module")
    list_filter = ("module",)


@admin.register(MemberPermission)
class MemberPermissionAdmin(admin.ModelAdmin):
    list_display = ("membership", "permission", "granted_by", "created_at")
