"""
Employee Model
"""
from sqlalchemy import Column, String, Date, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Employee(Base):
    """
    Employee Model

    Stores employee information including:
    - Personal details
    - Employment details
    - Contact information
    - Status
    """
    __tablename__ = "employees"

    # Primary key
    id = Column(String(10), primary_key=True)  # EMP001, EMP002, etc.

    # Personal details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    # Employment details
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    employment_type = Column(String(50), nullable=False, default="Full-time")  # Full-time, Part-time, Contract
    manager_id = Column(String(10), nullable=True)  # References another employee

    # Salary (stored for payroll calculations)
    base_salary = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leave_balances = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")
    payroll_records = relationship("PayrollRecord", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee(id={self.id}, email={self.email}, name={self.first_name} {self.last_name})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "department": self.department,
            "designation": self.designation,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "employment_type": self.employment_type,
            "manager_id": self.manager_id,
            "base_salary": float(self.base_salary) if self.base_salary else None,
            "currency": self.currency,
            "is_active": self.is_active
        }
