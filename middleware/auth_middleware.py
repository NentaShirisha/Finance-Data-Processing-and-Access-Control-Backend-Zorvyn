"""
JWT Authentication Middleware.
"""
from utils.jwt_handler import JWTHandler
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """
    Middleware to extract and validate JWT token from requests.
    Adds user context to request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract and validate token
        token = JWTHandler.extract_token_from_header(request)
        
        if token:
            payload = JWTHandler.verify_token(token)
            if payload:
                # Attach user info to request
                request.user_id = payload['user_id']
                request.user_role = payload['role']
                request.user_email = payload['email']
                request.is_authenticated = True
                logger.debug(f"User authenticated: {request.user_id}")
            else:
                request.is_authenticated = False
                logger.warning("Token verification failed")
        else:
            request.is_authenticated = False
        
        response = self.get_response(request)
        return response
