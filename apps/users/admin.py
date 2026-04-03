"""
User Admin Configuration.
"""
from django.contrib import admin
from apps.users.models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'status', 'created_at', 'is_deleted']
    list_filter = ['role', 'status', 'created_at', 'is_deleted']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']
