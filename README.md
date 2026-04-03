"""
Finance Dashboard Backend - README
Complete backend system for Finance Data Processing and Access Control Dashboard
"""

# Finance Dashboard Backend

A production-ready Django REST API backend for a Finance Data Processing and Access Control Dashboard with role-based access control, JWT authentication, and comprehensive financial analytics.

## Features

### ✅ **Complete Implementation**
- **Role-Based Access Control (RBAC)** - Three roles: Viewer, Analyst, Admin
- **JWT Authentication** - Secure token-based authentication with bcrypt password hashing
- **User Management** - Create, update, delete users with role management
- **Financial Records CRUD** - Complete CRUD operations for financial transactions
- **Dashboard Analytics** - Comprehensive financial analytics and summaries
- **Input Validation** - Proper validation with meaningful error responses
- **Error Handling** - Global error handler with structured JSON responses
- **Soft Delete** - Preserve data integrity with soft delete functionality
- **Pagination** - Paginated list views for better performance
- **Logging** - Comprehensive logging system for debugging
- **Clean Architecture** - Separation of concerns: models, serializers, services, views

## Project Structure

```
finance_dashboard_backend/
├── config/                          # Django configuration
│   ├── settings.py                  # Project settings
│   ├── urls.py                      # Root URL configuration
│   ├── wsgi.py                      # WSGI configuration
│   └── __init__.py
├── apps/                            # Django applications
│   ├── users/                       # User management app
│   │   ├── models.py                # User and Role models
│   │   ├── views.py                 # Authentication and user endpoints
│   │   ├── serializers.py           # User serializers
│   │   ├── services.py              # User business logic
│   │   ├── urls.py                  # App URLs
│   │   ├── admin.py                 # Django admin config
│   │   └── management/commands/
│   │       └── initialize_data.py   # Initialize roles and sample data
│   ├── records/                     # Financial records app
│   │   ├── models.py                # FinancialRecord model
│   │   ├── views.py                 # Record endpoints
│   │   ├── serializers.py           # Record serializers
│   │   ├── services.py              # Record business logic
│   │   ├── urls.py                  # App URLs
│   │   └── admin.py                 # Django admin config
│   └── dashboard/                   # Dashboard analytics app
│       ├── views.py                 # Dashboard analytics endpoints
│       ├── serializers.py           # Dashboard serializers
│       └── urls.py                  # App URLs
├── middleware/                      # Custom middleware
│   ├── auth_middleware.py           # JWT authentication middleware
│   └── rbac_decorators.py           # RBAC decorators
├── utils/                           # Utility functions
│   ├── jwt_handler.py               # JWT token generation and verification
│   ├── password_handler.py          # Password hashing and verification
│   ├── response_formatter.py        # API response formatting
│   └── exception_handler.py         # Global exception handler
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download Project

```bash
cd finance_dashboard_backend
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example to actual .env file
cp .env.example .env

# Edit .env with your configuration
# For development, the defaults should work fine
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Initialize Database with Sample Data

```bash
python manage.py initialize_data
```

This command will:
- Create default roles (viewer, analyst, admin)
- Create sample users for testing each role
- Create sample financial records

### Step 7: Create Superuser (Optional - for Django Admin)

```bash
python manage.py createsuperuser
```

### Step 8: Start Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Authentication Endpoints

#### 1. Register New User
```
POST /api/auth/register/
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "role": 1,
    "status": "active"
}

Response: 201 Created
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": 1,
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 2. Login
```
POST /api/auth/login/
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "securepass123"
}

Response: 200 OK
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "analyst",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

#### 3. Verify Token
```
GET /api/auth/verify/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Token is valid",
    "data": {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "analyst",
        "status": "active"
    }
}
```

### User Management Endpoints (Admin Only)

#### 4. List Users
```
GET /api/auth/users/?role=analyst&status=active
Authorization: Bearer <admin_token>

Response: 200 OK
{
    "success": true,
    "message": "Operation successful",
    "data": [
        {
            "id": 1,
            "name": "Analyst User",
            "email": "analyst@example.com",
            "role": 1,
            "role_detail": {...},
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### 5. Get User Details
```
GET /api/auth/users/<user_id>/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Operation successful",
    "data": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": 1,
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 6. Update User
```
PATCH /api/auth/users/<user_id>/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "name": "Updated Name",
    "status": "inactive"
}

Response: 200 OK
{
    "success": true,
    "message": "User updated successfully",
    "data": {...}
}
```

#### 7. Delete User
```
DELETE /api/auth/users/<user_id>/
Authorization: Bearer <admin_token>

Response: 200 OK
{
    "success": true,
    "message": "User deleted successfully",
    "data": null
}
```

### Financial Records Endpoints

#### 8. Create Financial Record (Analyst/Admin)
```
POST /api/records/
Authorization: Bearer <token>
Content-Type: application/json

{
    "amount": 5000.50,
    "type": "income",
    "category": "salary",
    "date": "2024-01-15",
    "description": "Monthly salary payment"
}

Response: 201 Created
{
    "success": true,
    "message": "Record created successfully",
    "data": {
        "id": 1,
        "user": 1,
        "user_name": "John Doe",
        "amount": "5000.50",
        "type": "income",
        "category": "salary",
        "date": "2024-01-15",
        "description": "Monthly salary payment",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 9. List Financial Records
```
GET /api/records/?type=income&category=salary&date_from=2024-01-01&date_to=2024-01-31&search=salary
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Operation successful",
    "data": [
        {
            "id": 1,
            "user_name": "John Doe",
            "amount": "5000.50",
            "type": "income",
            "category": "salary",
            "date": "2024-01-15",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### 10. Get Record Details
```
GET /api/records/<record_id>/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Operation successful",
    "data": {
        "id": 1,
        "user": 1,
        "user_name": "John Doe",
        "amount": "5000.50",
        ...
    }
}
```

#### 11. Update Record
```
PATCH /api/records/<record_id>/
Authorization: Bearer <token>
Content-Type: application/json

{
    "amount": 5500.00,
    "description": "Updated salary amount"
}

Response: 200 OK
{
    "success": true,
    "message": "Record updated successfully",
    "data": {...}
}
```

#### 12. Delete Record
```
DELETE /api/records/<record_id>/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Record deleted successfully",
    "data": null
}
```

### Dashboard Analytics Endpoints

#### 13. Dashboard Summary
```
GET /api/dashboard/summary/?date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Dashboard summary",
    "data": {
        "total_income": "8000.50",
        "total_expense": "2500.00",
        "net_balance": "5500.50",
        "income_count": 2,
        "expense_count": 5,
        "period": "2024-01-01 to 2024-01-31"
    }
}
```

#### 14. Category Breakdown
```
GET /api/dashboard/category-breakdown/?type=expense
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Category breakdown",
    "data": [
        {
            "category": "utilities",
            "total": "1200.00",
            "count": 3
        },
        {
            "category": "grocery",
            "total": "800.00",
            "count": 2
        }
    ]
}
```

#### 15. Monthly Trends
```
GET /api/dashboard/monthly-trends/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Monthly trends",
    "data": [
        {
            "month": "2024-01-01",
            "type": "income",
            "total": "8000.50",
            "count": 2
        },
        {
            "month": "2024-01-01",
            "type": "expense",
            "total": "2500.00",
            "count": 5
        }
    ]
}
```

#### 16. Recent Activity
```
GET /api/dashboard/recent-activity/?limit=10
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Recent activity",
    "data": [
        {
            "id": 1,
            "user_name": "John Doe",
            "type": "income",
            "category": "salary",
            "amount": "5000.50",
            "date": "2024-01-15",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### 17. Comprehensive Statistics
```
GET /api/dashboard/stats/
Authorization: Bearer <token>

Response: 200 OK
{
    "success": true,
    "message": "Comprehensive dashboard statistics",
    "data": {
        "summary": {
            "total_income": "8000.50",
            "total_expense": "2500.00",
            "net_balance": "5500.50",
            "income_count": 2,
            "expense_count": 5
        },
        "category_breakdown": [...],
        "recent_activity": [...]
    }
}
```

## Role-Based Access Control (RBAC)

### Viewer Role
- ✅ View dashboard summary
- ❌ Cannot create/update/delete records
- ❌ Cannot view detailed records
- ❌ Cannot manage users

### Analyst Role
- ✅ View dashboard summary
- ✅ View records (own only)
- ✅ Create records
- ✅ Update records (own only)
- ✅ Cannot delete records
- ❌ Cannot manage users

### Admin Role
- ✅ All Analyst permissions
- ✅ View records (all users)
- ✅ Delete records (all users)
- ✅ Manage users (CRUD)
- ✅ View other users' dashboards

## Authentication

All endpoints except login and register require the `Authorization` header with JWT token:

```
Authorization: Bearer <jwt_token>
```

### Token Format
JWT tokens are valid for 24 hours (configurable in .env).

## Error Handling

All errors follow a consistent format:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["error message"]
    }
}
```

### Common Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied (insufficient permissions)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Validation Rules

### User Validation
- Email must be unique and valid format
- Password must be at least 8 characters
- Name must not be empty

### Financial Record Validation
- Amount must be positive (> 0)
- Type must be 'income' or 'expense'
- Category must be from predefined list
- Date must be valid date format (YYYY-MM-DD)

## Database Models

### User Model
```python
- id: Integer (Primary Key)
- name: String (255)
- email: String (255) - Unique
- password: String (255) - Hashed
- role: ForeignKey→Role
- status: Choice (active, inactive, suspended)
- created_at: DateTime
- updated_at: DateTime
- is_deleted: Boolean
```

### Role Model
```python
- id: Integer (Primary Key)
- name: String (50) - Unique
- description: Text
- permissions: JSON
- created_at: DateTime
- updated_at: DateTime
```

### FinancialRecord Model
```python
- id: Integer (Primary Key)
- user: ForeignKey→User
- amount: Decimal (12, 2)
- type: Choice (income, expense)
- category: Choice (predefined)
- date: Date
- description: Text
- created_at: DateTime
- updated_at: DateTime
- is_deleted: Boolean
```

## Configuration

### Environment Variables (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

For MySQL, change DB_ENGINE and add MySQL credentials.

## Testing

### Sample Curl Requests

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "role": 2,
    "status": "active"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Create Record (Replace TOKEN with actual JWT)
curl -X POST http://localhost:8000/api/records/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.50,
    "type": "income",
    "category": "salary",
    "date": "2024-01-15",
    "description": "Test income"
  }'

# Get Dashboard Summary
curl -X GET http://localhost:8000/api/dashboard/summary/ \
  -H "Authorization: Bearer TOKEN"
```

## Logging

Logs are written to:
- `logs/app.log` - File logging
- Console output during development

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Deployment Considerations

### For Production:
1. Set DEBUG=False in .env
2. Change SECRET_KEY to a strong random value
3. Use MySQL instead of SQLite
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Set up HTTPS/SSL
6. Configure CORS properly for your frontend domain
7. Use environment-specific settings
8. Set up proper database backups
9. Monitor logs and errors
10. Use strong JWT secret key

### Docker Deployment (Optional)
```dockerfile
FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Clean Architecture Benefits

✅ **Separation of Concerns** - Models, Views, Services clearly separated
✅ **Reusability** - Services can be reused across different views
✅ **Testability** - Each layer can be tested independently
✅ **Maintainability** - Easy to understand and modify code
✅ **Scalability** - Easy to add new features without breaking existing ones

## Best Practices Implemented

✅ Meaningful variable names
✅ Comprehensive docstrings
✅ Proper error handling
✅ Input validation
✅ Security (password hashing, JWT, RBAC)
✅ Logging
✅ Pagination
✅ Soft delete for data integrity
✅ Consistent API response format
✅ Status codes usage
✅ Clean code structure
✅ DRY principle
✅ Modular design

## Future Enhancements

- [ ] GraphQL API support
- [ ] Two-factor authentication
- [ ] Email notifications
- [ ] Data export (CSV/PDF)
- [ ] Advanced filtering and search
- [ ] Recurring transactions
- [ ] Budget management
- [ ] Multi-currency support
- [ ] API rate limiting
- [ ] Audit logging
- [ ] WebSocket for real-time updates

## Troubleshooting

### Migration Issues
```bash
# Reset migrations (development only)
python manage.py migrate --fake users zero
python manage.py migrate
```

### Port Already in Use
```bash
# Run on different port
python manage.py runserver 8001
```

### Database Issues
```bash
# Delete SQLite and start fresh
rm db.sqlite3
python manage.py migrate
python manage.py initialize_data
```

## License

This project is provided as-is for educational and assignment purposes.

## Support

For issues or questions, please check the code comments and documentation.

---

**Happy Coding! 🚀**
