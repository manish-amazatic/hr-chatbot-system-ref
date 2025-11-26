#!/bin/bash

# Test Updated Attendance and Payroll Agents
# Verifies that agents can now call HRMS API successfully

set -e

CHATBOT_URL="http://127.0.0.1:8000/api/v1"
HRMS_URL="http://127.0.0.1:8001/api/v1"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "======================================"
echo "Testing Updated Agents"
echo "======================================"
echo ""

# Login to get token
echo "Logging in to HRMS API..."
login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"manish.w@amazatic.com","password":"password123"}' \
    "$HRMS_URL/auth/login")

TOKEN=$(echo $login_response | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to get access token${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Token obtained${NC}"
echo ""

# Create new session
echo "Creating new chat session..."
create_session=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"user_id":"EMP001","title":"Agent Test"}' \
    "$CHATBOT_URL/chat/sessions")

SESSION_ID=$(echo "$create_session" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"
echo ""

# Test 1: Attendance Query
echo -e "${BLUE}[TEST 1]${NC} Testing AttendanceAgent - Get attendance summary"
message1='{"session_id":"'$SESSION_ID'","message":"Show me my attendance summary for November 2025","user_id":"EMP001"}'
response1=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message1" \
    "$CHATBOT_URL/chat/message")

echo "$response1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Agent Used:', data.get('agent_used'))
print('\nResponse:')
print(data.get('response', 'No response')[:800])
"

echo ""
sleep 2

# Test 2: Payroll Query
echo -e "${BLUE}[TEST 2]${NC} Testing PayrollAgent - Get current payslip"
message2='{"session_id":"'$SESSION_ID'","message":"Show me my current month payslip","user_id":"EMP001"}'
response2=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message2" \
    "$CHATBOT_URL/chat/message")

echo "$response2" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Agent Used:', data.get('agent_used'))
print('\nResponse:')
print(data.get('response', 'No response')[:800])
"

echo ""
sleep 2

# Test 3: YTD Summary
echo -e "${BLUE}[TEST 3]${NC} Testing PayrollAgent - Get YTD summary"
message3='{"session_id":"'$SESSION_ID'","message":"What is my year to date salary summary?","user_id":"EMP001"}'
response3=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message3" \
    "$CHATBOT_URL/chat/message")

echo "$response3" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Agent Used:', data.get('agent_used'))
print('\nResponse:')
print(data.get('response', 'No response')[:800])
"

echo ""

echo "======================================"
echo -e "${GREEN}✓ All agent tests completed!${NC}"
echo "======================================"
