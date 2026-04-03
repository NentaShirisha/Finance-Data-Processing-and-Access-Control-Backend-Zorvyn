"""
Records Views/ViewSets for API endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.records.models import FinancialRecord
from apps.records.serializers import (
    FinancialRecordSerializer, FinancialRecordCreateSerializer,
    FinancialRecordListSerializer
)
from apps.records.services import RecordService
from utils.response_formatter import ResponseFormatter
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial records.
    Permissions:
    - Analyst and Admin can create records
    - Users can view their own records
    - Admin can view all records
    """
    
    def get_queryset(self):
        """Get records based on user role."""
        user_role = getattr(self.request, 'user_role', None)
        user_id = getattr(self.request, 'user_id', None)
        
        if user_role == 'admin':
            # Admins see all records
            return FinancialRecord.objects.filter(is_deleted=False)
        else:
            # Others see only their own
            return FinancialRecord.objects.filter(
                user_id=user_id,
                is_deleted=False
            )
    
    def list(self, request, *args, **kwargs):
        """
        List financial records with optional filters.
        Query parameters:
        - type: Filter by type (income/expense)
        - category: Filter by category
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - search: Search in description
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        if user_role == 'viewer':
            return ResponseFormatter.error(
                message="Access denied: Viewers cannot access records",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Get filters from query params
        record_type = request.query_params.get('type')
        category = request.query_params.get('category')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        search = request.query_params.get('search')
        
        # Determine user_id filter
        user_id = None if user_role == 'admin' else request.user_id
        
        # Parse dates
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
        
        records = RecordService.get_records(
            user_id=user_id,
            record_type=record_type,
            category=category,
            date_from=date_from,
            date_to=date_to,
            search=search
        )
        
        # Pagination
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = FinancialRecordListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FinancialRecordListSerializer(records, many=True)
        return ResponseFormatter.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create new financial record.
        Analysts and Admins only.
        
        Request body:
        {
            "amount": 100.50,
            "type": "income",
            "category": "salary",
            "date": "2024-01-15",
            "description": "Monthly salary"
        }
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user_role = request.user_role
        if user_role not in ['analyst', 'admin']:
            return ResponseFormatter.error(
                message="Access denied: Only analysts and admins can create records",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = FinancialRecordCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseFormatter.error(
                message="Invalid data",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        record = RecordService.create_record(
            user_id=request.user_id,
            amount=serializer.validated_data['amount'],
            record_type=serializer.validated_data['type'],
            category=serializer.validated_data['category'],
            date=serializer.validated_data['date'],
            description=serializer.validated_data.get('description', '')
        )
        
        if not record:
            return ResponseFormatter.error(
                message="Failed to create record",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return ResponseFormatter.success(
            data=FinancialRecordSerializer(record).data,
            message="Record created successfully",
            status_code=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """Get specific financial record."""
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        record_id = kwargs.get('pk')
        user_id = None if request.user_role == 'admin' else request.user_id
        
        record = RecordService.get_record(record_id, user_id)
        if not record:
            return ResponseFormatter.error(
                message="Record not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return ResponseFormatter.success(data=FinancialRecordSerializer(record).data)

    def update(self, request, *args, **kwargs):
        """
        Update financial record.
        Users can update their own, admins can update any.
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        record_id = kwargs.get('pk')
        user_id = None if request.user_role == 'admin' else request.user_id
        
        record = RecordService.get_record(record_id, user_id)
        if not record:
            return ResponseFormatter.error(
                message="Record not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FinancialRecordCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return ResponseFormatter.error(
                message="Invalid data",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
        
        updated_record = RecordService.update_record(
            record_id,
            user_id=user_id,
            **serializer.validated_data
        )
        
        if not updated_record:
            return ResponseFormatter.error(
                message="Failed to update record",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return ResponseFormatter.success(
            data=FinancialRecordSerializer(updated_record).data,
            message="Record updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete financial record (soft delete).
        Only admins can delete records.
        """
        if not getattr(request, 'is_authenticated', False):
            return ResponseFormatter.error(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if request.user_role != 'admin':
            return ResponseFormatter.error(
                message="Access denied: Only admins can delete records",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        record_id = kwargs.get('pk')
        user_id = None
        
        if not RecordService.get_record(record_id, user_id):
            return ResponseFormatter.error(
                message="Record not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if RecordService.delete_record(record_id, user_id):
            return ResponseFormatter.success(message="Record deleted successfully")
        
        return ResponseFormatter.error(
            message="Unable to delete record",
            status_code=status.HTTP_400_BAD_REQUEST
        )
