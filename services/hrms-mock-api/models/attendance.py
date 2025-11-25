"""
Attendance Record Model
"""
from sqlalchemy import Column, String, Date, Time, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class AttendanceRecord(Base):
    """
    Attendance Record Model

    Stores daily attendance records including:
    - Check-in and check-out times
    - Work hours
    - Status (Present, Absent, Half-day, etc.)
    - Notes
    """
    __tablename__ = "attendance_records"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to employee
    employee_id = Column(String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    # Date
    date = Column(Date, nullable=False, index=True)

    # Time tracking
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    work_hours = Column(String(10), nullable=True)  # "8.5", "4.0", etc.

    # Status
    status = Column(String(20), nullable=False, default="Present")  # Present, Absent, Half-day, Leave, Holiday

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

    def __repr__(self):
        return f"<AttendanceRecord(id={self.id}, employee_id={self.employee_id}, date={self.date}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "date": self.date.isoformat() if self.date else None,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "work_hours": self.work_hours,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
