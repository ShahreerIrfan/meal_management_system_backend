from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.ExpenseListCreateView.as_view(), name="expense_list_create"),
    path("<uuid:pk>/", views.ExpenseDetailView.as_view(), name="expense_detail"),
    path("audit/", views.AuditLogListView.as_view(), name="audit_log"),
]
