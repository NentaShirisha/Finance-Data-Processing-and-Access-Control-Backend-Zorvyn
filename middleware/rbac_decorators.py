"""
RBAC (Role-Based Access Control) Decorators.
"""
from functools import wraps
from rest_framework import status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def require_auth(view_func):
    """
    Decorator to require authentication.
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            logger.warning("Unauthorized access attempt")
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    """
    Decorator to check user role for authorization.
    
    Args:
        *allowed_roles: Tuple of allowed roles (viewer, analyst, admin)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not getattr(request, 'is_authenticated', False):
                logger.warning("Unauthorized access attempt: not authenticated")
                return Response(
                    {'success': False, 'message': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_role = getattr(request, 'user_role', None)
            if user_role not in allowed_roles:
                logger.warning(f"Access denied: user role '{user_role}' not in {allowed_roles}")
                return Response(
                    {'success': False, 'message': 'Access denied: insufficient permissions'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_owner_or_admin(view_func):
    """
    Decorator to check if user is owner or admin.
    """
    @wraps(view_func)
    def wrapper(self, request, *args, user_id=None, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            logger.warning("Unauthorized access attempt: not authenticated")
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        request_user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if user_role != 'admin' and request_user_id != user_id:
            logger.warning(f"Access denied: user {request_user_id} attempting to access user {user_id} data")
            return Response(
                {'success': False, 'message': 'Access denied: insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(self, request, *args, user_id=user_id, **kwargs)
    return wrapper
