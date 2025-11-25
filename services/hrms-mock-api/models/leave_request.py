"""
Leave Request Model
"""
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class LeaveRequest(Base):
    """
    Leave Request Model

    Stores leave requests from employees including:
    - Request details
    - Leave type and dates
    - Status (Pending, Approved, Rejected)
    - Approval information
    """
    __tablename__ = "leave_requests"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to employee
    employee_id = Column(String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    # Leave details
    leave_type = Column(String(50), nullable=False)  # Annual, Sick, Casual, etc.
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    days_count = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="Pending", index=True)  # Pending, Approved, Rejected, Cancelled

    # Approval details
    approved_by = Column(String(10), nullable=True)  # Manager/HR who approved
    approval_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="leave_requests")

    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, employee_id={self.employee_id}, type={self.leave_type}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "leave_type": self.leave_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "days_count": self.days_count,
            "reason": self.reason,
            "status": self.status,
            "approved_by": self.approved_by,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
