"""
Attendance Service

Handles all attendance-related business logic including:
- Attendance record management
- Check-in/check-out tracking
- Attendance summaries and reports
"""
from sqlalchemy import select, and_, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, time
from typing import List, Optional, Dict
import uuid

from models.attendance import AttendanceRecord
from models.employee import Employee


class AttendanceService:
    """Service for managing attendance operations"""

    @staticmethod
    async def mark_attendance(
        db: AsyncSession,
        employee_id: str,
        attendance_date: date,
        check_in_time: Optional[time] = None,
        check_out_time: Optional[time] = None,
        status: str = "Present",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Mark attendance for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            attendance_date: Attendance date
            check_in_time: Check-in time
            check_out_time: Check-out time
            status: Attendance status
            notes: Additional notes

        Returns:
            Created attendance record
        """
        # Check if attendance already exists for this date
        existing_query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == attendance_date
            )
        )
        result = await db.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Attendance already marked for {attendance_date}")

        # Calculate work hours if both times provided
        work_hours = None
        if check_in_time and check_out_time:
            # Convert to datetime for calculation
            check_in_dt = datetime.combine(attendance_date, check_in_time)
            check_out_dt = datetime.combine(attendance_date, check_out_time)
            hours_diff = (check_out_dt - check_in_dt).total_seconds() / 3600
            work_hours = f"{hours_diff:.1f}"

        # Create attendance record
        attendance = AttendanceRecord(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            date=attendance_date,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            work_hours=work_hours,
            status=status,
            notes=notes
        )

        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)

        return attendance.to_dict()

    @staticmethod
    async def check_in(
        db: AsyncSession,
        employee_id: str,
        check_in_time: Optional[time] = None
    ) -> Dict:
        """
        Mark check-in for today

        Args:
            db: Database session
            employee_id: Employee ID
            check_in_time: Check-in time (defaults to current time)

        Returns:
            Updated attendance record
        """
        today = date.today()
        if check_in_time is None:
            check_in_time = datetime.now().time()

        # Check if already checked in
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == today
            )
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()

        if attendance:
            if attendance.check_in_time:
                raise ValueError("Already checked in for today")
            attendance.check_in_time = check_in_time
            attendance.status = "Present"
        else:
            attendance = AttendanceRecord(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                date=today,
                check_in_time=check_in_time,
                status="Present"
            )
            db.add(attendance)

        await db.commit()
        await db.refresh(attendance)

        return attendance.to_dict()

    @staticmethod
    async def check_out(
        db: AsyncSession,
        employee_id: str,
        check_out_time: Optional[time] = None
    ) -> Dict:
        """
        Mark check-out for today

        Args:
            db: Database session
            employee_id: Employee ID
            check_out_time: Check-out time (defaults to current time)

        Returns:
            Updated attendance record
        """
        today = date.today()
        if check_out_time is None:
            check_out_time = datetime.now().time()

        # Get today's attendance
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == today
            )
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()

        if not attendance:
            raise ValueError("No check-in record found for today")

        if not attendance.check_in_time:
            raise ValueError("Must check in before checking out")

        if attendance.check_out_time:
            raise ValueError("Already checked out for today")

        # Update check-out time
        attendance.check_out_time = check_out_time

        # Calculate work hours
        check_in_dt = datetime.combine(today, attendance.check_in_time)
        check_out_dt = datetime.combine(today, check_out_time)
        hours_diff = (check_out_dt - check_in_dt).total_seconds() / 3600
        attendance.work_hours = f"{hours_diff:.1f}"
        attendance.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(attendance)

        return attendance.to_dict()

    @staticmethod
    async def get_attendance_records(
        db: AsyncSession,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get attendance records for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            start_date: Start date filter
            end_date: End date filter
            status: Status filter

        Returns:
            List of attendance records
        """
        conditions = [AttendanceRecord.employee_id == employee_id]

        if start_date:
            conditions.append(AttendanceRecord.date >= start_date)
        if end_date:
            conditions.append(AttendanceRecord.date <= end_date)
        if status:
            conditions.append(AttendanceRecord.status == status)

        query = select(AttendanceRecord).where(and_(*conditions)).order_by(AttendanceRecord.date.desc())
        result = await db.execute(query)
        records = result.scalars().all()

        return [record.to_dict() for record in records]

    @staticmethod
    async def get_attendance_by_date(
        db: AsyncSession,
        employee_id: str,
        attendance_date: date
    ) -> Optional[Dict]:
        """Get attendance record for a specific date"""
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == attendance_date
            )
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()

        return attendance.to_dict() if attendance else None

    @staticmethod
    async def get_monthly_summary(
        db: AsyncSession,
        employee_id: str,
        month: int,
        year: int
    ) -> Dict:
        """
        Get monthly attendance summary

        Args:
            db: Database session
            employee_id: Employee ID
            month: Month (1-12)
            year: Year

        Returns:
            Summary with counts and percentages
        """
        # Get all records for the month
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                extract('month', AttendanceRecord.date) == month,
                extract('year', AttendanceRecord.date) == year
            )
        )
        result = await db.execute(query)
        records = result.scalars().all()

        # Calculate summary
        total_days = len(records)
        present_count = sum(1 for r in records if r.status == "Present")
        absent_count = sum(1 for r in records if r.status == "Absent")
        leave_count = sum(1 for r in records if r.status == "Leave")
        half_day_count = sum(1 for r in records if r.status == "Half-day")

        # Calculate total work hours
        total_work_hours = 0.0
        for record in records:
            if record.work_hours:
                try:
                    total_work_hours += float(record.work_hours)
                except ValueError:
                    pass

        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_days": total_days,
            "present_days": present_count,
            "absent_days": absent_count,
            "leave_days": leave_count,
            "half_days": half_day_count,
            "total_work_hours": round(total_work_hours, 1),
            "attendance_percentage": round((present_count / total_days * 100), 2) if total_days > 0 else 0
        }

    @staticmethod
    async def update_attendance(
        db: AsyncSession,
        record_id: str,
        employee_id: str,
        check_in_time: Optional[time] = None,
        check_out_time: Optional[time] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Update an existing attendance record"""
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.id == record_id,
                AttendanceRecord.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()

        if not attendance:
            raise ValueError("Attendance record not found")

        # Update fields if provided
        if check_in_time is not None:
            attendance.check_in_time = check_in_time
        if check_out_time is not None:
            attendance.check_out_time = check_out_time
        if status is not None:
            attendance.status = status
        if notes is not None:
            attendance.notes = notes

        # Recalculate work hours if both times are present
        if attendance.check_in_time and attendance.check_out_time:
            check_in_dt = datetime.combine(attendance.date, attendance.check_in_time)
            check_out_dt = datetime.combine(attendance.date, attendance.check_out_time)
            hours_diff = (check_out_dt - check_in_dt).total_seconds() / 3600
            attendance.work_hours = f"{hours_diff:.1f}"

        attendance.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(attendance)

        return attendance.to_dict()

    @staticmethod
    async def delete_attendance(
        db: AsyncSession,
        record_id: str,
        employee_id: str
    ) -> bool:
        """Delete an attendance record"""
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.id == record_id,
                AttendanceRecord.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()

        if not attendance:
            raise ValueError("Attendance record not found")

        await db.delete(attendance)
        await db.commit()

        return True
