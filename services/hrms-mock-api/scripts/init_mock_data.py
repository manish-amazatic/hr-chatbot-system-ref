"""
Initialize Mock Data for HRMS Database

Populates the database with:
- 5 employees
- Leave balances (Annual, Sick, Casual)
- Leave requests (various statuses)
- Attendance records (1 month)
- Payroll records (1 month)
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta, time
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.base import SessionLocal, init_db
from models import Employee, LeaveBalance, LeaveRequest, AttendanceRecord, PayrollRecord


def clear_database(db):
    """Clear all existing data"""
    print("Clearing existing data...")
    db.query(PayrollRecord).delete()
    db.query(AttendanceRecord).delete()
    db.query(LeaveRequest).delete()
    db.query(LeaveBalance).delete()
    db.query(Employee).delete()
    db.commit()
    print("✓ Database cleared")


def create_employees(db):
    """Create 5 mock employees"""
    print("\nCreating employees...")

    employees_data = [
        {
            "id": "EMP001",
            "first_name": "Manish",
            "last_name": "Wadhwani",
            "email": "manish.w@amazatic.com",
            "phone": "+91-9876543210",
            "date_of_birth": date(1985, 6, 15),
            "department": "Engineering",
            "designation": "Engineering Manager",
            "joining_date": date(2018, 1, 15),
            "employment_type": "Full-time",
            "manager_id": None,
            "base_salary": Decimal("120000.00"),
            "currency": "INR"
        },
        {
            "id": "EMP002",
            "first_name": "Priyanka",
            "last_name": "Sharma",
            "email": "priyanka.s@amazatic.com",
            "phone": "+91-9876543211",
            "date_of_birth": date(1992, 3, 22),
            "department": "Engineering",
            "designation": "Senior Software Engineer",
            "joining_date": date(2020, 3, 10),
            "employment_type": "Full-time",
            "manager_id": "EMP001",
            "base_salary": Decimal("80000.00"),
            "currency": "INR"
        },
        {
            "id": "EMP003",
            "first_name": "Rohit",
            "last_name": "Kumar",
            "email": "rohit.k@amazatic.com",
            "phone": "+91-9876543212",
            "date_of_birth": date(1994, 8, 10),
            "department": "Engineering",
            "designation": "Frontend Developer",
            "joining_date": date(2021, 6, 1),
            "employment_type": "Full-time",
            "manager_id": "EMP001",
            "base_salary": Decimal("65000.00"),
            "currency": "INR"
        },
        {
            "id": "EMP004",
            "first_name": "Palak",
            "last_name": "Verma",
            "email": "palak.v@amazatic.com",
            "phone": "+91-9876543213",
            "date_of_birth": date(1993, 11, 5),
            "department": "Engineering",
            "designation": "Backend Developer",
            "joining_date": date(2021, 2, 15),
            "employment_type": "Full-time",
            "manager_id": "EMP001",
            "base_salary": Decimal("70000.00"),
            "currency": "INR"
        },
        {
            "id": "EMP005",
            "first_name": "Shubham",
            "last_name": "Patel",
            "email": "shubham.p@amazatic.com",
            "phone": "+91-9876543214",
            "date_of_birth": date(1995, 2, 18),
            "department": "Engineering",
            "designation": "Software Engineer",
            "joining_date": date(2022, 8, 1),
            "employment_type": "Full-time",
            "manager_id": "EMP001",
            "base_salary": Decimal("55000.00"),
            "currency": "INR"
        }
    ]

    employees = []
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.add(employee)
        employees.append(employee)

    db.commit()
    print(f"✓ Created {len(employees)} employees")
    return employees


def create_leave_balances(db, employees):
    """Create leave balances for all employees"""
    print("\nCreating leave balances...")

    current_year = datetime.now().year
    leave_types = [
        {"type": "Annual", "total": 20},
        {"type": "Sick", "total": 12},
        {"type": "Casual", "total": 10}
    ]

    count = 0
    for employee in employees:
        for leave_type in leave_types:
            # Vary used days based on employee
            used_days = hash(employee.id + leave_type["type"]) % 5  # 0-4 days used

            balance = LeaveBalance(
                employee_id=employee.id,
                leave_type=leave_type["type"],
                total_days=leave_type["total"],
                used_days=used_days,
                available_days=leave_type["total"] - used_days,
                year=current_year
            )
            db.add(balance)
            count += 1

    db.commit()
    print(f"✓ Created {count} leave balance records")


def create_leave_requests(db, employees):
    """Create leave requests with various statuses"""
    print("\nCreating leave requests...")

    requests_data = [
        # Approved requests
        {
            "employee_id": "EMP002",
            "leave_type": "Annual",
            "start_date": date(2024, 11, 10),
            "end_date": date(2024, 11, 12),
            "days_count": 3,
            "reason": "Family vacation",
            "status": "Approved",
            "approved_by": "EMP001",
            "approval_date": datetime(2024, 11, 5, 10, 30)
        },
        {
            "employee_id": "EMP003",
            "leave_type": "Sick",
            "start_date": date(2024, 11, 18),
            "end_date": date(2024, 11, 18),
            "days_count": 1,
            "reason": "Medical appointment",
            "status": "Approved",
            "approved_by": "EMP001",
            "approval_date": datetime(2024, 11, 17, 14, 0)
        },
        # Pending requests
        {
            "employee_id": "EMP004",
            "leave_type": "Annual",
            "start_date": date(2024, 12, 20),
            "end_date": date(2024, 12, 24),
            "days_count": 5,
            "reason": "Year-end holidays",
            "status": "Pending",
            "approved_by": None,
            "approval_date": None
        },
        {
            "employee_id": "EMP005",
            "leave_type": "Casual",
            "start_date": date(2024, 11, 28),
            "end_date": date(2024, 11, 29),
            "days_count": 2,
            "reason": "Personal work",
            "status": "Pending",
            "approved_by": None,
            "approval_date": None
        },
        # Rejected request
        {
            "employee_id": "EMP003",
            "leave_type": "Annual",
            "start_date": date(2024, 11, 25),
            "end_date": date(2024, 11, 29),
            "days_count": 5,
            "reason": "Extended weekend",
            "status": "Rejected",
            "approved_by": "EMP001",
            "approval_date": datetime(2024, 11, 15, 16, 0),
            "rejection_reason": "Team needs coverage during this period"
        }
    ]

    for req_data in requests_data:
        request = LeaveRequest(**req_data)
        db.add(request)

    db.commit()
    print(f"✓ Created {len(requests_data)} leave requests")


def create_attendance_records(db, employees):
    """Create attendance records for the last 30 days"""
    print("\nCreating attendance records...")

    today = date.today()
    start_date = today - timedelta(days=30)

    count = 0
    for employee in employees:
        current_date = start_date

        while current_date <= today:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                # Most days are present
                if hash(f"{employee.id}{current_date}") % 10 < 8:  # 80% attendance
                    status = "Present"
                    check_in = time(9, hash(f"{employee.id}{current_date}a") % 30)
                    check_out = time(18, hash(f"{employee.id}{current_date}b") % 30)
                    work_hours = "9.0"
                else:
                    status = "Absent"
                    check_in = None
                    check_out = None
                    work_hours = None

                record = AttendanceRecord(
                    employee_id=employee.id,
                    date=current_date,
                    check_in_time=check_in,
                    check_out_time=check_out,
                    work_hours=work_hours,
                    status=status
                )
                db.add(record)
                count += 1

            current_date += timedelta(days=1)

    db.commit()
    print(f"✓ Created {count} attendance records")


def create_payroll_records(db, employees):
    """Create payroll records for the current month"""
    print("\nCreating payroll records...")

    current_month = datetime.now().month
    current_year = datetime.now().year

    for employee in employees:
        base_salary = employee.base_salary

        # Calculate components
        hra = base_salary * Decimal("0.30")  # 30% HRA
        transport = Decimal("2000.00")
        meal = Decimal("1500.00")
        allowances = {
            "HRA": float(hra),
            "Transport Allowance": float(transport),
            "Meal Allowance": float(meal)
        }

        gross_salary = base_salary + hra + transport + meal

        # Deductions
        tax = gross_salary * Decimal("0.10")  # 10% tax
        pf = base_salary * Decimal("0.12")  # 12% PF
        deductions = {
            "Income Tax": float(tax),
            "Provident Fund": float(pf)
        }

        total_deductions = tax + pf
        net_salary = gross_salary - total_deductions

        payroll = PayrollRecord(
            employee_id=employee.id,
            month=current_month,
            year=current_year,
            base_salary=base_salary,
            allowances=allowances,
            gross_salary=gross_salary,
            deductions=deductions,
            total_deductions=total_deductions,
            net_salary=net_salary,
            payment_date=date(current_year, current_month, 28),
            payment_status="Processed",
            payment_method="Bank Transfer"
        )
        db.add(payroll)

    db.commit()
    print(f"✓ Created {len(employees)} payroll records")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("HRMS Mock Data Initialization")
    print("=" * 60)

    # Initialize database (create tables)
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized")

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)

        # Create mock data
        employees = create_employees(db)
        create_leave_balances(db, employees)
        create_leave_requests(db, employees)
        create_attendance_records(db, employees)
        create_payroll_records(db, employees)

        print("\n" + "=" * 60)
        print("✓ Mock data initialization completed successfully!")
        print("=" * 60)
        print("\nDatabase summary:")
        print(f"  - Employees: {db.query(Employee).count()}")
        print(f"  - Leave Balances: {db.query(LeaveBalance).count()}")
        print(f"  - Leave Requests: {db.query(LeaveRequest).count()}")
        print(f"  - Attendance Records: {db.query(AttendanceRecord).count()}")
        print(f"  - Payroll Records: {db.query(PayrollRecord).count()}")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
