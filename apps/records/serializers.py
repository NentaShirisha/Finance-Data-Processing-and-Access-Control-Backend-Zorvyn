"""
Records Serializers.
"""
from rest_framework import serializers
from apps.records.models import FinancialRecord
from decimal import Decimal


class FinancialRecordSerializer(serializers.ModelSerializer):
    """Serializer for Financial Record."""
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'user', 'user_name', 'amount', 'type', 'category',
            'date', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate(self, data):
        """Validate record data."""
        # Ensure amount is decimal
        if isinstance(data.get('amount'), str):
            try:
                data['amount'] = Decimal(data['amount'])
            except:
                raise serializers.ValidationError("Invalid amount format.")
        
        return data


class FinancialRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating financial records."""
    
    class Meta:
        model = FinancialRecord
        fields = ['amount', 'type', 'category', 'date', 'description']

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class FinancialRecordListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views."""
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'user_name', 'amount', 'type', 'category',
            'date', 'created_at'
        ]
