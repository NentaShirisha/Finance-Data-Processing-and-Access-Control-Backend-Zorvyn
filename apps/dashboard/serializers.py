"""
Dashboard serializers for analytics data.
"""
from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary statistics."""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_count = serializers.IntegerField()
    expense_count = serializers.IntegerField()
    period = serializers.CharField()


class CategoryTotalSerializer(serializers.Serializer):
    """Serializer for category-wise totals."""
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()


class MonthlyTrendSerializer(serializers.Serializer):
    """Serializer for monthly trends."""
    month = serializers.DateTimeField()
    type = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()


class RecentTransactionSerializer(serializers.Serializer):
    """Serializer for recent transactions."""
    id = serializers.IntegerField()
    user_name = serializers.CharField()
    type = serializers.CharField()
    category = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    date = serializers.DateField()
    created_at = serializers.DateTimeField()
