"""
Financial Records Models.
"""
from django.db import models
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class FinancialRecord(models.Model):
    """
    Financial Record/Transaction Model.
    
    Stores income and expense transactions for users.
    
    Fields:
    - id: Primary key
    - user_id: Owner of the record
    - amount: Transaction amount (must be > 0)
    - type: Income or Expense
    - category: Transaction category
    - date: Transaction date
    - description: Transaction notes
    - created_at: Record creation timestamp
    - updated_at: Last update timestamp
    - is_deleted: Soft delete flag
    """
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('freelance', 'Freelance'),
        ('investment', 'Investment'),
        ('grocery', 'Grocery'),
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='financial_records',
        help_text="User who owns this record"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount (must be positive)"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        help_text="Income or Expense"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Transaction category"
    )
    date = models.DateField(help_text="Transaction date")
    description = models.TextField(
        blank=True,
        help_text="Transaction description/notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")

    def __str__(self):
        return f"{self.type.upper()} - {self.category}: {self.amount} by {self.user.name}"

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['user', 'category']),
        ]
        verbose_name = "Financial Record"
        verbose_name_plural = "Financial Records"
