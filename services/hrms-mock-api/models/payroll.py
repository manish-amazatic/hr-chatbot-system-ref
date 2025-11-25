"""
Payroll Record Model
"""
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class PayrollRecord(Base):
    """
    Payroll Record Model

    Stores monthly payroll records including:
    - Salary components
    - Deductions
    - Net pay
    - Payment status
    """
    __tablename__ = "payroll_records"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to employee
    employee_id = Column(String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    # Period
    month = Column(Integer, nullable=False, index=True)  # 1-12
    year = Column(Integer, nullable=False, index=True)

    # Salary components (all amounts in employee's currency)
    base_salary = Column(Numeric(10, 2), nullable=False)
    allowances = Column(JSON, nullable=True, default=dict)  # {"HRA": 5000, "Transport": 2000, etc.}
    gross_salary = Column(Numeric(10, 2), nullable=False)

    # Deductions
    deductions = Column(JSON, nullable=True, default=dict)  # {"Tax": 3000, "PF": 2000, etc.}
    total_deductions = Column(Numeric(10, 2), nullable=False, default=0)

    # Net pay
    net_salary = Column(Numeric(10, 2), nullable=False)

    # Payment details
    payment_date = Column(Date, nullable=True)
    payment_status = Column(String(20), nullable=False, default="Pending")  # Pending, Processed, Paid
    payment_method = Column(String(50), nullable=True)  # Bank Transfer, Cheque, etc.

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="payroll_records")

    def __repr__(self):
        return f"<PayrollRecord(id={self.id}, employee_id={self.employee_id}, period={self.month}/{self.year}, status={self.payment_status})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "month": self.month,
            "year": self.year,
            "base_salary": float(self.base_salary) if self.base_salary else None,
            "allowances": self.allowances,
            "gross_salary": float(self.gross_salary) if self.gross_salary else None,
            "deductions": self.deductions,
            "total_deductions": float(self.total_deductions) if self.total_deductions else None,
            "net_salary": float(self.net_salary) if self.net_salary else None,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
