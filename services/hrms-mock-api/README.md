# HRMS Mock API

Mock HRMS backend providing authentication, leave management, attendance tracking, and payroll APIs with realistic mock data.

## Owner
**palak.s@amazatic.com**

## Tech Stack
- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication

## Features

- 40+ REST API endpoints
- JWT authentication
- Mock data for 5 employees × 1 month
- SQLite database

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Generate Mock Data
```bash
# python scripts/seed_data.py
python scripts/init_mock_data.py
```

### 5. Run the Service
```bash
uvicorn api.main:app --reload --port 8001
```

## API Endpoints

### Authentication (5 endpoints)
- `POST /api/v1/auth/login` - Employee login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user profile
- `GET /api/v1/auth/verify` - Verify JWT token

### Leave Management (9 endpoints)
- `GET /api/v1/leave/balance` - Get leave balance
- `GET /api/v1/leave/balance/types` - Get balance by leave type
- `GET /api/v1/leave/requests` - List leave requests
- `GET /api/v1/leave/requests/{id}` - Get leave request details
- `POST /api/v1/leave/requests` - Apply for leave
- `PUT /api/v1/leave/requests/{id}` - Update leave request
- `DELETE /api/v1/leave/requests/{id}` - Cancel leave request
- `GET /api/v1/leave/types` - Get available leave types
- `GET /api/v1/leave/history` - Get leave history

### Attendance (8 endpoints)
- `GET /api/v1/attendance/today` - Get today's attendance
- `GET /api/v1/attendance/records` - List attendance records
- `POST /api/v1/attendance/checkin` - Mark check-in
- `POST /api/v1/attendance/checkout` - Mark check-out
- `PUT /api/v1/attendance/update` - Update attendance record
- `GET /api/v1/attendance/summary` - Monthly/yearly summary
- `GET /api/v1/attendance/status` - Current attendance status
- `GET /api/v1/attendance/report` - Generate attendance report

### Payroll (7 endpoints)
- `GET /api/v1/payroll/current` - Current month payroll
- `GET /api/v1/payroll/slips` - List salary slips
- `GET /api/v1/payroll/slips/{id}` - Get salary slip details
- `GET /api/v1/payroll/slips/{id}/pdf` - Download salary slip PDF
- `GET /api/v1/payroll/ytd` - Year-to-date earnings
- `GET /api/v1/payroll/tax-summary` - Tax summary
- `GET /api/v1/payroll/breakdown` - Salary breakdown details

### Employees (4 endpoints)
- `GET /api/v1/employees/profile` - Get employee profile
- `PUT /api/v1/employees/profile` - Update employee profile
- `GET /api/v1/employees/team` - Get team members
- `GET /api/v1/employees/{id}` - Get employee by ID

### System (2 endpoints)
- `GET /api/v1/health` - Health check
- `GET /api/v1/system/stats` - System statistics

## Mock Data

### Employees
1. manish.w@amazatic.com - Engineering Manager
2. priyanka.c@amazatic.com - Senior Backend Developer
3. palak.s@amazatic.com - Backend Developer
4. rohit.g@amazatic.com - Frontend Developer
5. manik.l@amazatic.com - DevOps Engineer

### Default Passwords
All employees: `password123`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

## Project Structure

```
hrms-mock-api/
├── api/
│   ├── main.py                      # FastAPI app
│   ├── routes/
│   │   ├── auth.py                  # Auth endpoints
│   │   ├── leave.py                 # Leave endpoints
│   │   ├── attendance.py            # Attendance endpoints
│   │   ├── payroll.py               # Payroll endpoints
│   │   └── employees.py             # Employee endpoints
│   └── middleware/
│       └── auth_middleware.py       # Auth middleware
├── models/
│   ├── employee.py                  # Employee model
│   ├── leave.py                     # Leave models
│   ├── attendance.py                # Attendance model
│   └── payroll.py                   # Payroll model
├── services/
│   ├── auth_service.py              # Auth service
│   ├── leave_service.py             # Leave service
│   ├── attendance_service.py        # Attendance service
│   └── payroll_service.py           # Payroll service
├── utils/
│   ├── jwt_utils.py                 # JWT utilities
│   └── config.py                    # Configuration
├── scripts/
│   ├── seed_data.py                 # Seed database
│   └── generate_mock_data.py        # Generate mock data
├── data/                            # Database files
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Documentation

API documentation available at: http://localhost:8001/docs
