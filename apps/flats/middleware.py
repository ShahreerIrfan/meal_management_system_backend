"""
Flat-context middleware – injects current flat into request
based on X-Flat-ID header or user's active membership.

Works with JWT authentication by parsing the token in the middleware
since DRF auth runs after Django middleware.
"""
from django.utils.deprecation import MiddlewareMixin
from apps.flats.models import FlatMembership


class FlatContextMiddleware(MiddlewareMixin):
    """
    Attaches `request.flat` and `request.membership` for authenticated users.
    Frontend sends header  X-Flat-ID: <uuid>.
    Falls back to user's first active membership.

    Since DRF's JWT authentication runs AFTER Django middleware,
    we manually parse the JWT token here to get the user.
    """

    def process_request(self, request):
        request.flat = None
        request.membership = None

        user = getattr(request, "user", None)

        # If user is not yet authenticated (JWT auth hasn't run yet),
        # try to parse the JWT token manually.
        if not user or not user.is_authenticated:
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                jwt_auth = JWTAuthentication()
                result = jwt_auth.authenticate(request)
                if result:
                    user, _token = result
                    request.user = user
            except Exception:
                return

        if not user or not user.is_authenticated:
            return

        flat_id = request.headers.get("X-Flat-ID")
        qs = FlatMembership.objects.select_related("flat").filter(
            user=user, is_active=True
        )

        if flat_id:
            membership = qs.filter(flat_id=flat_id).first()
        else:
            membership = qs.first()

        if membership:
            request.flat = membership.flat
            request.membership = membership
