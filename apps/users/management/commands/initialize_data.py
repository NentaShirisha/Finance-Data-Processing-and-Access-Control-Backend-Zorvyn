"""
Management command to initialize roles and sample data.
Usage: python manage.py initialize_data
"""
from django.core.management.base import BaseCommand
from apps.users.models import Role, User
from apps.users.services import UserService
from apps.records.models import FinancialRecord
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize database with roles and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data initialization...'))
        
        # Initialize roles
        self.stdout.write('Initializing roles...')
        UserService.initialize_roles()
        self.stdout.write(self.style.SUCCESS('[OK] Roles initialized'))
        
        # Create sample users if they don't exist
        self.stdout.write('Creating sample users...')
        
        roles = {
            'viewer': Role.objects.get(name='viewer'),
            'analyst': Role.objects.get(name='analyst'),
            'admin': Role.objects.get(name='admin'),
        }
        
        sample_users = [
            {
                'name': 'Viewer User',
                'email': 'viewer@example.com',
                'password': 'viewer123',
                'role': 'viewer',
            },
            {
                'name': 'Analyst User',
                'email': 'analyst@example.com',
                'password': 'analyst123',
                'role': 'analyst',
            },
            {
                'name': 'Admin User',
                'email': 'admin@example.com',
                'password': 'admin123',
                'role': 'admin',
            },
        ]
        
        created_users = {}
        for user_data in sample_users:
            if not User.objects.filter(email=user_data['email']).exists():
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    role=roles[user_data['role']],
                    status='active'
                )
                user.set_password(user_data['password'])
                user.save()
                created_users[user_data['role']] = user
                self.stdout.write(f"  [OK] Created {user_data['name']} ({user_data['email']})")
            else:
                created_users[user_data['role']] = User.objects.get(email=user_data['email'])
        
        self.stdout.write(self.style.SUCCESS('[OK] Users created'))
        
        # Create sample financial records
        if created_users.get('analyst'):
            self.stdout.write('Creating sample financial records...')
            analyst_user = created_users['analyst']
            
            # Check if records already exist
            if not FinancialRecord.objects.filter(user=analyst_user).exists():
                today = datetime.now().date()
                
                sample_records = [
                    {
                        'amount': Decimal('5000'),
                        'type': 'income',
                        'category': 'salary',
                        'date': today,
                        'description': 'Monthly salary',
                    },
                    {
                        'amount': Decimal('1200'),
                        'type': 'expense',
                        'category': 'utilities',
                        'date': today - timedelta(days=1),
                        'description': 'Electricity and water bills',
                    },
                    {
                        'amount': Decimal('500'),
                        'type': 'expense',
                        'category': 'grocery',
                        'date': today - timedelta(days=2),
                        'description': 'Weekly groceries',
                    },
                    {
                        'amount': Decimal('3000'),
                        'type': 'income',
                        'category': 'freelance',
                        'date': today - timedelta(days=3),
                        'description': 'Freelance project payment',
                    },
                    {
                        'amount': Decimal('200'),
                        'type': 'expense',
                        'category': 'entertainment',
                        'date': today - timedelta(days=4),
                        'description': 'Movie and dinner',
                    },
                    {
                        'amount': Decimal('1500'),
                        'type': 'expense',
                        'category': 'transport',
                        'date': today - timedelta(days=5),
                        'description': 'Car maintenance and fuel',
                    },
                ]
                
                for record_data in sample_records:
                    FinancialRecord.objects.create(
                        user=analyst_user,
                        **record_data
                    )
                    self.stdout.write(f"  [OK] Created {record_data['type']} record: {record_data['category']}")
                
                self.stdout.write(self.style.SUCCESS('[OK] Sample records created'))
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Data initialization completed successfully!'))
        self.stdout.write(self.style.WARNING('\nYou can now login with:'))
        self.stdout.write('  Viewer: viewer@example.com / viewer123')
        self.stdout.write('  Analyst: analyst@example.com / analyst123')
        self.stdout.write('  Admin: admin@example.com / admin123')
