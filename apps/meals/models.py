"""
Meal models – MealEntry and MonthlySummary with month-lock support.
"""
from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class MealEntry(TimeStampedModel):
    """
    One row = one user's meal count for one date in one flat.
    The cell in the Excel-like grid.
    """

    flat = models.ForeignKey(
        "flats.Flat", on_delete=models.CASCADE, related_name="meal_entries"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meal_entries",
    )
    date = models.DateField(db_index=True)
    meal_count = models.DecimalField(
        max_digits=4, decimal_places=1, default=0,
        help_text="Supports half meals: 0, 0.5, 1, 1.5, 2, 3…",
    )

    class Meta:
        db_table = "meal_entries"
        unique_together = ("flat", "user", "date")
        indexes = [
            models.Index(fields=["flat", "date"]),
            models.Index(fields=["flat", "user", "date"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} | {self.date} | {self.meal_count}"


class MonthlySummary(TimeStampedModel):
    """
    Cached monthly calculation per flat.
    Recalculated on every meal/expense update for the relevant month.
    """

    flat = models.ForeignKey(
        "flats.Flat", on_delete=models.CASCADE, related_name="monthly_summaries"
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1-12

    total_meals = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    meal_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_locked = models.BooleanField(default=False, help_text="Month-lock flag")
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_summaries",
    )
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "monthly_summaries"
        unique_together = ("flat", "year", "month")
        indexes = [
            models.Index(fields=["flat", "year", "month"]),
        ]

    def __str__(self):
        return f"{self.flat.name} | {self.year}-{self.month:02d} | Rate: {self.meal_rate}"
