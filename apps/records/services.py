"""
Records Services Layer.
Business logic for financial records operations.
"""
from apps.records.models import FinancialRecord
from apps.users.models import User
from django.db.models import Q, Sum
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class RecordService:
    """Service class for financial record operations."""
    
    @staticmethod
    def create_record(user_id, amount, record_type, category, date, description=''):
        """
        Create new financial record.
        
        Args:
            user_id: User who owns the record
            amount: Transaction amount
            record_type: 'income' or 'expense'
            category: Transaction category
            date: Transaction date
            description: Optional description
            
        Returns:
            Created record or None
        """
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
            record = FinancialRecord(
                user=user,
                amount=amount,
                type=record_type,
                category=category,
                date=date,
                description=description
            )
            record.save()
            logger.info(f"Record created for user {user_id}: {record_type} {amount}")
            return record
        except User.DoesNotExist:
            logger.warning(f"User not found: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error creating record: {str(e)}")
            return None

    @staticmethod
    def get_record(record_id, user_id=None):
        """
        Get financial record.
        
        Args:
            record_id: Record ID
            user_id: Optional user ID for validation
            
        Returns:
            Record or None
        """
        query = FinancialRecord.objects.filter(id=record_id, is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        return query.first()

    @staticmethod
    def get_records(user_id=None, record_type=None, category=None, 
                   date_from=None, date_to=None, search=None):
        """
        Get financial records with filters.
        
        Args:
            user_id: Filter by user
            record_type: Filter by type (income/expense)
            category: Filter by category
            date_from: Filter records from date
            date_to: Filter records to date
            search: Search in description
            
        Returns:
            QuerySet of records
        """
        queryset = FinancialRecord.objects.filter(is_deleted=False).select_related('user')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if record_type:
            queryset = queryset.filter(type=record_type)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if search:
            queryset = queryset.filter(description__icontains=search)
        
        return queryset.order_by('-date')

    @staticmethod
    def update_record(record_id, user_id=None, **kwargs):
        """
        Update financial record.
        
        Args:
            record_id: Record ID
            user_id: Optional user ID for validation
            **kwargs: Fields to update
            
        Returns:
            Updated record or None
        """
        try:
            record = FinancialRecord.objects.get(id=record_id, is_deleted=False)
            
            if user_id and record.user_id != user_id:
                logger.warning(f"Unauthorized update attempt by user {user_id}")
                return None
            
            for key, value in kwargs.items():
                if hasattr(record, key) and key not in ['id', 'user', 'created_at']:
                    setattr(record, key, value)
            
            record.save()
            logger.info(f"Record updated: {record_id}")
            return record
        except FinancialRecord.DoesNotExist:
            logger.warning(f"Record not found: {record_id}")
            return None

    @staticmethod
    def delete_record(record_id, user_id=None):
        """
        Soft delete financial record.
        
        Args:
            record_id: Record ID
            user_id: Optional user ID for validation
            
        Returns:
            Boolean indicating success
        """
        try:
            record = FinancialRecord.objects.get(id=record_id)
            
            if user_id and record.user_id != user_id:
                logger.warning(f"Unauthorized delete attempt by user {user_id}")
                return False
            
            record.is_deleted = True
            record.save()
            logger.info(f"Record deleted: {record_id}")
            return True
        except FinancialRecord.DoesNotExist:
            logger.warning(f"Record not found: {record_id}")
            return False

    @staticmethod
    def get_total_income(user_id=None, date_from=None, date_to=None):
        """Get total income for user."""
        query = FinancialRecord.objects.filter(type='income', is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        if date_from:
            query = query.filter(date__gte=date_from)
        
        if date_to:
            query = query.filter(date__lte=date_to)
        
        total = query.aggregate(Sum('amount'))['amount__sum']
        return total or Decimal('0')

    @staticmethod
    def get_total_expense(user_id=None, date_from=None, date_to=None):
        """Get total expense for user."""
        query = FinancialRecord.objects.filter(type='expense', is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        if date_from:
            query = query.filter(date__gte=date_from)
        
        if date_to:
            query = query.filter(date__lte=date_to)
        
        total = query.aggregate(Sum('amount'))['amount__sum']
        return total or Decimal('0')

    @staticmethod
    def get_net_balance(user_id=None, date_from=None, date_to=None):
        """Get net balance (income - expense)."""
        income = RecordService.get_total_income(user_id, date_from, date_to)
        expense = RecordService.get_total_expense(user_id, date_from, date_to)
        return income - expense

    @staticmethod
    def get_category_totals(user_id=None, record_type=None, date_from=None, date_to=None):
        """Get totals by category."""
        query = FinancialRecord.objects.filter(is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        if record_type:
            query = query.filter(type=record_type)
        
        if date_from:
            query = query.filter(date__gte=date_from)
        
        if date_to:
            query = query.filter(date__lte=date_to)
        
        totals = query.values('category').annotate(
            total=Sum('amount'),
            count=models.Count('id')
        ).order_by('-total')
        
        return list(totals)

    @staticmethod
    def get_monthly_trends(user_id=None, record_type=None):
        """Get monthly income/expense trends."""
        from django.db.models import F
        from django.db.models.functions import TruncMonth
        
        query = FinancialRecord.objects.filter(is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        if record_type:
            query = query.filter(type=record_type)
        
        trends = query.annotate(
            month=TruncMonth('date')
        ).values('month', 'type').annotate(
            total=Sum('amount'),
            count=models.Count('id')
        ).order_by('month')
        
        return list(trends)

    @staticmethod
    def get_recent_records(user_id=None, limit=10):
        """Get recent financial records."""
        query = FinancialRecord.objects.filter(is_deleted=False)
        
        if user_id:
            query = query.filter(user_id=user_id)
        
        return query.order_by('-created_at')[:limit]


# Import models for the service
from django.db import models
