from django.contrib import admin
from .models import MealEntry, MonthlySummary


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "flat", "date", "meal_count")
    list_filter = ("flat", "date")


@admin.register(MonthlySummary)
class MonthlySummaryAdmin(admin.ModelAdmin):
    list_display = ("flat", "year", "month", "total_meals", "total_expense", "meal_rate", "is_locked")
    list_filter = ("flat", "is_locked")
