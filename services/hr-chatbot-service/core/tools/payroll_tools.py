"""
Payroll Agent
Specialized LangChain agent for payroll and compensation queries
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from langchain_classic.tools import tool
from core.tools.hr_rag_tool import search_hr_policies
from core.services.hrms_api import hrms_client

logger = logging.getLogger(__name__)




@tool
async def get_latest_payslip() -> str:
    """
    Get the latest payslip information.

    Returns:
        Details of the most recent payslip
    """
    try:
        payslip = await hrms_client.get_current_payslip()

        result = f"Current Month Payslip:\n\n"
        result += f"• Month/Year: {payslip.get('month')}/{payslip.get('year')}\n"
        result += f"• Base Salary: ${payslip.get('base_salary', 0):,.2f}\n"
        result += f"• Gross Salary: ${payslip.get('gross_salary', 0):,.2f}\n"
        result += f"• Total Deductions: ${payslip.get('total_deductions', 0):,.2f}\n"
        result += f"• Net Salary: ${payslip.get('net_salary', 0):,.2f}\n"
        result += f"• Payment Status: {payslip.get('payment_status', 'Pending')}\n"

        if payslip.get('payment_date'):
            result += f"• Payment Date: {payslip['payment_date']}\n"

        # Show allowances if available
        if payslip.get('allowances'):
            result += "\nAllowances:\n"
            for key, value in payslip['allowances'].items():
                result += f"  • {key}: ${value:,.2f}\n"

        # Show deductions if available
        if payslip.get('deductions'):
            result += "\nDeductions:\n"
            for key, value in payslip['deductions'].items():
                result += f"  • {key}: ${value:,.2f}\n"

        return result
    except Exception as e:
        logger.error(f"Error getting payslip: {str(e)}")
        return f"Error retrieving payslip: {str(e)}"

@tool
async def get_ytd_summary(year: Optional[str] = None) -> str:
    """
    Get year-to-date earnings summary.

    Args:
        year: Year for the summary (defaults to current year)

    Returns:
        YTD earnings, deductions, and net pay summary
    """
    try:
        year_int = int(year) if year else None

        ytd = await hrms_client.get_ytd_summary(year=year_int)

        result = f"Year-to-Date Summary ({ytd.get('year')}):\n\n"
        result += f"• YTD Gross Salary: ${ytd.get('ytd_gross_salary', 0):,.2f}\n"
        result += f"• YTD Deductions: ${ytd.get('ytd_deductions', 0):,.2f}\n"
        result += f"• YTD Net Salary: ${ytd.get('ytd_net_salary', 0):,.2f}\n"
        result += f"• Months Processed: {ytd.get('months_processed', 0)}\n"

        if ytd.get('average_monthly_salary'):
            result += f"• Average Monthly Salary: ${ytd['average_monthly_salary']:,.2f}\n"

        return result
    except Exception as e:
        logger.error(f"Error getting YTD summary: {str(e)}")
        return f"Error getting YTD summary: {str(e)}"

@tool
async def search_payroll_policy(query: str) -> str:
    """
    Search for payroll and compensation policies.

    Use this for questions about:
    - Salary structure
    - Allowances and benefits
    - Tax deductions
    - Bonus policies
    - Increment policies
    - Compensation guidelines

    Args:
        query: Question about payroll policies

    Returns:
        Answer based on company payroll policies
    """
    try:
        # Use RAG tool to search policies
        return search_hr_policies.invoke({"query": query})
    except Exception as e:
        logger.error(f"Error searching payroll policy: {str(e)}")
        return f"Error searching payroll policy: {str(e)}"

@tool
def explain_payslip_component(component: str) -> str:
    """
    Explain a specific payslip component or deduction.

    Args:
        component: The payslip component to explain (e.g., "HRA", "PF", "TDS")

    Returns:
        Explanation of the component
    """
    try:
        # Common payslip components
        explanations = {
            "hra": "HRA (House Rent Allowance) is a component of your salary paid by your employer to meet your accommodation expenses. It's partially tax-exempt under certain conditions.",
            "pf": "PF (Provident Fund) is a retirement savings scheme where both you and your employer contribute a percentage of your basic salary. Your contribution is 12% and employer's contribution is also 12%.",
            "tds": "TDS (Tax Deducted at Source) is the income tax deducted from your salary by your employer as per Income Tax Act. The amount depends on your tax slab.",
            "esi": "ESI (Employee State Insurance) is a social security scheme providing medical and cash benefits to employees earning below a certain threshold.",
            "gratuity": "Gratuity is a lump sum amount paid by the employer to an employee at the time of leaving the organization after completing at least 5 years of continuous service.",
            "basic": "Basic salary is the fixed component of your salary before any additions or deductions. It typically forms 40-50% of your CTC.",
            "da": "DA (Dearness Allowance) is a cost of living adjustment allowance paid to employees to offset the impact of inflation.",
            "bonus": "Bonus is an additional payment made to employees based on company performance, individual performance, or as per statutory requirements.",
            "professional_tax": "Professional Tax is a state-level tax levied on income earned through employment or profession. The amount varies by state."
        }

        component_lower = component.lower().replace(" ", "_")
        
        # Check if we have a direct explanation
        for key, explanation in explanations.items():
            if key in component_lower or component_lower in key:
                return f"{explanation}\n\nFor more specific details about your payslip, please check the HRMS portal or contact payroll@company.com."

        # If not found, search policies
        return search_hr_policies.invoke({"query": f"What is {component} in payslip?"})

    except Exception as e:
        logger.error(f"Error explaining payslip component: {str(e)}")
        return f"Error explaining component: {str(e)}"

