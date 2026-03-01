from django.contrib import admin
from .models import Expense, AuditLog


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("paid_by", "flat", "amount", "date", "description")
    list_filter = ("flat", "date")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("flat", "user", "action", "entity_type", "created_at")
    list_filter = ("action",)
