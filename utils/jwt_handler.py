"""
JWT Token Utilities.
"""
import jwt
import json
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """
    Handles JWT token generation and validation.
    """
    
    @staticmethod
    def generate_token(user_id, role, email, expiration_hours=None):
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_id: User ID
            role: User role (viewer, analyst, admin)
            email: User email
            expiration_hours: Token expiration time in hours
            
        Returns:
            JWT token string
        """
        if expiration_hours is None:
            expiration_hours = settings.JWT_CONFIG['EXPIRATION_HOURS']
        
        payload = {
            'user_id': user_id,
            'role': role,
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        }
        
        token = jwt.encode(
            payload,
            settings.JWT_CONFIG['SECRET_KEY'],
            algorithm=settings.JWT_CONFIG['ALGORITHM']
        )
        
        logger.info(f"Token generated for user: {user_id}")
        return token

    @staticmethod
    def verify_token(token):
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None if token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_CONFIG['SECRET_KEY'],
                algorithms=[settings.JWT_CONFIG['ALGORITHM']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

    @staticmethod
    def extract_token_from_header(request):
        """
        Extract JWT token from Authorization header.
        
        Args:
            request: Django request object
            
        Returns:
            Token string or None
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        return auth_header[7:]  # Remove 'Bearer ' prefix
