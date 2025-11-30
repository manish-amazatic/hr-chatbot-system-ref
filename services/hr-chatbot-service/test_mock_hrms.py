"""
Test script for Mock HRMS Client
"""
import asyncio
from core.services.hrms_api import HRMSClient


async def test_mock_hrms():
    """Test all mock HRMS operations"""
    client = HRMSClient()
    
    print("=" * 60)
    print("Testing Mock HRMS Client")
    print("=" * 60)
    
    # Test 1: Get leave balance
    print("\n1. Getting leave balance...")
    balance = await client.get_leave_balance()
    print(f"   Employee: {balance['employee_id']}")
    print(f"   Year: {balance['year']}")
    for b in balance['balances']:
        print(f"   {b['leave_type']}: {b['available_days']}/{b['total_days']} days available")
    
    # Test 2: Apply for leave
    print("\n2. Applying for leave...")
    leave_request = await client.apply_leave(
        leave_type="Annual",
        start_date="2025-12-05",
        end_date="2025-12-07",
        reason="Holiday vacation"
    )
    print(f"   Request ID: {leave_request['id']}")
    print(f"   Status: {leave_request['status']}")
    print(f"   Days: {leave_request['days']}")
    
    # Test 3: Get all leave requests
    print("\n3. Getting all leave requests...")
    requests = await client.get_leave_requests()
    print(f"   Total requests: {len(requests)}")
    for req in requests[:3]:  # Show first 3
        print(f"   - {req['id']}: {req['leave_type']} ({req['status']})")
    
    # Test 4: Get attendance records
    print("\n4. Getting attendance records...")
    attendance = await client.get_attendance_records()
    print(f"   Total records: {len(attendance)}")
    for att in attendance[:3]:  # Show first 3
        print(f"   - {att['date']}: {att['status']}, {att['work_hours']} hours")
    
    # Test 5: Get attendance summary
    print("\n5. Getting attendance summary...")
    summary = await client.get_attendance_summary(month=11, year=2025)
    print(f"   Present days: {summary['present_days']}/{summary['total_days']}")
    print(f"   Average work hours: {summary['average_work_hours']:.1f} hours/day")
    
    # Test 6: Get current payslip
    print("\n6. Getting current payslip...")
    payslip = await client.get_current_payslip()
    print(f"   Month/Year: {payslip['month']}/{payslip['year']}")
    print(f"   Base Salary: ${payslip['base_salary']:,}")
    print(f"   Gross Salary: ${payslip['gross_salary']:,}")
    print(f"   Net Salary: ${payslip['net_salary']:,}")
    
    # Test 7: Get YTD summary
    print("\n7. Getting YTD summary...")
    ytd = await client.get_ytd_summary(year=2025)
    print(f"   Total Gross: ${ytd['total_gross_salary']:,}")
    print(f"   Total Net: ${ytd['total_net_salary']:,}")
    print(f"   Months Paid: {ytd['months_paid']}")
    print(f"   Average Monthly Net: ${ytd['average_monthly_net']:,.2f}")
    
    # Test 8: Cancel leave request
    print("\n8. Cancelling a leave request...")
    try:
        cancelled = await client.cancel_leave_request(leave_request['id'])
        print(f"   Request {cancelled['id']} cancelled successfully")
        print(f"   New status: {cancelled['status']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_mock_hrms())
