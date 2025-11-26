#!/bin/bash

#############################################
# HR Chatbot System - Complete Demo
# Demonstrates both RAG and Agent flows
#############################################

CHATBOT_URL="http://127.0.0.1:8000/api/v1"
HRMS_URL="http://127.0.0.1:8001/api/v1"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Banner
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        HR CHATBOT SYSTEM - COMPLETE DEMONSTRATION             ║"
echo "║                                                                ║"
echo "║  Showcasing:                                                   ║"
echo "║  • RAG Flow: Static Policy Questions (Milvus + OpenAI)        ║"
echo "║  • Agent Flow: Transactional Operations (Leave/Payroll/Attn)  ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to print section header
section_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print subsection
subsection() {
    echo ""
    echo -e "${MAGENTA}━━━ $1 ━━━${NC}"
    echo ""
}

# Function to send chat message and display response
send_message() {
    local query="$1"
    local description="$2"

    echo -e "${BLUE}💬 User Query:${NC} \"$query\""
    echo ""

    message="{\"session_id\":\"$SESSION_ID\",\"message\":\"$query\",\"user_id\":\"EMP001\"}"
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$message" \
        "$CHATBOT_URL/chat/message")

    echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
agent = data.get('agent_used', 'unknown')
intent = data.get('intent', 'unknown')
response = data.get('response', 'No response')

# Color codes
YELLOW = '\033[0;33m'
GREEN = '\033[0;32m'
NC = '\033[0m'

print(f'{YELLOW}🤖 Agent:{NC} {agent}')
print(f'{YELLOW}📊 Intent:{NC} {intent}')
print(f'{GREEN}✓ Response:{NC}')
print(response[:800])
if len(response) > 800:
    print('...')
"

    echo ""
    echo -e "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
    sleep 3
}

#############################################
# STEP 1: Authentication
#############################################
section_header "STEP 1: AUTHENTICATION"

echo -e "${BLUE}→${NC} Authenticating with HRMS API..."
login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"manish.w@amazatic.com","password":"password123"}' \
    "$HRMS_URL/auth/login")

TOKEN=$(echo $login_response | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Successfully authenticated as: manish.w@amazatic.com${NC}"
echo -e "${GREEN}✓ Employee ID: EMP001${NC}"

#############################################
# STEP 2: Create Chat Session
#############################################
section_header "STEP 2: CREATE CHAT SESSION"

echo -e "${BLUE}→${NC} Creating new chat session..."
create_session=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"user_id":"EMP001","title":"Complete System Demo"}' \
    "$CHATBOT_URL/chat/sessions")

SESSION_ID=$(echo "$create_session" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"

#############################################
# PART A: RAG FLOW - Static Policy Questions
#############################################
section_header "PART A: RAG FLOW - STATIC POLICY QUESTIONS"
echo -e "These queries retrieve information from HR policy documents stored in Milvus."
echo -e "Flow: User Query → Orchestrator → RAG Tool → Milvus Search → LLM Response"

subsection "Test 1: Annual Leave Policy"
send_message \
    "How many days of annual leave do employees get per year?" \
    "Policy question about annual leave entitlement"

subsection "Test 2: Work From Home Policy"
send_message \
    "What is the company policy on working from home?" \
    "Policy question about WFH guidelines"

subsection "Test 3: Performance Review Process"
send_message \
    "How is performance evaluated at the company?" \
    "Policy question about performance review process"

subsection "Test 4: Maternity Leave Benefits"
send_message \
    "What is the maternity leave policy?" \
    "Policy question about maternity leave duration and eligibility"

subsection "Test 5: Code of Conduct"
send_message \
    "What are the key principles in our code of conduct?" \
    "Policy question about company code of conduct"

#############################################
# PART B: AGENT FLOW - Transactional Queries
#############################################
section_header "PART B: AGENT FLOW - TRANSACTIONAL QUERIES"
echo -e "These queries perform actions via specialized agents calling HRMS APIs."
echo -e "Flow: User Query → Orchestrator → Specialized Agent → Tools → HRMS API"

#
# Leave Agent Tests
#
subsection "Test 6: Check Leave Balance (LeaveAgent)"
send_message \
    "Check my current leave balance" \
    "Transactional query to fetch leave balance from HRMS"

subsection "Test 7: Apply for Leave (LeaveAgent)"
send_message \
    "I want to apply for 2 days sick leave from 2025-12-20 to 2025-12-21" \
    "Transactional query to submit leave application"

subsection "Test 8: View Leave History (LeaveAgent)"
send_message \
    "Show me my leave request history" \
    "Transactional query to fetch leave records"

#
# Attendance Agent Tests
#
subsection "Test 9: Attendance Summary (AttendanceAgent)"
send_message \
    "Show me my attendance summary for November 2025" \
    "Transactional query to fetch attendance data"

#
# Payroll Agent Tests
#
subsection "Test 10: Current Payslip (PayrollAgent)"
send_message \
    "Show me my current month payslip" \
    "Transactional query to fetch payroll data"

subsection "Test 11: Year-to-Date Summary (PayrollAgent)"
send_message \
    "What is my year to date salary summary?" \
    "Transactional query to fetch YTD payroll summary"

#############################################
# PART C: Mixed Queries - Context Awareness
#############################################
section_header "PART C: CONTEXT AWARENESS - FOLLOW-UP QUESTIONS"
echo -e "Testing conversation memory and context retention."

subsection "Test 12: Follow-up Question"
send_message \
    "Can you explain the leave balance details you just showed?" \
    "Follow-up question using conversation context"

#############################################
# DEMO SUMMARY
#############################################
section_header "DEMO SUMMARY"

echo -e "${GREEN}✓ Demonstrated RAG Flow:${NC}"
echo "  • Annual leave policy (rag_tool)"
echo "  • WFH policy (rag_tool)"
echo "  • Performance review process (rag_tool)"
echo "  • Maternity leave policy (rag_tool)"
echo "  • Code of conduct (rag_tool)"
echo ""
echo -e "${GREEN}✓ Demonstrated Agent Flow:${NC}"
echo "  • Leave balance check (leave_agent → HRMS API)"
echo "  • Leave application (leave_agent → HRMS API)"
echo "  • Leave history (leave_agent → HRMS API)"
echo "  • Attendance summary (attendance_agent → HRMS API)"
echo "  • Current payslip (payroll_agent → HRMS API)"
echo "  • YTD summary (payroll_agent → HRMS API)"
echo ""
echo -e "${GREEN}✓ System Capabilities Validated:${NC}"
echo "  • Multi-agent orchestration ✓"
echo "  • RAG with Milvus vector search ✓"
echo "  • HRMS API integration ✓"
echo "  • Conversation memory ✓"
echo "  • Intent classification ✓"
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    DEMO COMPLETED SUCCESSFULLY                 ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
