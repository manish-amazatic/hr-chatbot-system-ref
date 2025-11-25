"""
Payroll Service

Handles all payroll-related business logic including:
- Payroll record management
- Salary calculations
- Payslip generation
- Payment tracking
"""
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import List, Optional, Dict
from decimal import Decimal
import uuid

from models.payroll import PayrollRecord
from models.employee import Employee


class PayrollService:
    """Service for managing payroll operations"""

    @staticmethod
    async def get_payroll_records(
        db: AsyncSession,
        employee_id: str,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get payroll records for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            year: Filter by year
            status: Filter by payment status

        Returns:
            List of payroll records
        """
        conditions = [PayrollRecord.employee_id == employee_id]

        if year:
            conditions.append(PayrollRecord.year == year)
        if status:
            conditions.append(PayrollRecord.payment_status == status)

        query = select(PayrollRecord).where(and_(*conditions)).order_by(
            PayrollRecord.year.desc(),
            PayrollRecord.month.desc()
        )
        result = await db.execute(query)
        records = result.scalars().all()

        return [record.to_dict() for record in records]

    @staticmethod
    async def get_payslip(
        db: AsyncSession,
        employee_id: str,
        month: int,
        year: int
    ) -> Optional[Dict]:
        """
        Get payslip for a specific month

        Args:
            db: Database session
            employee_id: Employee ID
            month: Month (1-12)
            year: Year

        Returns:
            Payroll record or None
        """
        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.employee_id == employee_id,
                PayrollRecord.month == month,
                PayrollRecord.year == year
            )
        )
        result = await db.execute(query)
        payroll = result.scalar_one_or_none()

        return payroll.to_dict() if payroll else None

    @staticmethod
    async def get_payslip_by_id(
        db: AsyncSession,
        record_id: str,
        employee_id: str
    ) -> Optional[Dict]:
        """Get a specific payslip by ID"""
        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.id == record_id,
                PayrollRecord.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        payroll = result.scalar_one_or_none()

        return payroll.to_dict() if payroll else None

    @staticmethod
    async def create_payroll_record(
        db: AsyncSession,
        employee_id: str,
        month: int,
        year: int,
        base_salary: Decimal,
        allowances: Dict = None,
        deductions: Dict = None,
        payment_date: Optional[date] = None,
        payment_method: Optional[str] = None
    ) -> Dict:
        """
        Create a new payroll record

        Args:
            db: Database session
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            base_salary: Base salary amount
            allowances: Dict of allowances {"HRA": 5000, "Transport": 2000}
            deductions: Dict of deductions {"Tax": 3000, "PF": 2000}
            payment_date: Payment date
            payment_method: Payment method

        Returns:
            Created payroll record
        """
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")

        # Check if payroll already exists for this period
        existing = await PayrollService.get_payslip(db, employee_id, month, year)
        if existing:
            raise ValueError(f"Payroll record already exists for {month}/{year}")

        # Calculate gross salary
        allowances = allowances or {}
        total_allowances = sum(Decimal(str(v)) for v in allowances.values())
        gross_salary = base_salary + total_allowances

        # Calculate total deductions
        deductions = deductions or {}
        total_deductions = sum(Decimal(str(v)) for v in deductions.values())

        # Calculate net salary
        net_salary = gross_salary - total_deductions

        # Create payroll record
        payroll = PayrollRecord(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            month=month,
            year=year,
            base_salary=base_salary,
            allowances=allowances,
            gross_salary=gross_salary,
            deductions=deductions,
            total_deductions=total_deductions,
            net_salary=net_salary,
            payment_date=payment_date,
            payment_status="Pending" if not payment_date else "Processed",
            payment_method=payment_method
        )

        db.add(payroll)
        await db.commit()
        await db.refresh(payroll)

        return payroll.to_dict()

    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        record_id: str,
        employee_id: str,
        payment_status: str,
        payment_date: Optional[date] = None,
        payment_method: Optional[str] = None
    ) -> Dict:
        """
        Update payment status of a payroll record

        Args:
            db: Database session
            record_id: Payroll record ID
            employee_id: Employee ID (for verification)
            payment_status: New status (Pending, Processed, Paid)
            payment_date: Payment date
            payment_method: Payment method

        Returns:
            Updated payroll record
        """
        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.id == record_id,
                PayrollRecord.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        payroll = result.scalar_one_or_none()

        if not payroll:
            raise ValueError("Payroll record not found")

        valid_statuses = ["Pending", "Processed", "Paid"]
        if payment_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        payroll.payment_status = payment_status
        if payment_date:
            payroll.payment_date = payment_date
        if payment_method:
            payroll.payment_method = payment_method

        payroll.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(payroll)

        return payroll.to_dict()

    @staticmethod
    async def get_ytd_summary(
        db: AsyncSession,
        employee_id: str,
        year: Optional[int] = None
    ) -> Dict:
        """
        Get Year-To-Date (YTD) salary summary

        Args:
            db: Database session
            employee_id: Employee ID
            year: Year (defaults to current year)

        Returns:
            YTD summary with totals
        """
        if year is None:
            year = datetime.now().year

        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.employee_id == employee_id,
                PayrollRecord.year == year
            )
        ).order_by(PayrollRecord.month)

        result = await db.execute(query)
        records = result.scalars().all()

        if not records:
            return {
                "employee_id": employee_id,
                "year": year,
                "months_processed": 0,
                "ytd_gross_salary": 0.0,
                "ytd_deductions": 0.0,
                "ytd_net_salary": 0.0,
                "average_monthly_gross": 0.0,
                "average_monthly_net": 0.0
            }

        # Calculate totals
        ytd_gross = sum(record.gross_salary for record in records)
        ytd_deductions = sum(record.total_deductions for record in records)
        ytd_net = sum(record.net_salary for record in records)
        months_count = len(records)

        return {
            "employee_id": employee_id,
            "year": year,
            "months_processed": months_count,
            "ytd_gross_salary": float(ytd_gross),
            "ytd_deductions": float(ytd_deductions),
            "ytd_net_salary": float(ytd_net),
            "average_monthly_gross": float(ytd_gross / months_count),
            "average_monthly_net": float(ytd_net / months_count),
            "months_detail": [
                {
                    "month": record.month,
                    "gross_salary": float(record.gross_salary),
                    "net_salary": float(record.net_salary),
                    "status": record.payment_status
                }
                for record in records
            ]
        }

    @staticmethod
    async def delete_payroll_record(
        db: AsyncSession,
        record_id: str,
        employee_id: str
    ) -> bool:
        """Delete a payroll record (admin function)"""
        query = select(PayrollRecord).where(
            and_(
                PayrollRecord.id == record_id,
                PayrollRecord.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        payroll = result.scalar_one_or_none()

        if not payroll:
            raise ValueError("Payroll record not found")

        if payroll.payment_status == "Paid":
            raise ValueError("Cannot delete paid payroll records")

        await db.delete(payroll)
        await db.commit()

        return True
