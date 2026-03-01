"""
Custom exception handler for DRF – consistent error envelope.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "errors": response.data,
            "status_code": response.status_code,
        }
        response.data = custom_data
        return response

    # Unhandled 500
    return Response(
        {"success": False, "errors": {"detail": "Internal server error"}, "status_code": 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
