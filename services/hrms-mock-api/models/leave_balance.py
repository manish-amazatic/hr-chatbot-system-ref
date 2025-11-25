"""
Leave Balance Model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class LeaveBalance(Base):
    """
    Leave Balance Model

    Stores leave balance information for employees including:
    - Leave type (Annual, Sick, Casual, etc.)
    - Total allocated days
    - Used days
    - Available days
    """
    __tablename__ = "leave_balances"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to employee
    employee_id = Column(String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    # Leave type
    leave_type = Column(String(50), nullable=False)  # Annual, Sick, Casual, Maternity, Paternity, etc.

    # Balance details
    total_days = Column(Integer, nullable=False, default=0)
    used_days = Column(Integer, nullable=False, default=0)
    available_days = Column(Integer, nullable=False, default=0)

    # Year (for tracking annual balances)
    year = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="leave_balances")

    def __repr__(self):
        return f"<LeaveBalance(id={self.id}, employee_id={self.employee_id}, type={self.leave_type}, available={self.available_days})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "leave_type": self.leave_type,
            "total_days": self.total_days,
            "used_days": self.used_days,
            "available_days": self.available_days,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
