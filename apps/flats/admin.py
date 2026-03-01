from django.contrib import admin
from .models import Flat, FlatMembership, InviteToken


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "created_at")
    search_fields = ("name",)


@admin.register(FlatMembership)
class FlatMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "flat", "role", "is_active")
    list_filter = ("role", "is_active")


@admin.register(InviteToken)
class InviteTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "flat", "created_by", "expires_at", "is_active", "times_used")
