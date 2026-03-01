"""
Expense serializers.
"""
from rest_framework import serializers
from .models import Expense, AuditLog


class ExpenseSerializer(serializers.ModelSerializer):
    paid_by_name = serializers.CharField(source="paid_by.full_name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "flat", "paid_by", "paid_by_name",
            "amount", "description", "date", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "flat", "paid_by_name", "created_at", "updated_at"]


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["paid_by", "amount", "description", "date"]


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "user", "user_name", "action", "entity_type", "entity_id", "details", "created_at"]
