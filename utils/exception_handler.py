"""
Exception Handler Configuration.
"""
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses.
    """
    response_data = {
        'success': False,
        'message': str(exc),
        'data': None,
    }

    if isinstance(exc, Exception):
        logger.error(f"Exception: {type(exc).__name__} - {str(exc)}", exc_info=True)
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        response_status = status.HTTP_400_BAD_REQUEST

    return Response(response_data, status=response_status)
