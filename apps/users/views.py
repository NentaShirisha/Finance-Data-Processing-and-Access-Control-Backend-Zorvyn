"""
User Views/ViewSets for API endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.models import User, Role
from apps.users.serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    UserDetailSerializer, RoleSerializer
)
from apps.users.services import UserService
from utils.response_formatter import ResponseFormatter
from middleware.rbac_decorators import require_auth, require_role
import logging

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication endpoints.
    Handles login, registration, and token refresh.
    """
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register new user.
        
        Request body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123",
            "role": 1,
            "status": "active"
        }
        """
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.email}")
            return ResponseFormatter.success(
                data=UserSerializer(user).data,
                message="User registered successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return ResponseFormatter.error(
            message="Registration failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate user and return JWT token.
        
        Request body:
        {
            "email": "john@example.com",
            "password": "securepass123"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseFormatter.error(
                message="Invalid credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        result = UserService.authenticate_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if result:
            return ResponseFormatter.success(
                data=result,
                message="Login successful"
            )
        
        return ResponseFormatter.error(
            message="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=['get'], url_path='verify')
    def verify_token(self, request):
        """
        Verify current JWT token and return user info.
        Requires Authentication header: Authorization: Bearer <token>
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user = UserService.get_user(request.user_id)
        if not user:
            return ResponseFormatter.error(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return ResponseFormatter.success(
            data={
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.name,
                'status': user.status,
            },
            message="Token is valid"
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.
    Available to admin users only.
    """
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    lookup_field = 'id'
    
    def list(self, request, *args, **kwargs):
        """
        List all users (admin only).
        Query parameters:
        - role: Filter by role name (viewer, analyst, admin)
        - status: Filter by status (active, inactive, suspended)
        - search: Search in name or email
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user_role != 'admin':
            return ResponseFormatter.error(
                message="Access denied: Only admins can list users",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        role_filter = request.query_params.get('role')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')
        
        queryset = UserService.get_users(
            role_filter=role_filter,
            status_filter=status_filter,
            search=search
        )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserDetailSerializer(queryset, many=True)
        return ResponseFormatter.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """Create new user (admin only)."""
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user_role != 'admin':
            return ResponseFormatter.error(
                message="Access denied: Only admins can create users",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return ResponseFormatter.success(
                data=UserSerializer(user).data,
                message="User created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return ResponseFormatter.error(
            message="Failed to create user",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )

    def retrieve(self, request, *args, **kwargs):
        """Get user details."""
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_id = kwargs.get('id')
        
        # Users can view their own profile, admins can view anyone
        if request.user_role != 'admin' and request.user_id != int(user_id):
            return ResponseFormatter.error(
                message="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        user = UserService.get_user(user_id)
        if not user:
            return ResponseFormatter.error(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return ResponseFormatter.success(data=UserDetailSerializer(user).data)

    def update(self, request, *args, **kwargs):
        """Update user (admin only or own profile)."""
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_id = kwargs.get('id')
        
        if request.user_role != 'admin' and request.user_id != int(user_id):
            return ResponseFormatter.error(
                message="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        user = UserService.get_user(user_id)
        if not user:
            return ResponseFormatter.error(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormatter.success(
                data=UserSerializer(user).data,
                message="User updated successfully"
            )
        
        return ResponseFormatter.error(
            message="Failed to update user",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        """Delete user (admin only)."""
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if request.user_role != 'admin':
            return ResponseFormatter.error(
                message="Access denied: Only admins can delete users",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        user_id = kwargs.get('id')
        if UserService.delete_user(user_id):
            return ResponseFormatter.success(message="User deleted successfully")
        
        return ResponseFormatter.error(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing roles (read-only)."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
    def list(self, request):
        """List all available roles."""
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return ResponseFormatter.success(data=serializer.data)
