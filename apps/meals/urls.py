from django.urls import path
from . import views

app_name = "meals"

urlpatterns = [
    path("grid/", views.MealGridView.as_view(), name="meal_grid"),
    path("cell/", views.MealCellUpdateView.as_view(), name="meal_cell_update"),
    path("summary/", views.MonthSummaryView.as_view(), name="month_summary"),
    path("lock-month/", views.LockMonthView.as_view(), name="lock_month"),
    path("unlock-month/", views.UnlockMonthView.as_view(), name="unlock_month"),
]
