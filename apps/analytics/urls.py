from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("meal-per-user/", views.MealCountPerUserView.as_view(), name="meal_per_user"),
    path("expense-share/", views.ExpenseShareView.as_view(), name="expense_share"),
    path("daily-meals/", views.DailyMealTrendView.as_view(), name="daily_meals"),
    path("monthly-comparison/", views.MonthlyComparisonView.as_view(), name="monthly_comparison"),
]
