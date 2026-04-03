"""
Response Utility Functions.
"""
from rest_framework.response import Response
from rest_framework import status


class ResponseFormatter:
    """
    Formats consistent API responses.
    """
    
    @staticmethod
    def success(data=None, message="Operation successful", status_code=status.HTTP_200_OK):
        """
        Format success response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Response object
        """
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status_code
        )

    @staticmethod
    def error(message="Operation failed", status_code=status.HTTP_400_BAD_REQUEST, errors=None):
        """
        Format error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            errors: Additional error details
            
        Returns:
            Response object
        """
        return Response(
            {
                'success': False,
                'message': message,
                'errors': errors,
            },
            status=status_code
        )
