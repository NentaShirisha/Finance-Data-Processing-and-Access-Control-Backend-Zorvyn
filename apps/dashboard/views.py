"""
Dashboard Views for analytics and summary information.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.dashboard.serializers import (
    DashboardSummarySerializer, CategoryTotalSerializer,
    MonthlyTrendSerializer, RecentTransactionSerializer
)
from apps.records.services import RecordService
from apps.records.models import FinancialRecord
from utils.response_formatter import ResponseFormatter
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard analytics and summaries.
    Permissions:
    - Viewers: Can access dashboard only
    - Analysts: Can access their own dashboard
    - Admins: Can access any user's dashboard
    """
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Get dashboard summary statistics.
        Query parameters:
        - user_id: Get dashboard for specific user (admin only)
        - date_from: Summary from date (YYYY-MM-DD)
        - date_to: Summary to date (YYYY-MM-DD)
        
        Returns:
        {
            "total_income": 5000.00,
            "total_expense": 2000.00,
            "net_balance": 3000.00,
            "income_count": 5,
            "expense_count": 8,
            "period": "Last 30 days"
        }
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        
        # Determine user_id
        target_user_id = request.query_params.get('user_id')
        if target_user_id:
            if user_role != 'admin':
                return ResponseFormatter.error(
                    message="Access denied: Only admins can view other users' data",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            user_id = int(target_user_id)
        else:
            user_id = request.user_id
        
        # Parse dates
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        period_label = "All time"
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except:
                date_from = None
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except:
                date_to = None
        
        if date_from and date_to:
            period_label = f"{date_from} to {date_to}"
        elif date_from:
            period_label = f"From {date_from}"
        elif date_to:
            period_label = f"Until {date_to}"
        
        # Calculate summary
        total_income = RecordService.get_total_income(user_id, date_from, date_to)
        total_expense = RecordService.get_total_expense(user_id, date_from, date_to)
        net_balance = RecordService.get_net_balance(user_id, date_from, date_to)
        
        # Count transactions
        query = FinancialRecord.objects.filter(user_id=user_id, is_deleted=False)
        if date_from:
            query = query.filter(date__gte=date_from)
        if date_to:
            query = query.filter(date__lte=date_to)
        
        income_count = query.filter(type='income').count()
        expense_count = query.filter(type='expense').count()
        
        data = {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'income_count': income_count,
            'expense_count': expense_count,
            'period': period_label,
        }
        
        return ResponseFormatter.success(data=data, message="Dashboard summary")

    @action(detail=False, methods=['get'], url_path='category-breakdown')
    def category_breakdown(self, request):
        """
        Get category-wise breakdown of transactions.
        Query parameters:
        - user_id: Get breakdown for specific user (admin only)
        - type: Filter by type (income/expense)
        - date_from: From date (YYYY-MM-DD)
        - date_to: To date (YYYY-MM-DD)
        
        Returns:
        [
            {"category": "salary", "total": 5000.00, "count": 2},
            {"category": "grocery", "total": 1000.00, "count": 5},
            ...
        ]
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        if user_role == 'viewer':
            return ResponseFormatter.error(
                message="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Determine user_id
        target_user_id = request.query_params.get('user_id')
        if target_user_id:
            if user_role != 'admin':
                return ResponseFormatter.error(
                    message="Access denied",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            user_id = int(target_user_id)
        else:
            user_id = request.user_id
        
        record_type = request.query_params.get('type')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except:
                date_from = None
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except:
                date_to = None
        
        totals = RecordService.get_category_totals(
            user_id=user_id,
            record_type=record_type,
            date_from=date_from,
            date_to=date_to
        )
        
        return ResponseFormatter.success(
            data=totals,
            message="Category breakdown"
        )

    @action(detail=False, methods=['get'], url_path='monthly-trends')
    def monthly_trends(self, request):
        """
        Get monthly income and expense trends.
        Query parameters:
        - user_id: Get trends for specific user (admin only)
        - type: Filter by type (income/expense)
        
        Returns:
        [
            {
                "month": "2024-01-01",
                "type": "income",
                "total": 5000.00,
                "count": 2
            },
            ...
        ]
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        if user_role == 'viewer':
            return ResponseFormatter.error(
                message="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Determine user_id
        target_user_id = request.query_params.get('user_id')
        if target_user_id:
            if user_role != 'admin':
                return ResponseFormatter.error(
                    message="Access denied",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            user_id = int(target_user_id)
        else:
            user_id = request.user_id
        
        record_type = request.query_params.get('type')
        
        trends = RecordService.get_monthly_trends(
            user_id=user_id,
            record_type=record_type
        )
        
        return ResponseFormatter.success(
            data=trends,
            message="Monthly trends"
        )

    @action(detail=False, methods=['get'], url_path='recent-activity')
    def recent_activity(self, request):
        """
        Get recent transactions.
        Query parameters:
        - limit: Number of recent records to return (default: 10)
        - user_id: Get activity for specific user (admin only)
        
        Returns:
        [
            {
                "id": 1,
                "user_name": "John Doe",
                "type": "income",
                "category": "salary",
                "amount": 5000.00,
                "date": "2024-01-15",
                "created_at": "2024-01-15T10:30:00Z"
            },
            ...
        ]
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Determine user_id
        target_user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 10))
        
        if target_user_id:
            if request.user_role != 'admin':
                return ResponseFormatter.error(
                    message="Access denied",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            user_id = int(target_user_id)
        else:
            user_id = request.user_id if request.user_role != 'admin' else None
        
        records = RecordService.get_recent_records(user_id=user_id, limit=limit)
        
        data = [
            {
                'id': r.id,
                'user_name': r.user.name,
                'type': r.type,
                'category': r.category,
                'amount': str(r.amount),
                'date': r.date.isoformat(),
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]
        
        return ResponseFormatter.success(
            data=data,
            message="Recent activity"
        )

    @action(detail=False, methods=['get'], url_path='stats')
    def statistics(self, request):
        """
        Comprehensive statistics for dashboard.
        Combines all data into one endpoint.
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        if user_role == 'viewer':
            # Viewers get limited stats (only from specific date range)
            return ResponseFormatter.error(
                message="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Determine user_id
        target_user_id = request.query_params.get('user_id')
        if target_user_id:
            if user_role != 'admin':
                return ResponseFormatter.error(
                    message="Access denied",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            user_id = int(target_user_id)
        else:
            user_id = request.user_id
        
        # Get summary
        total_income = RecordService.get_total_income(user_id)
        total_expense = RecordService.get_total_expense(user_id)
        net_balance = RecordService.get_net_balance(user_id)
        
        # Get totals
        query = FinancialRecord.objects.filter(user_id=user_id, is_deleted=False)
        income_count = query.filter(type='income').count()
        expense_count = query.filter(type='expense').count()
        
        # Get category breakdown
        category_breakdown = RecordService.get_category_totals(user_id=user_id)
        
        # Get recent activity
        recent = RecordService.get_recent_records(user_id=user_id, limit=5)
        recent_data = [
            {
                'id': r.id,
                'type': r.type,
                'category': r.category,
                'amount': str(r.amount),
                'date': r.date.isoformat(),
            }
            for r in recent
        ]
        
        data = {
            'summary': {
                'total_income': str(total_income),
                'total_expense': str(total_expense),
                'net_balance': str(net_balance),
                'income_count': income_count,
                'expense_count': expense_count,
            },
            'category_breakdown': category_breakdown,
            'recent_activity': recent_data,
        }
        
        return ResponseFormatter.success(
            data=data,
            message="Comprehensive dashboard statistics"
        )
