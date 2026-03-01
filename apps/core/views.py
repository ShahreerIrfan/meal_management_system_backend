"""
Core views – Activity Log.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogListView(generics.ListAPIView):
    """List activity logs for the current flat."""

    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        flat = getattr(self.request, "flat", None)
        qs = ActivityLog.objects.select_related("user")
        if flat:
            qs = qs.filter(flat=flat)
        else:
            qs = qs.filter(user=self.request.user)

        # Optional filter by user
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)

        # Optional filter by action type
        action = self.request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)

        return qs[:100]  # Limit to last 100 entries

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "logs": serializer.data})
