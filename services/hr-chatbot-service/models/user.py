"""
User Model (cached from HRMS)
Optional: Store user information locally for faster access
"""
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime

from .base import Base


class User(Base):
    """
    User Model (Cache)

    Stores cached user information from HRMS API
    This is optional - mainly for faster lookups and offline capability
    """
    __tablename__ = "users"

    # Primary key (employee ID from HRMS)
    id = Column(String(10), primary_key=True)  # EMP001, EMP002, etc.

    # User details (from HRMS)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department": self.department,
            "designation": self.designation,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
