"""
Agents for the HR Chatbot
Specialized agents for different HR tasks
"""

from .leave_agent import LeaveAgent
from .attendance_agent import AttendanceAgent
from .payroll_agent import PayrollAgent


__all__ = ["LeaveAgent", "AttendanceAgent", "PayrollAgent"]