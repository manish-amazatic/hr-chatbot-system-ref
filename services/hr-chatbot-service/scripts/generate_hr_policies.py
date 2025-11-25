"""
Generate HR Policy Documents

Creates synthetic HR policy documents for RAG system testing.
Generates 8 comprehensive HR policy documents covering common workplace topics.
"""
import os
from pathlib import Path
from datetime import datetime


# HR Policy Documents Content
POLICIES = {
    "leave_policy.txt": """
# Leave Policy - Amazatic Technologies

**Effective Date**: January 1, 2025
**Version**: 2.0

## 1. Overview

This leave policy outlines the various types of leave available to employees at Amazatic Technologies and the procedures for requesting and approving leave.

## 2. Types of Leave

### 2.1 Annual Leave
- **Entitlement**: 20 days per calendar year
- **Accrual**: Prorated based on joining date
- **Carry Forward**: Maximum 5 days to next year
- **Encashment**: Allowed upon resignation (unused balance)
- **Notice Period**: Minimum 7 days advance notice required

### 2.2 Sick Leave
- **Entitlement**: 12 days per calendar year
- **Documentation**: Medical certificate required for 3+ consecutive days
- **Carry Forward**: Not allowed
- **Encashment**: Not allowed

### 2.3 Casual Leave
- **Entitlement**: 10 days per calendar year
- **Usage**: For short-term, unplanned absences
- **Notice Period**: Can be taken with short notice
- **Carry Forward**: Not allowed

### 2.4 Maternity Leave
- **Duration**: 26 weeks (6 months)
- **Eligibility**: Available to all female employees
- **Notice**: Inform manager 8 weeks before expected date
- **Benefits**: Full salary during leave period

### 2.5 Paternity Leave
- **Duration**: 15 days
- **Eligibility**: Available to all male employees
- **Usage**: Must be taken within 3 months of child's birth
- **Benefits**: Full salary during leave period

### 2.6 Compassionate Leave
- **Duration**: 5 days per incident
- **Purpose**: Death of immediate family member
- **Benefits**: Fully paid

### 2.7 Marriage Leave
- **Duration**: 5 days
- **Eligibility**: Once during employment
- **Notice**: Minimum 30 days advance notice
- **Benefits**: Fully paid

## 3. Leave Application Process

### 3.1 Advance Planning
- Submit leave request via HRMS portal
- Manager approval required
- Minimum notice periods must be observed

### 3.2 Emergency Leave
- Inform manager immediately via phone/email
- Submit formal request within 24 hours
- Provide supporting documentation

### 3.3 Approval Workflow
1. Employee submits request
2. Manager reviews and approves/rejects
3. HR records the decision
4. Employee receives notification

## 4. Leave Restrictions

- Maximum 10 consecutive working days without special approval
- Blackout periods during critical project phases
- No leave encashment during active employment (except annual leave)
- Unused sick and casual leave lapses at year-end

## 5. Leave Balance Tracking

- Check balance via HRMS portal
- Monthly statements sent via email
- Annual balance reset on January 1

## 6. Special Circumstances

### 6.1 Extended Medical Leave
- Beyond sick leave entitlement
- Requires medical board certification
- May be unpaid based on tenure

### 6.2 Sabbatical
- Available after 5 years of service
- Up to 6 months unpaid
- Requires 6 months advance notice
- Position not guaranteed upon return

## 7. Policy Violations

Unauthorized absence or misuse of leave may result in:
- Written warning
- Salary deduction
- Disciplinary action
- Termination (for repeat offenses)

## 8. Contact Information

For questions about leave policy:
- Email: hr@amazatic.com
- Phone: +91-80-1234-5678
- HRMS Portal: https://hrms.amazatic.com

---
*Last Updated: January 2025*
*Policy Owner: HR Department*
""",

    "attendance_policy.txt": """
# Attendance and Work Hours Policy

**Company**: Amazatic Technologies
**Effective Date**: January 1, 2025
**Policy Number**: HR-ATT-001

## 1. Work Schedule

### 1.1 Standard Working Hours
- **Monday to Friday**: 9:00 AM to 6:00 PM
- **Lunch Break**: 1:00 PM to 2:00 PM (unpaid)
- **Total Work Hours**: 40 hours per week
- **Saturday**: Optional (as required by project)
- **Sunday**: Holiday

### 1.2 Flexible Working Hours
- Core hours: 10:00 AM to 4:00 PM (mandatory presence)
- Flexible start time: 8:00 AM to 10:00 AM
- Flexible end time: 5:00 PM to 7:00 PM
- Must complete 8 hours excluding lunch break

## 2. Attendance Recording

### 2.1 Check-in/Check-out Process
- Use biometric system or HRMS mobile app
- Check-in required within 15 minutes of arrival
- Check-out required before leaving
- Forgotten check-in/out: Report to HR within 24 hours

### 2.2 Late Arrival
- Grace period: 15 minutes (twice per month)
- Beyond grace: Deduction of 1 hour salary
- Habitual lateness: Subject to disciplinary action
- More than 3 late arrivals per month: Written warning

### 2.3 Early Departure
- Requires manager approval
- Must complete minimum 6 hours
- Adjust arrival time to compensate
- Medical emergencies: Exempt from deductions

## 3. Absence Management

### 3.1 Planned Absence
- Apply for leave through HRMS portal
- Get manager approval before absence
- Minimum 24 hours notice for casual leave

### 3.2 Unplanned Absence
- Notify manager within 2 hours of shift start
- Submit leave application within 24 hours
- Medical certificate required for sick leave
- Unapproved absence: Loss of pay

### 3.3 No Call, No Show
- First instance: Written warning + salary deduction
- Second instance: Final warning + 2 days salary deduction
- Third instance: Termination of employment

## 4. Remote Work Attendance

### 4.1 Work From Home (WFH)
- Must be pre-approved by manager
- Check-in via HRMS mobile app
- Available during core hours for meetings
- Track work hours same as office days

### 4.2 Remote Work Expectations
- Respond to emails within 2 hours
- Attend all scheduled meetings
- Deliver work as per agreed timelines
- Maintain communication with team

## 5. Overtime

### 5.1 Overtime Eligibility
- Prior approval from manager required
- Maximum 10 hours per week
- Not applicable to senior management

### 5.2 Overtime Compensation
- Regular days: 1.5x hourly rate
- Weekends: 2x hourly rate
- Holidays: 2.5x hourly rate
- Compensatory off for extended hours

## 6. Attendance Monitoring

### 6.1 Monthly Reports
- Attendance reports generated monthly
- Sent to employees and managers
- Discrepancies must be reported within 5 days

### 6.2 Attendance Thresholds
- Minimum attendance: 90% per month
- Below 85%: Performance review triggered
- Below 75%: Salary deduction + warning

## 7. Special Situations

### 7.1 Company Events
- All-hands meetings: Mandatory attendance
- Team building activities: Encouraged
- Training sessions: As scheduled

### 7.2 Inclement Weather
- Use judgment about commute safety
- WFH option available with manager approval
- Company may announce work-from-home days

### 7.3 Medical Appointments
- Schedule during non-core hours when possible
- Inform manager in advance
- Adjust work hours to compensate
- Extended medical appointments: Apply for leave

## 8. Disciplinary Actions

### 8.1 Progressive Discipline
1. Verbal warning (first offense)
2. Written warning (second offense)
3. Final written warning (third offense)
4. Termination (fourth offense or severe violation)

### 8.2 Serious Violations
- Falsifying attendance records: Immediate termination
- Buddy punching: Termination of both parties
- Consistent policy violations: Termination

## 9. Appeals Process

- Submit written appeal to HR within 5 working days
- HR reviews with manager and employee
- Decision made within 10 working days
- Decision is final

## 10. Policy Review

This policy is reviewed annually and updated as needed.
Last review date: January 1, 2025
Next review date: January 1, 2026

---
*For questions: hr@amazatic.com | +91-80-1234-5678*
""",

    "payroll_policy.txt": """
# Payroll and Compensation Policy

**Organization**: Amazatic Technologies
**Policy ID**: HR-PAY-001
**Version**: 3.0
**Effective**: January 2025

## 1. Salary Structure

### 1.1 Components
- **Basic Salary**: 40% of CTC
- **House Rent Allowance (HRA)**: 30% of Basic
- **Special Allowance**: 20% of CTC
- **Transport Allowance**: ₹2,000 per month
- **Meal Allowance**: ₹1,500 per month

### 1.2 Variable Components
- **Performance Bonus**: Up to 20% of annual CTC
- **Quarterly Incentives**: Based on team/company performance
- **Annual Increment**: 8-15% based on performance

## 2. Payroll Processing

### 2.1 Pay Schedule
- **Pay Date**: 28th of every month
- **Pay Period**: 1st to last day of month
- **Advance Salary**: Not allowed
- **Holiday Pay Date**: If 28th is holiday, payment on previous working day

### 2.2 Payslip Distribution
- Digital payslips via email
- Downloadable from HRMS portal
- Confidential - not to be shared

### 2.3 Payment Method
- Direct bank transfer
- Salary account with designated bank
- Account details must be updated in HRMS

## 3. Deductions

### 3.1 Statutory Deductions
- **Provident Fund (PF)**: 12% of Basic
- **Professional Tax**: As per state regulations
- **Income Tax (TDS)**: As per IT Act
- **Employee State Insurance (ESI)**: If applicable

### 3.2 Other Deductions
- Loan repayments (if any)
- Advance recovery
- Loss of pay for unap proved absence
- Notice period recovery

### 3.3 Loss of Pay Calculation
- Per day deduction = Monthly Basic / 30
- Applies to unauthorized absence
- Half-day absence = 50% deduction

## 4. Allowances and Reimbursements

### 4.1 Travel Allowances
- Local travel: Actuals with bills
- Outstation: Per diem + actual expenses
- International: As per company policy
- Claim submission within 30 days

### 4.2 Medical Reimbursement
- Annual limit: ₹25,000
- Covers employee and immediate family
- Requires original bills
- Submit claims quarterly

### 4.3 Communication Allowance
- Mobile: ₹1,000 per month
- Internet: ₹500 per month
- Actual bill submission not required

### 4.4 Education Allowance
- ₹2,000 per child per month
- Maximum 2 children
- School fee reimbursement
- Requires fee receipts

## 5. Performance Bonuses

### 5.1 Quarterly Performance Bonus
- Based on individual and team performance
- Rating: 1-5 scale
- Payout: 0-10% of quarterly salary
- Paid in following quarter

### 5.2 Annual Performance Bonus
- Based on annual performance review
- Range: 0-20% of annual CTC
- Exceptional performers: Up to 30%
- Paid in April following appraisal cycle

### 5.3 Retention Bonus
- After 3 years: 1 month salary
- After 5 years: 2 months salary
- After 10 years: 3 months salary
- Payable upon completion anniversary

## 6. Salary Revision

### 6.1 Annual Increment
- Performance review in March
- Increments effective from April
- Range: 8-15% based on rating
- Exceptional: Up to 20%

### 6.2 Promotion Increment
- Minimum 15% increment
- Effective from promotion date
- Revised designation and responsibilities

### 6.3 Market Correction
- Periodic salary benchmarking
- Adjustments for market competitiveness
- Ad-hoc revisions as needed

## 7. Taxation

### 7.1 Tax Regime
- Employees may choose old or new tax regime
- Declaration required by April 30th
- Changes allowed once per year

### 7.2 Investment Declarations
- Submit proofs by January 31st
- Section 80C: Up to ₹1.5 lakhs
- HRA exemption: Requires rent receipts
- Form 12BB submission mandatory

### 7.3 Income Tax Statement
- Form 16 issued by May 31st
- Available on HRMS portal
- Required for ITR filing

## 8. Final Settlement

### 8.1 Resignation
- Full and final settlement within 45 days
- Includes: Salary, leave encashment, bonus (prorated)
- Deductions: Notice period recovery, loans

### 8.2 Termination
- Payment as per termination terms
- No bonus or incentive payout
- Statutory dues settled

### 8.3 Retirement
- Gratuity as per Payment of Gratuity Act
- PF withdrawal process initiated
- All pending dues settled

## 9. Salary Confidentiality

- Salary information is strictly confidential
- Disclosure prohibited (except to authorized personnel)
- Violation may result in termination

## 10. Grievance Redressal

### 10.1 Query Resolution
- Contact HR for payroll queries
- Response within 2 working days
- Escalate to HR Head if unresolved

### 10.2 Dispute Resolution
- Submit written complaint to HR
- Review within 10 working days
- Escalation to Management if needed

## 11. Payroll Calendar

- **January**: Annual tax declaration
- **February**: Investment proof submission
- **March**: Performance appraisals
- **April**: Increment processing
- **May**: Form 16 distribution
- **Quarterly**: Bonus processing

## 12. Contact

**Payroll Team**
- Email: payroll@amazatic.com
- Phone: +91-80-1234-5679
- HRMS Support: hrms.support@amazatic.com

---
*Policy managed by Finance & HR Department*
*Review frequency: Annual*
""",

    "wfh_policy.txt": """
# Work From Home (WFH) Policy

**Company**: Amazatic Technologies
**Effective Date**: January 2025
**Policy Code**: HR-WFH-002

## 1. Policy Overview

This policy outlines guidelines for remote work arrangements, ensuring productivity, accountability, and work-life balance while maintaining team collaboration.

## 2. Eligibility

### 2.1 General Eligibility
- Completed probation period (6 months)
- Consistent good performance
- Role suitable for remote work
- Reliable internet and workspace at home

### 2.2 Ineligible Roles
- Roles requiring physical presence
- New joiners (first 6 months)
- Employees on performance improvement plan

## 3. WFH Options

### 3.1 Regular WFH
- Up to 2 days per week
- Manager pre-approval required
- Schedule in advance on HRMS

### 3.2 Ad-hoc WFH
- Same-day request with valid reason
- Manager approval required
- Limited to 1 day per week

### 3.3 Extended WFH
- Medical reasons or special circumstances
- Requires documentation
- Manager and HR approval
- Duration: Up to 2 weeks

### 3.4 Hybrid Work Model
- Team decides fixed WFH days
- Mandatory office days: Tuesday, Thursday
- Optional: Monday, Wednesday, Friday

## 4. Work Expectations

### 4.1 Availability
- Online during core hours (10 AM - 4 PM)
- Respond to messages within 30 minutes
- Available for video calls
- Update status on communication tools

### 4.2 Communication
- Daily standup: Mandatory attendance
- Team meetings: Video on required
- Use company-approved tools: Slack, Zoom, Teams
- Update calendar with availability

### 4.3 Productivity
- Complete assigned tasks on time
- Track time using approved tools
- Same deliverables as office work
- Proactive communication about blockers

## 5. Technology Requirements

### 5.1 Mandatory
- Stable internet connection (minimum 20 Mbps)
- Laptop/desktop with updated software
- Headset with microphone
- Webcam for video calls

### 5.2 Company Provided
- Laptop (company property)
- VPN access for secure connection
- Access to required software/tools
- IT support available remotely

### 5.3 Employee Responsibility
- Home internet costs
- Electricity
- Ergonomic setup
- Secure workspace

## 6. Data Security

### 6.1 Mandatory Practices
- Use VPN for company network access
- Secure home WiFi with strong password
- Lock screen when away
- No sharing of credentials

### 6.2 Prohibited
- Using public WiFi for work
- Storing company data on personal devices
- Sharing screen with unauthorized persons
- Working from cafes or co-working spaces without approval

### 6.3 Data Breach
- Report immediately to IT and manager
- Investigation initiated
- Disciplinary action for negligence

## 7. Work Environment

### 7.1 Home Office Requirements
- Dedicated quiet workspace
- Minimal distractions
- Proper lighting
- Ergonomic setup recommended

### 7.2 Professionalism
- Appropriate background for video calls
- Professional attire (at least business casual)
- Minimize background noise
- Family members aware of work hours

## 8. Attendance and Time Tracking

### 8.1 Check-in Process
- Log in via HRMS mobile app
- Update status on communication platform
- Log work hours accurately

### 8.2 Break Times
- Regular break times same as office
- Lunch break: 1 hour
- Short breaks: Allowed

### 8.3 Overtime
- Prior manager approval required
- Track accurately in HRMS
- Same rules as office work

## 9. Meeting Guidelines

### 9.1 Video Calls
- Camera on for team meetings
- Mute when not speaking
- Test audio/video before important meetings
- Be on time

### 9.2 In-person Meetings
- Attend office meetings when scheduled
- Minimum 24 hours notice given
- WFH not applicable on meeting days

## 10. Performance Management

### 10.1 Evaluation Criteria
- Quality and timeliness of deliverables
- Communication and collaboration
- Availability and responsiveness
- Achievement of goals and KPIs

### 10.2 WFH Privileges
- May be revoked for poor performance
- Regular monitoring by managers
- Feedback sessions as needed

## 11. Special Circumstances

### 11.1 Medical Conditions
- Pregnant employees: Flexible WFH
- Medical conditions: With doctor's note
- Duration as needed
- Regular check-ins with HR

### 11.2 Natural Disasters/Emergencies
- Company-wide WFH announced
- Flexible hours allowed
- Focus on safety first
- Regular team communication

### 11.3 Parental Responsibilities
- Emergencies: Immediate WFH
- Childcare issues: Discuss with manager
- Flexible arrangements possible

## 12. Equipment and Support

### 12.1 IT Support
- Help desk: 9 AM to 6 PM
- Email: itsupport@amazatic.com
- Remote assistance available
- SLA: 4 hours response time

### 12.2 Equipment Issues
- Report to IT immediately
- Backup laptop available if needed
- Repair/replacement process
- No personal device usage for work

## 13. Expenses and Reimbursements

### 13.1 Not Reimbursable
- Home internet
- Electricity
- Furniture
- Stationary

### 13.2 Reimbursable
- VPN/security software (if required)
- Specific tools approved by IT
- Business calls/communication

## 14. Termination of WFH Privilege

### 14.1 Reasons
- Poor performance
- Productivity decline
- Security violations
- Abuse of policy
- Project requirements

### 14.2 Process
- Manager discussion
- HR notification
- Notice period: 1 week
- Return to office arrangement

## 15. Policy Review

- Reviewed quarterly
- Updated based on feedback
- Changes communicated via email

## 16. Approval Process

1. Request WFH on HRMS portal
2. Manager reviews and approves/rejects
3. Notification sent to employee
4. Update calendar and team

## 17. Contact

**WFH Coordinators**
- HR: wfh@amazatic.com
- IT Support: itsupport@amazatic.com
- Manager: Direct communication

---
*This policy promotes flexibility while ensuring business continuity*
*Subject to periodic review and updates*
""",

    "code_of_conduct.txt": """
# Code of Conduct

**Amazatic Technologies**
**Version**: 4.0
**Effective**: January 2025

## 1. Purpose

This Code of Conduct establishes expectations for ethical behavior, professionalism, and workplace conduct for all employees at Amazatic Technologies.

## 2. Core Values

### 2.1 Integrity
- Honesty in all business dealings
- Ethical decision-making
- Transparency in communication
- Accountability for actions

### 2.2 Respect
- Treat everyone with dignity
- Value diversity and inclusion
- Listen actively to others
- Respect different perspectives

### 2.3 Excellence
- Commitment to quality
- Continuous improvement
- Innovation and creativity
- Professional growth

### 2.4 Collaboration
- Team-oriented approach
- Knowledge sharing
- Support colleagues
- Constructive feedback

## 3. Professional Conduct

### 3.1 Workplace Behavior
- Arrive on time and prepared
- Maintain professional appearance
- Use respectful language
- Follow company policies
- Complete assigned work diligently

### 3.2 Communication
- Respond to emails within 24 hours
- Be clear and concise
- Avoid gossip and rumors
- Use appropriate channels
- Professional tone in all communication

### 3.3 Attendance and Punctuality
- Adhere to work schedule
- Inform manager of absences
- Request leave appropriately
- Avoid excessive absenteeism

## 4. Ethical Standards

### 4.1 Honesty
- No falsification of documents
- Accurate reporting of work hours
- Truthful communication
- Admit mistakes promptly

### 4.2 Confidentiality
- Protect company information
- Respect client confidentiality
- No disclosure of trade secrets
- Secure handling of data

### 4.3 Conflict of Interest
- Disclose potential conflicts
- No personal benefit from position
- Avoid dual employment conflicts
- Transparent external engagements

### 4.4 Anti-Bribery and Corruption
- No giving or receiving bribes
- No kickbacks or improper payments
- Fair dealing with vendors
- Report suspected violations

## 5. Workplace Respect

### 5.1 Harassment Prevention
Zero tolerance for:
- Sexual harassment
- Verbal abuse or threats
- Physical intimidation
- Bullying or belittling
- Discriminatory behavior

### 5.2 Discrimination
Prohibited discrimination based on:
- Gender or gender identity
- Race or ethnicity
- Religion or beliefs
- Age
- Disability
- Sexual orientation
- Marital status
- Any other protected category

### 5.3 Creating Inclusive Environment
- Welcome diverse perspectives
- Use inclusive language
- Accommodate differences
- Celebrate diversity

## 6. Use of Company Resources

### 6.1 Property and Equipment
- Use for business purposes only
- Take care of company property
- Report damage or theft immediately
- Return all property upon termination

### 6.2 Technology Usage
- Follow IT policies
- No unauthorized software
- Secure passwords and access
- Report security incidents

### 6.3 Personal Use
- Limited personal use acceptable
- Must not interfere with work
- No illegal or inappropriate content
- Subject to monitoring

## 7. Social Media and External Communication

### 7.1 Professional Boundaries
- Don't speak for the company
- Respect confidentiality
- Maintain professional image
- Separate personal and professional accounts

### 7.2 Prohibited Content
- Confidential company information
- Disparaging remarks about company
- Harassment or discrimination
- Illegal or offensive content

### 7.3 Client Interaction
- Professional at all times
- Protect client information
- Refer media inquiries to PR
- No unauthorized commitments

## 8. Health and Safety

### 8.1 Workplace Safety
- Follow safety procedures
- Report hazards immediately
- Use protective equipment
- Participate in safety training

### 8.2 Substance Abuse
- No alcohol during work hours
- No illegal drugs
- No working under influence
- Support programs available

### 8.3 Violence Prevention
- Zero tolerance for violence
- Report threats immediately
- No weapons on premises
- Create safe environment

## 9. Financial Integrity

### 9.1 Accurate Records
- Truthful expense reports
- Proper documentation
- No falsification
- Timely submission

### 9.2 Company Funds
- Use only for authorized purposes
- No personal benefit
- Comply with financial policies
- Report irregularities

### 9.3 Gifts and Entertainment
- Follow gift policy
- Nominal value only
- No quid pro quo
- Disclose significant gifts

## 10. Intellectual Property

### 10.1 Protection
- Respect IP rights
- No unauthorized copying
- Proper licensing
- Credit original creators

### 10.2 Company IP
- Company owns work product
- Protect proprietary information
- No unauthorized disclosure
- Agreement terms binding

## 11. Environmental Responsibility

### 11.1 Sustainability
- Reduce waste
- Recycle when possible
- Conserve energy
- Eco-friendly practices

### 11.2 Compliance
- Follow environmental regulations
- Report violations
- Support green initiatives

## 12. Reporting Violations

### 12.1 Responsibility to Report
- All employees must report violations
- Good faith reporting protected
- Multiple reporting channels
- No retaliation for reporting

### 12.2 Reporting Channels
- Direct manager
- HR Department
- Ethics hotline: 1-800-ETHICS
- Email: ethics@amazatic.com
- Anonymous reporting available

### 12.3 Investigation Process
- Prompt investigation
- Confidentiality maintained
- Fair process
- Appropriate action taken

## 13. Consequences of Violations

### 13.1 Disciplinary Actions
- Verbal warning
- Written warning
- Suspension
- Termination
- Legal action if warranted

### 13.2 Factors Considered
- Severity of violation
- Intent
- Prior history
- Cooperation in investigation
- Mitigating circumstances

## 14. No Retaliation

- Protected whistleblowers
- No adverse action for good faith reporting
- Retaliation itself a violation
- Support for reporters

## 15. Compliance Certification

- Annual acknowledgment required
- Training provided
- Questions encouraged
- Ongoing commitment

## 16. Policy Updates

This Code is reviewed annually and updated as needed to reflect:
- Legal changes
- Best practices
- Company growth
- Employee feedback

## 17. Questions and Guidance

**Ethics and Compliance Team**
- Email: ethics@amazatic.com
- Phone: +91-80-1234-5680
- Anonymous Hotline: 1-800-ETHICS
- HR Department: hr@amazatic.com

## 18. Acknowledgment

I acknowledge that I have read, understood, and agree to comply with this Code of Conduct. I understand that violations may result in disciplinary action up to and including termination.

---
*Amazatic Technologies is committed to maintaining the highest standards of ethics and professionalism*
*Every employee plays a role in upholding these standards*
""",

    "performance_review.txt": """
# Performance Review Policy

**Organization**: Amazatic Technologies
**Policy ID**: HR-PERF-001
**Version**: 2.0
**Last Updated**: January 2025

## 1. Overview

This policy outlines the performance management system at Amazatic Technologies, including review cycles, evaluation criteria, and development planning.

## 2. Philosophy

Performance management at Amazatic is:
- **Continuous**: Not just annual reviews
- **Developmental**: Focus on growth and improvement
- **Fair**: Based on objective criteria
- **Transparent**: Clear expectations and feedback
- **Collaborative**: Manager and employee partnership

## 3. Review Cycles

### 3.1 Annual Performance Review
- **Timing**: March each year
- **Period Covered**: April to March
- **Outcomes**: Rating, increment, promotion decisions
- **Process**: Self-assessment + Manager review + Calibration

### 3.2 Mid-Year Review
- **Timing**: September
- **Purpose**: Progress check-in
- **Format**: Informal discussion
- **Outcomes**: Course correction, goal adjustment

### 3.3 Quarterly Check-ins
- **Frequency**: Quarterly
- **Duration**: 30-60 minutes
- **Focus**: Recent performance, immediate goals
- **Documentation**: Brief notes in HRMS

### 3.4 Continuous Feedback
- Ongoing throughout the year
- Real-time feedback encouraged
- Both positive and constructive

## 4. Performance Rating Scale

### 4.1 5-Point Rating System
1. **Exceptional (E)** - Consistently exceeds expectations
   - Far surpasses goals
   - Significant impact
   - Role model for others
   - Top 5% of employees

2. **Exceeds Expectations (EE)** - Regularly exceeds goals
   - Surpasses all objectives
   - High-quality work
   - Proactive and initiative-taking
   - 15-20% of employees

3. **Meets Expectations (ME)** - Fully meets all requirements
   - Achieves all goals
   - Consistent performance
   - Reliable and dependable
   - 60-65% of employees

4. **Needs Improvement (NI)** - Partially meets expectations
   - Some goals not met
   - Requires support
   - Developmental areas identified
   - 10-15% of employees

5. **Unsatisfactory (U)** - Does not meet basic requirements
   - Significant gaps in performance
   - Immediate improvement required
   - May lead to PIP or termination
   - <5% of employees

### 4.2 Rating Distribution
- Calibration ensures fairness
- Forced distribution not mandatory but guidelines exist
- Focus on accurate assessment, not quota

## 5. Evaluation Criteria

### 5.1 Goal Achievement (40%)
- Completion of assigned objectives
- Quality of deliverables
- Timeliness
- Impact on team/company goals

### 5.2 Core Competencies (30%)
- **Technical Skills**: Role-specific expertise
- **Communication**: Clear and effective
- **Collaboration**: Teamwork and cooperation
- **Problem-Solving**: Analytical and creative
- **Adaptability**: Flexibility and learning agility

### 5.3 Values Alignment (15%)
- Integrity
- Respect
- Excellence
- Innovation
- Customer focus

### 5.4 Leadership/Potential (15%)
- For individual contributors: Self-leadership
- For managers: Team leadership
- Initiative and ownership
- Mentoring and knowledge sharing
- Future potential

## 6. Review Process

### 6.1 Goal Setting (April)
- SMART goals defined
- Aligned with team/company objectives
- Documented in HRMS
- Regular tracking throughout year

### 6.2 Self-Assessment (February)
- Employee completes self-review
- Evidence of achievements
- Areas of strength
- Development needs
- Career aspirations

### 6.3 Manager Assessment (Early March)
- Comprehensive evaluation
- 360-degree feedback considered
- Rating and comments
- Development recommendations

### 6.4 Calibration (Mid March)
- Manager presents to calibration committee
- Ratings reviewed for consistency
- Final ratings determined
- Increment/promotion decisions

### 6.5 Review Discussion (Late March)
- One-on-one meeting
- Manager shares rating and feedback
- Discussion of strengths and areas for improvement
- New goals set for next year
- Development plan created

### 6.6 Documentation
- Review form completed in HRMS
- Employee acknowledgment
- Action items documented
- Filed in employee record

## 7. 360-Degree Feedback

### 7.1 Participants
- Self
- Manager
- Peers (2-3)
- Direct reports (for managers)
- Skip-level manager (for senior roles)

### 7.2 Process
- Anonymous peer feedback
- Focus on behaviors, not personality
- Considered in manager's assessment
- Shared with employee

### 7.3 Areas Assessed
- Communication
- Collaboration
- Leadership
- Technical expertise
- Professionalism

## 8. Development Planning

### 8.1 Individual Development Plan (IDP)
- Created during annual review
- Skill gaps identified
- Learning opportunities
- Timeline and milestones
- Manager support

### 8.2 Development Activities
- Training programs
- Online courses
- Workshops and seminars
- Stretch assignments
- Mentoring
- Cross-functional projects

### 8.3 Career Progression
- Career paths discussed
- Promotion readiness
- Skill building for next role
- Long-term goals

## 9. Performance Improvement Plan (PIP)

### 9.1 When Initiated
- "Needs Improvement" or "Unsatisfactory" rating
- Consistent underperformance
- Specific performance issues

### 9.2 PIP Process
- Clearly defined expectations
- Specific improvement goals
- Timeline (typically 60-90 days)
- Regular check-ins
- HR involvement
- Documented progress

### 9.3 PIP Outcomes
- **Successful**: Return to normal performance management
- **Unsuccessful**: May lead to role change or termination
- **Extended**: Additional time if progress shown

## 10. Rewards and Recognition

### 10.1 Based on Performance
- **Exceptional**: 15-20% increment, promotion consideration
- **Exceeds Expectations**: 12-15% increment
- **Meets Expectations**: 8-10% increment
- **Needs Improvement**: 0-5% increment
- **Unsatisfactory**: No increment

### 10.2 Promotions
- Based on performance and readiness
- Must have "Exceeds" or "Exceptional" rating
- Demonstrated skills for next level
- Typically 2-3 years in current role

### 10.3 Bonuses
- Annual bonus based on rating
- Company performance factor
- Individual contribution

## 11. Appeals Process

### 11.1 Grounds for Appeal
- Process not followed
- Bias or discrimination
- Factual errors
- Significant new information

### 11.2 Appeal Process
1. Discuss with manager first
2. Submit written appeal to HR within 10 days
3. HR reviews with senior management
4. Decision within 15 working days
5. Decision is final

## 12. Special Situations

### 12.1 New Hires
- No review in first year if joining after October
- Included in next cycle if joining before October

### 12.2 Role Changes
- Reviewed in previous role if change after October
- Prorated assessment if significant time in new role

### 12.3 Long Absences
- Medical leave: Rating based on time worked
- Maternity/Paternity: No adverse impact
- Other leave: Case by case basis

### 12.4 Terminations
- Exit during cycle: Prorated review if applicable
- No bonus or increment

## 13. Manager Responsibilities

- Set clear expectations
- Provide regular feedback
- Document performance (good and bad)
- Conduct fair and timely reviews
- Support employee development
- Address performance issues promptly

## 14. Employee Responsibilities

- Understand performance expectations
- Seek feedback regularly
- Document achievements
- Complete self-assessment honestly
- Engage in development activities
- Take ownership of performance

## 15. HR Responsibilities

- Administer review process
- Provide training on performance management
- Ensure consistency and fairness
- Facilitate calibration
- Handle appeals
- Maintain records

## 16. Training and Support

- Manager training on performance reviews
- Employee orientation on process
- Templates and guidelines available
- HR support throughout process

## 17. Policy Review

This policy is reviewed annually and may be updated based on:
- Business needs
- Best practices
- Employee feedback
- Legal requirements

## 18. Contact Information

**Performance Management Team**
- Email: performance@amazatic.com
- Phone: +91-80-1234-5681
- HRMS Support: hrms.support@amazatic.com

---
*Effective performance management is key to employee development and company success*
*We're committed to fair, transparent, and developmental review processes*
""",

    "onboarding_guide.txt": """
# New Employee Onboarding Guide

**Welcome to Amazatic Technologies!**

**Your First 90 Days**

## Pre-Joining (Before Day 1)

### Documents to Submit
- [ ] Signed offer letter
- [ ] Educational certificates (attested copies)
- [ ] Previous employment documents
- [ ] PAN card copy
- [ ] Aadhar card copy
- [ ] Passport size photographs (4)
- [ ] Bank account details (canceled cheque)
- [ ] Form 11 (PF declaration)
- [ ] Medical fitness certificate

### What to Expect
- Welcome email from HR
- IT equipment details
- Joining date and time confirmation
- Parking/transport information
- Dress code guidelines

## Day 1: Welcome!

### Reporting Details
- **Time**: 10:00 AM
- **Location**: Reception, 3rd Floor
- **Contact**: HR Coordinator +91-80-1234-5678

### Day 1 Agenda
- 10:00 AM: HR orientation
- 11:00 AM: IT setup (laptop, email, accounts)
- 12:00 PM: Office tour
- 1:00 PM: Lunch with team
- 2:00 PM: Meet your manager
- 3:00 PM: Team introduction
- 4:00 PM: Workspace setup
- 5:00 PM: Day 1 wrap-up

### What to Bring
- Original documents for verification
- Signed NDA and employment agreement
- Laptop bag (if personal laptop)
- Lunch or meal card funds

## Week 1: Getting Started

### HR Activities
- Complete employee information form
- Enroll in benefits (medical insurance)
- PF and ESI registration
- Setup HRMS portal access
- Receive employee ID card
- Attendance system registration

### IT Setup
- Corporate email configuration
- Access to company systems
- VPN setup for remote access
- Software installation
- Security training
- Password policies

### Team Integration
- Daily standups
- Meet team members individually
- Understand team dynamics
- Learn project overview
- Setup 1:1 with manager

### Learning
- Company overview presentation
- Product/service familiarization
- Industry context
- Competitor landscape
- Company values and culture

## Week 2-4: Ramp Up

### Training Programs
- Technical skills training
- Tools and systems training
- Process documentation review
- Best practices workshop
- Security and compliance training

### Project Assignment
- First assignment (small task)
- Shadow senior team member
- Pair programming/reviews
- Ask questions freely
- Document learnings

### Networking
- Meet stakeholders
- Cross-functional introductions
- Join company social channels
- Attend team events
- Coffee chats with colleagues

### 30-Day Check-in
- Meeting with manager
- Discuss progress and challenges
- Clarify expectations
- Adjust goals if needed
- Feedback on onboarding experience

## Month 2: Building Confidence

### Increasing Responsibilities
- Take ownership of small features
- Participate in team meetings actively
- Contribute to team discussions
- Start code reviews (if developer)
- Begin independent work

### Development
- Identify learning needs
- Enroll in relevant courses
- Seek mentorship
- Set development goals
- Request feedback regularly

### Company Culture
- Understand unwritten rules
- Participate in company events
- Join employee resource groups
- Engage in social activities
- Build relationships

### 60-Day Review
- Formal review with manager
- Performance discussion
- Goal progress evaluation
- Address any concerns
- Plan next 30 days

## Month 3: Independence

### Full Productivity
- Handle regular responsibilities
- Work independently
- Meet deadlines consistently
- Quality matches standards
- Proactive communication

### Team Contribution
- Help onboard newer members
- Share knowledge
- Participate in planning
- Suggest improvements
- Collaborate effectively

### Career Planning
- Discuss career goals
- Identify growth areas
- Plan skill development
- Understand promotion paths
- Set long-term objectives

### 90-Day Review
- Comprehensive performance review
- Probation completion discussion
- Confirmation decision
- Future goals setting
- Development plan finalization

## Onboarding Checklist

### Administrative
- [ ] All documents submitted
- [ ] Employee ID card received
- [ ] HRMS portal access
- [ ] Benefits enrollment complete
- [ ] Bank account updated
- [ ] Tax declaration submitted

### IT & Systems
- [ ] Email working
- [ ] All systems access granted
- [ ] VPN configured
- [ ] Required software installed
- [ ] Security training completed

### Team & Work
- [ ] Met all team members
- [ ] Understand team goals
- [ ] First task completed
- [ ] Regular 1:1s scheduled
- [ ] Working independently

### Learning
- [ ] Company overview complete
- [ ] Product knowledge acquired
- [ ] Process training done
- [ ] Technical training complete
- [ ] Security awareness training

## Resources

### People to Know
- **Your Manager**: Direct supervisor
- **HR Business Partner**: [Name]
- **IT Support**: itsupport@amazatic.com
- **Facilities**: facilities@amazatic.com
- **Finance**: finance@amazatic.com

### Important Links
- HRMS Portal: https://hrms.amazatic.com
- Intranet: https://intranet.amazatic.com
- Learning Platform: https://learn.amazatic.com
- Help Desk: https://helpdesk.amazatic.com

### Communication Tools
- Email: Outlook/Gmail
- Chat: Slack/Teams
- Video: Zoom/Teams
- Project Management: Jira/Asana

### Policies to Read
- Code of Conduct
- Leave Policy
- Attendance Policy
- WFH Policy
- IT Usage Policy
- Data Security Policy

## Tips for Success

### Do's
- Ask questions
- Take notes
- Be proactive
- Seek feedback
- Network actively
- Respect culture
- Meet deadlines
- Communicate openly

### Don'ts
- Don't hesitate to ask
- Don't work in isolation
- Don't ignore policies
- Don't skip meetings
- Don't gossip
- Don't miss deadlines

## Common Questions

**Q: When do I get my first salary?**
A: On the 28th of the month following your joining.

**Q: How much leave do I have?**
A: Prorated based on joining date. Check HRMS portal.

**Q: Can I work from home?**
A: After probation period, as per WFH policy.

**Q: Who do I contact for [query]?**
A: Check the Resources section above or ask your manager.

**Q: When is my probation review?**
A: At 3 months (90 days).

**Q: How do I apply for leave?**
A: Through HRMS portal with manager approval.

## Feedback

We want to make onboarding better! Share your feedback:
- Email: onboarding@amazatic.com
- Anonymous survey (link sent at 30, 60, 90 days)
- Direct conversation with HR

## Emergency Contacts

- **Office Reception**: +91-80-1234-5678
- **HR Emergency**: +91-98765-43210
- **IT Support**: +91-98765-43211
- **Security**: +91-98765-43212

## Your Onboarding Buddy

You'll be assigned a buddy - a fellow employee who will:
- Answer your questions
- Show you around
- Introduce you to others
- Share tips and tricks
- Be your go-to person

---

**Welcome to the Amazatic family!**

We're excited to have you here and look forward to your contributions and success!

For any questions during onboarding:
**Onboarding Team** | onboarding@amazatic.com | +91-80-1234-5678
""",

    "employee_handbook.txt": """
# Employee Handbook

**Amazatic Technologies Private Limited**

**Edition**: 2025
**Effective Date**: January 1, 2025

---

## Welcome Message

Dear Team Member,

Welcome to Amazatic Technologies! This handbook is your guide to our company culture, policies, and what you can expect as part of our team.

At Amazatic, we believe in:
- **Innovation**: Pushing boundaries
- **Integrity**: Doing what's right
- **Excellence**: Delivering our best
- **Collaboration**: Succeeding together
- **Growth**: Continuous improvement

This handbook outlines your rights, responsibilities, and the resources available to you. Please read it carefully and refer to it whenever you have questions.

We're thrilled to have you on board!

**Manish Wadhwani**
Founder & CEO

---

## Table of Contents

1. About Amazatic
2. Employment Basics
3. Compensation and Benefits
4. Time Off and Leave
5. Workplace Policies
6. Professional Development
7. Performance Management
8. Health and Safety
9. Technology and Security
10. Termination and Separation

---

## 1. About Amazatic

### 1.1 Company Overview
- **Founded**: 2018
- **Headquarters**: Bangalore, Karnataka
- **Industry**: Technology Services
- **Employees**: 250+
- **Mission**: Deliver innovative solutions that transform businesses

### 1.2 Our Values
- **Customer First**: Client success is our success
- **Innovation**: Embrace change and creativity
- **Integrity**: Honesty and transparency
- **Excellence**: High standards in everything
- **Teamwork**: Collaborate and support each other

### 1.3 Products and Services
- Custom Software Development
- Cloud Solutions
- Mobile App Development
- AI/ML Consulting
- DevOps Services

---

## 2. Employment Basics

### 2.1 Employment Status
- **Full-time**: 40 hours per week
- **Part-time**: Less than 40 hours (prorated benefits)
- **Contract**: Fixed-term agreements
- **Intern**: Training program (3-6 months)

### 2.2 Probation Period
- Duration: 6 months
- Performance evaluation at 3 and 6 months
- Either party may terminate with 1 week notice
- Upon confirmation: Full benefits and 2-month notice period

### 2.3 Work Hours
- Standard: 9:00 AM - 6:00 PM, Monday-Friday
- Flexible hours available after probation
- Core hours: 10:00 AM - 4:00 PM (mandatory)

### 2.4 Employee Classification
- **Non-Exempt**: Eligible for overtime
- **Exempt**: Salaried, no overtime

---

## 3. Compensation and Benefits

### 3.1 Salary
- Paid monthly on the 28th
- Direct deposit to bank account
- Annual increment in April
- Performance-based bonuses

### 3.2 Benefits Package
- **Health Insurance**: Employee + Family
- **Life Insurance**: 3x annual CTC
- **Accidental Insurance**: 5x annual CTC
- **Provident Fund**: 12% contribution
- **Gratuity**: As per law (after 5 years)

### 3.3 Additional Benefits
- Meal allowance: ₹1,500/month
- Transport allowance: ₹2,000/month
- Internet allowance: ₹500/month (for WFH)
- Mobile allowance: ₹1,000/month

### 3.4 Perks
- Free snacks and beverages
- Friday lunches (sponsored)
- Gym membership subsidy
- Learning and development budget
- Team outings (quarterly)
- Festival bonuses

---

## 4. Time Off and Leave

### 4.1 Leave Types
- **Annual Leave**: 20 days
- **Sick Leave**: 12 days
- **Casual Leave**: 10 days
- **Maternity Leave**: 26 weeks
- **Paternity Leave**: 15 days
- **Compassionate Leave**: 5 days
- **Marriage Leave**: 5 days

### 4.2 Holidays
- National holidays: ~12 per year
- Optional holidays: 3 (choose from list)
- Published annually in advance

### 4.3 Leave Application
- Apply through HRMS portal
- Manager approval required
- Minimum notice varies by leave type
- Check detailed Leave Policy

---

## 5. Workplace Policies

### 5.1 Attendance
- Punctuality expected
- Check-in/out via HRMS or biometric
- 90% minimum attendance required
- See Attendance Policy for details

### 5.2 Dress Code
- Business casual
- Client meetings: Formal attire
- Fridays: Casual (jeans allowed)
- No offensive clothing

### 5.3 Workplace Behavior
- Respectful communication
- No harassment or discrimination
- Professional conduct
- Collaborative attitude

### 5.4 Substance Abuse
- Alcohol-free workplace
- No illegal drugs
- Violation may lead to termination

### 5.5 Confidentiality
- Protect company information
- NDA binding during and after employment
- No sharing of proprietary data
- Secure handling of client information

---

## 6. Professional Development

### 6.1 Learning Opportunities
- Online course subscriptions
- Conference attendance
- Workshop sponsorship
- Certification support
- Internal training programs

### 6.2 Career Growth
- Annual performance reviews
- Development plans
- Mentorship programs
- Internal job postings
- Promotion opportunities

### 6.3 Learning Budget
- ₹25,000 per year per employee
- For courses, certifications, books
- Manager approval required
- Use it or lose it (no carry forward)

---

## 7. Performance Management

### 7.1 Review Cycle
- Annual review in March
- Mid-year check-in in September
- Quarterly 1:1s with manager
- Continuous feedback encouraged

### 7.2 Goals and Objectives
- Set at beginning of year
- SMART goals
- Regular progress tracking
- Adjusted as needed

### 7.3 Ratings
- 5-point scale
- Linked to increment and bonus
- See Performance Review Policy

---

## 8. Health and Safety

### 8.1 Workplace Safety
- First aid kits available
- Fire exits marked
- Emergency procedures displayed
- Drills conducted quarterly

### 8.2 Health Support
- Annual health checkups
- Mental health counseling (confidential)
- Ergonomic assessments
- Wellness programs

### 8.3 Reporting
- Report incidents immediately
- Near-misses also reported
- Investigation conducted
- Corrective actions taken

---

## 9. Technology and Security

### 9.1 IT Equipment
- Company laptop provided
- Mobile phone (if role requires)
- Accessories as needed
- Return upon separation

### 9.2 Data Security
- Use strong passwords
- Enable 2FA
- VPN for remote work
- No sharing of credentials
- Report security incidents

### 9.3 Acceptable Use
- Business use primary
- Limited personal use okay
- No illegal activities
- No offensive content
- Company reserves right to monitor

### 9.4 Social Media
- Personal accounts separate from work
- Don't speak for company
- Respect confidentiality
- Professional conduct online

---

## 10. Termination and Separation

### 10.1 Resignation
- Submit in writing
- Notice period: 2 months (post-probation)
- Exit interview conducted
- Full and final settlement

### 10.2 Termination
- With or without cause
- Notice or payment in lieu
- Exit formalities
- Return company property

### 10.3 Retirement
- Retirement age: 60 years
- Gratuity and PF settlement
- Recognition and farewell

### 10.4 Exit Process
- Resignation acceptance
- Knowledge transfer
- Clearances obtained
- Exit interview
- Final settlement (within 45 days)

---

## Important Contacts

### HR Department
- **Email**: hr@amazatic.com
- **Phone**: +91-80-1234-5678
- **In-person**: 3rd Floor, HR Wing

### IT Support
- **Email**: itsupport@amazatic.com
- **Phone**: +91-80-1234-5679
- **Help Desk**: Ground Floor

### Finance
- **Email**: finance@amazatic.com
- **Phone**: +91-80-1234-5680

### Facilities
- **Email**: facilities@amazatic.com
- **Phone**: +91-80-1234-5681

### Emergency
- **Security**: +91-98765-43212
- **Medical**: +91-98765-43213

---

## Acknowledgment

This handbook provides an overview of company policies. Detailed policies are available on the intranet. The company reserves the right to modify policies at any time.

By joining Amazatic, you acknowledge receipt of this handbook and agree to comply with all policies.

**Have questions?** Contact HR at hr@amazatic.com

---

**Thank you for being part of Amazatic Technologies!**

Together, we'll achieve great things.

**Version**: 4.0 | **Date**: January 2025
"""
}


def generate_policies(output_dir: str = "data/hr_policies"):
    """
    Generate all HR policy documents
    
    Args:
        output_dir: Directory to save policy files
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("HR Policy Document Generation")
    print("=" * 60)
    print(f"\nOutput directory: {output_path.absolute()}")
    print(f"Generating {len(POLICIES)} policy documents...\n")
    
    # Generate each policy
    for filename, content in POLICIES.items():
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        # Calculate size
        size_kb = len(content.encode('utf-8')) / 1024
        
        print(f"✓ Generated: {filename}")
        print(f"  Size: {size_kb:.1f} KB")
        print(f"  Lines: {len(content.splitlines())}")
        print()
    
    print("=" * 60)
    print(f"✓ Successfully generated {len(POLICIES)} policy documents!")
    print(f"✓ Total size: {sum(len(c.encode('utf-8')) for c in POLICIES.values()) / 1024:.1f} KB")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review generated policies")
    print("2. Run: python scripts/ingest_hr_policies.py")
    print("3. Policies will be ingested into Milvus for RAG")
    print()


if __name__ == "__main__":
    generate_policies()
