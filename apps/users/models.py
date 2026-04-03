"""
User Models.
"""
from django.db import models
from utils.password_handler import PasswordHandler
import logging

logger = logging.getLogger(__name__)


class Role(models.Model):
    """
    Role model for RBAC.
    
    Roles:
    - viewer: Can only view dashboard data
    - analyst: Can view records and access insights
    - admin: Full access including user management
    """
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Role name: viewer, analyst, or admin"
    )
    description = models.TextField(blank=True, help_text="Role description")
    permissions = models.JSONField(default=dict, help_text="Role permissions in JSON format")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.description}"

    class Meta:
        ordering = ['name']
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class User(models.Model):
    """
    User Model.
    
    Fields:
    - id: Primary key
    - name: Full name of the user
    - email: Unique email address
    - password: Hashed password
    - role: User's role (viewer, analyst, admin)
    - status: User account status (active, inactive)
    - created_at: Account creation timestamp
    - updated_at: Last update timestamp
    - is_deleted: Soft delete flag
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=255, help_text="User's full name")
    email = models.EmailField(unique=True, help_text="User's email address")
    password = models.CharField(max_length=255, help_text="Hashed password")
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        help_text="User's role"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="User account status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")

    def __str__(self):
        return f"{self.name} ({self.email})"

    def set_password(self, raw_password):
        """Hash and set password."""
        self.password = PasswordHandler.hash_password(raw_password)
        logger.info(f"Password set for user: {self.email}")

    def verify_password(self, raw_password):
        """Verify password against hash."""
        return PasswordHandler.verify_password(raw_password, self.password)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"
