"""
Records Admin Configuration.
"""
from django.contrib import admin
from apps.records.models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'category', 'amount', 'date', 'created_at', 'is_deleted']
    list_filter = ['type', 'category', 'date', 'created_at', 'is_deleted']
    search_fields = ['user__name', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
