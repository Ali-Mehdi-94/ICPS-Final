# ICPS - Student Registration & Course Management System

A comprehensive Django REST API system for managing student registrations, course programs, payments, and team incentives. Built with Django 5.2.5 and Django REST Framework.

## Features

- **Role-Based Access Control**: Three user roles (Sales, Operations, CEO) with distinct permissions
- **Student Registration Management**: Complete registration workflow with course provider, field, and level tracking
- **Payment Management**: Automated payment plan generation with installment tracking
- **Task Management**: Unit-based task tracking with deadlines and completion status
- **Incentive System**: Automated incentive tracking for Sales and Operations teams
- **Dashboard Analytics**: Role-specific dashboards with KPIs and metrics
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Configured for frontend integration

## Technology Stack

- **Backend**: Django 5.2.5
- **API**: Django REST Framework 3.16.1
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **CORS**: django-cors-headers 4.7.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Date Utilities**: python-dateutil 2.9.0

## Project Structure

```
ICPS/
├── ICPS/              # Main project directory
│   ├── settings.py    # Django settings
│   ├── urls.py        # Root URL configuration
│   ├── wsgi.py        # WSGI configuration
│   └── asgi.py        # ASGI configuration
├── core/              # Main application
│   ├── models.py      # Database models
│   ├── views.py       # API views and endpoints
│   ├── serializers.py # DRF serializers
│   ├── urls.py        # App URL routing
│   ├── permissions.py # Custom permissions
│   ├── services.py    # Business logic services
│   ├── signals.py     # Django signals
│   ├── dashboard.py   # Dashboard data functions
│   ├── utils.py       # Utility functions
│   ├── notifications.py # Email notifications
│   └── admin.py       # Django admin configuration
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
└── README.md         # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ICPS
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure the following variables:
   - `SECRET_KEY`: Generate a new secret key (see below)
   - `DEBUG`: Set to `False` for production
   - `ALLOWED_HOSTS`: Add your domain(s)
   - Configure email settings if needed

**Generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 6: Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Documentation

### Authentication

All API endpoints (except authentication) require JWT authentication.

#### Obtain Token
```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

#### Using Tokens
Include the access token in the Authorization header:
```http
Authorization: Bearer <your_access_token>
```

### API Endpoints

#### User Management

- `GET /api/users/` - List all users (CEO only)
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user
- `GET /api/me/` - Get current user info

#### Students

- `GET /api/students/` - List students (filtered by role)
- `POST /api/students/` - Create student
- `GET /api/students/{id}/` - Get student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student

#### Registrations

- `GET /api/registrations/` - List registrations (filtered by role)
- `POST /api/registrations/` - Create registration
- `GET /api/registrations/{id}/` - Get registration details
- `PUT /api/registrations/{id}/` - Update registration
- `DELETE /api/registrations/{id}/` - Delete registration

**Registration Response includes:**
- Student information
- Course details (provider, field, level)
- Progress metrics (units_total, units_done, units_overdue)
- Payment metrics (payments_total, payments_paid, payments_overdue)
- Task timeline
- Payment installments

#### Course Configuration

- `GET /api/providers/` - List course providers
- `GET /api/fields/?provider={id}` - List fields (optionally filtered by provider)
- `GET /api/levels/?provider={id}&field={id}` - List levels

#### Dashboard Endpoints

**CEO Dashboard:**
```http
GET /api/dashboard/ceo/summary/
```
Returns: Total students, registrations, revenue metrics, overdue items

**Sales Dashboard:**
```http
GET /api/dashboard/sales/summary/
```
Returns: Personal sales metrics, revenue, payment status, incentives

**Operations Dashboard:**
```http
GET /api/dashboard/ops/summary/
```
Returns: Task metrics, unit progress, upcoming deadlines, incentives

#### Actions

**Complete Unit Task:**
```http
POST /api/units/{id}/complete/
```
Marks a unit task as completed. Ops can only complete their own tasks; CEO can complete any task.

**Mark Payment Paid:**
```http
POST /api/installments/{id}/pay/
```
Marks a payment installment as paid. Available to Sales and CEO roles.

### Role-Based Access

#### CEO
- Full access to all data
- Can view all registrations, students, and users
- Can complete any task
- Can mark any payment as paid

#### Sales
- Can view only their own registrations (where `registered_by` = user)
- Can create new registrations
- Can mark payments as paid
- Cannot complete tasks

#### Operations (Ops)
- Can view only assigned registrations (where `assigned_to` = user)
- Can complete their own tasks only
- Cannot create registrations or mark payments

## Models Overview

### Core Models

- **CustomUser**: Extended user model with role field (Sales, Ops, CEO)
- **Student**: Student information (name, email, phone, DOB)
- **Registration**: Links student to course program with payment and task tracking
- **CourseProvider**: Course providers (OTHM, ProQual, etc.)
- **Field**: Course fields (OHS, Business, IT, etc.)
- **Level**: Course levels (3, 4, 5, 6, 7)
- **ProgramTemplate**: Reusable program definitions
- **UnitTask**: Task timeline items (Forms, Assignments, Assessment/Buffer)
- **PaymentPlan**: Payment plan for a registration
- **PaymentInstallment**: Individual payment installments
- **SalesIncentive**: Sales team incentive tracking
- **OperationsIncentive**: Operations team incentive tracking

## Business Logic

### Registration Workflow

1. **Create Registration**: Sales team creates a registration
2. **Auto-Assignment**: System automatically assigns to next Ops user (round-robin)
3. **Template Application**: If program template exists, applies defaults (unit count, deadline)
4. **Task Generation**: Automatically generates UnitTask timeline based on template
5. **Payment Plan**: If total_fee provided, generates payment installments

### Provider-Specific Logic

- **OTHM**: 3-4 months duration, straight unit assignments
- **ProQual**: 6-10 months duration, includes 8-week forms phase before units

### Incentive System

- **Sales Incentive**: Automatically marked as paid when all payment installments are completed
- **Operations Incentive**: Automatically marked as paid when all assignment units are completed before deadline

## Development

### Running Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser

```bash
python manage.py createsuperuser
```

### Django Admin

Access the admin panel at `http://localhost:8000/admin/` after creating a superuser.

### Management Commands

- `python manage.py seed_programs` - Seed program templates
- `python manage.py notify_daily` - Send daily notifications (if configured)

## Production Deployment

### Security Checklist

1. ✅ Set `DEBUG=False` in environment variables
2. ✅ Set a strong `SECRET_KEY` (never commit to version control)
3. ✅ Configure `ALLOWED_HOSTS` with your domain(s)
4. ✅ Use PostgreSQL or another production database
5. ✅ Configure proper email backend (SMTP)
6. ✅ Use HTTPS in production
7. ✅ Set up proper logging
8. ✅ Review CORS settings for production

### Environment Variables for Production

```env
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Migration

For PostgreSQL:
1. Install PostgreSQL adapter: `pip install psycopg2-binary`
2. Update `DATABASES` in `settings.py` to use PostgreSQL
3. Run migrations: `python manage.py migrate`

### Static Files

```bash
python manage.py collectstatic
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core
```

## Logging

Logs are configured in `settings.py` and will be written to:
- Console (all environments)
- File: `logs/django.log` (if logs directory exists)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Run migrations: `python manage.py migrate`
3. **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` in settings
4. **Authentication Errors**: Verify JWT token is included in Authorization header

### Getting Help

- Check Django documentation: https://docs.djangoproject.com/
- Check DRF documentation: https://www.django-rest-framework.org/

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

[Specify your license here]

## Changelog

### Version 1.0.0
- Initial release
- Role-based access control
- Student registration management
- Payment and task tracking
- Dashboard analytics
- Incentive system

