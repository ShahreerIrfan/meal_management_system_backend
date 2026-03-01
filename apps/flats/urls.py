from django.urls import path
from . import views

app_name = "flats"

urlpatterns = [
    path("me/", views.MyFlatsView.as_view(), name="my_flats"),
    path("current/", views.FlatDetailView.as_view(), name="flat_detail"),
    path("members/", views.FlatMemberListView.as_view(), name="member_list"),
    path("members/<uuid:membership_id>/remove/", views.RemoveMemberView.as_view(), name="remove_member"),
    path("invite/", views.CreateInviteView.as_view(), name="create_invite"),
    path("invite/<str:token>/info/", views.InviteInfoView.as_view(), name="invite_info"),
    path("invites/", views.ListInvitesView.as_view(), name="list_invites"),
    path("join/", views.JoinFlatView.as_view(), name="join_flat"),
    path("register-and-join/", views.RegisterAndJoinView.as_view(), name="register_and_join"),
    path("member-month-status/", views.MemberMonthStatusListView.as_view(), name="member_month_status_list"),
    path("member-month-status/update/", views.MemberMonthStatusUpdateView.as_view(), name="member_month_status_update"),
]
