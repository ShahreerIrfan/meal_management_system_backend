"""
Meal serializers – cell update (PATCH), grid read, summary.
"""
from rest_framework import serializers
from .models import MealEntry, MonthlySummary


class MealCellUpdateSerializer(serializers.Serializer):
    """
    Single-cell auto-save payload.
    Frontend sends: { user_id, date, meal_count }
    """

    user_id = serializers.UUIDField()
    date = serializers.DateField()
    meal_count = serializers.DecimalField(max_digits=4, decimal_places=1, min_value=0)


class MealEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = MealEntry
        fields = ["id", "user", "user_name", "date", "meal_count", "updated_at"]
        read_only_fields = ["id", "user_name", "updated_at"]


class MonthlySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySummary
        fields = [
            "id", "flat", "year", "month", "total_meals",
            "total_expense", "meal_rate", "is_locked",
            "locked_by", "locked_at",
        ]


class MonthYearSerializer(serializers.Serializer):
    """Query params for month-based endpoints."""

    year = serializers.IntegerField(min_value=2020, max_value=2099)
    month = serializers.IntegerField(min_value=1, max_value=12)


class LockMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2020, max_value=2099)
    month = serializers.IntegerField(min_value=1, max_value=12)
