"""
User Serializers.
"""
from rest_framework import serializers
from apps.users.models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    role_detail = RoleSerializer(source='role', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'role_detail',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'role_detail']

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating users."""
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role', 'status']

    def create(self, validated_data):
        """Create user with hashed password."""
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user."""
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with all information.
    Used for admin viewing user details.
    """
    role_detail = RoleSerializer(source='role', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'role_detail',
            'status', 'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
