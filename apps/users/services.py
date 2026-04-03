"""
User Services Layer.
Services contain business logic separated from views.
"""
from apps.users.models import User, Role
from utils.jwt_handler import JWTHandler
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user and generate JWT token.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Dict with token and user info or None
        """
        try:
            user = User.objects.get(email=email, is_deleted=False)
            
            if user.status != 'active':
                logger.warning(f"Login attempt for inactive user: {email}")
                return None
            
            if not user.verify_password(password):
                logger.warning(f"Failed login attempt for: {email}")
                return None
            
            token = JWTHandler.generate_token(
                user_id=user.id,
                role=user.role.name,
                email=user.email
            )
            
            logger.info(f"User authenticated: {email}")
            return {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.name,
                'token': token,
            }
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return None

    @staticmethod
    def get_user(user_id):
        """Get user by ID."""
        return User.objects.filter(id=user_id, is_deleted=False).first()

    @staticmethod
    def get_users(role_filter=None, status_filter=None, search=None):
        """
        Get users with optional filters.
        
        Args:
            role_filter: Filter by role name
            status_filter: Filter by status
            search: Search in name or email
            
        Returns:
            QuerySet of users
        """
        queryset = User.objects.filter(is_deleted=False).select_related('role')
        
        if role_filter:
            queryset = queryset.filter(role__name=role_filter)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | models.Q(email__icontains=search)
            )
        
        return queryset

    @staticmethod
    def create_user(name, email, password, role_id, status='active'):
        """
        Create new user.
        
        Args:
            name: User name
            email: User email
            password: Plain text password
            role_id: Role ID
            status: User status
            
        Returns:
            Created user or None
        """
        try:
            role = Role.objects.get(id=role_id)
            user = User(
                name=name,
                email=email,
                role=role,
                status=status
            )
            user.set_password(password)
            user.save()
            logger.info(f"User created: {email}")
            return user
        except Role.DoesNotExist:
            logger.error(f"Role not found: {role_id}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Update user.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated user or None
        """
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
            
            for key, value in kwargs.items():
                if key == 'password':
                    user.set_password(value)
                elif hasattr(user, key):
                    setattr(user, key, value)
            
            user.save()
            logger.info(f"User updated: {user.email}")
            return user
        except User.DoesNotExist:
            logger.warning(f"User not found: {user_id}")
            return None

    @staticmethod
    def delete_user(user_id):
        """
        Soft delete user (set is_deleted=True).
        
        Args:
            user_id: User ID
            
        Returns:
            Boolean indicating success
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_deleted = True
            user.status = 'inactive'
            user.save()
            logger.info(f"User deleted: {user.email}")
            return True
        except User.DoesNotExist:
            logger.warning(f"User not found: {user_id}")
            return False

    @staticmethod
    def initialize_roles():
        """Initialize default roles if they don't exist."""
        roles_data = [
            {
                'name': 'viewer',
                'description': 'Can only view dashboard data',
                'permissions': {
                    'view_dashboard': True,
                    'view_records': False,
                    'create_records': False,
                    'update_records': False,
                    'delete_records': False,
                    'manage_users': False,
                }
            },
            {
                'name': 'analyst',
                'description': 'Can view records and access analytics',
                'permissions': {
                    'view_dashboard': True,
                    'view_records': True,
                    'create_records': True,
                    'update_records': True,
                    'delete_records': False,
                    'manage_users': False,
                }
            },
            {
                'name': 'admin',
                'description': 'Full access including user management',
                'permissions': {
                    'view_dashboard': True,
                    'view_records': True,
                    'create_records': True,
                    'update_records': True,
                    'delete_records': True,
                    'manage_users': True,
                }
            },
        ]
        
        for role_data in roles_data:
            Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions'],
                }
            )
        
        logger.info("Default roles initialized")


# Import models for the service
from django.db import models
