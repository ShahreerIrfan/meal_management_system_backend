from django.urls import path
from . import views

app_name = "permissions"

urlpatterns = [
    path("all/", views.AllPermissionsView.as_view(), name="all_permissions"),
    path("mine/", views.MyPermissionsView.as_view(), name="my_permissions"),
    path("member/<uuid:membership_id>/", views.MemberPermissionsView.as_view(), name="member_perms"),
    path("set/", views.SetPermissionsView.as_view(), name="set_permissions"),
]
