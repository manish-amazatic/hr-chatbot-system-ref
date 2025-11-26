#!/bin/bash

# Test RAG Flow with HR Policy Questions
# Tests the complete RAG pipeline with real policy data

CHATBOT_URL="http://127.0.0.1:8000/api/v1"
HRMS_URL="http://127.0.0.1:8001/api/v1"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "======================================"
echo "RAG Flow Test - HR Policy Questions"
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
    -d '{"user_id":"EMP001","title":"Policy Questions - RAG Test"}' \
    "$CHATBOT_URL/chat/sessions")

SESSION_ID=$(echo "$create_session" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"
echo ""

echo "======================================"
echo "TESTING RAG FLOW"
echo "======================================"
echo ""

# Test 1: Leave Policy Question
echo -e "${BLUE}[TEST 1]${NC} Policy Question: Annual Leave"
message1='{"session_id":"'$SESSION_ID'","message":"How many days of annual leave do employees get per year?","user_id":"EMP001"}'
response1=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message1" \
    "$CHATBOT_URL/chat/message")

echo "$response1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Intent:', data.get('intent', 'unknown'))
print('Agent Used:', data.get('agent_used', 'unknown'))
print('\nResponse:')
print(data.get('response', 'No response')[:600])
"

echo ""
echo "---"
sleep 2

# Test 2: WFH Policy Question
echo -e "${BLUE}[TEST 2]${NC} Policy Question: Work From Home"
message2='{"session_id":"'$SESSION_ID'","message":"What is the company policy on working from home?","user_id":"EMP001"}'
response2=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message2" \
    "$CHATBOT_URL/chat/message")

echo "$response2" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Intent:', data.get('intent', 'unknown'))
print('Agent Used:', data.get('agent_used', 'unknown'))
print('\nResponse:')
print(data.get('response', 'No response')[:600])
"

echo ""
echo "---"
sleep 2

# Test 3: Performance Review Policy
echo -e "${BLUE}[TEST 3]${NC} Policy Question: Performance Reviews"
message3='{"session_id":"'$SESSION_ID'","message":"How is performance evaluated at the company?","user_id":"EMP001"}'
response3=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message3" \
    "$CHATBOT_URL/chat/message")

echo "$response3" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Intent:', data.get('intent', 'unknown'))
print('Agent Used:', data.get('agent_used', 'unknown'))
print('\nResponse:')
print(data.get('response', 'No response')[:600])
"

echo ""
echo "---"
sleep 2

# Test 4: Maternity Leave Policy
echo -e "${BLUE}[TEST 4]${NC} Policy Question: Maternity Leave"
message4='{"session_id":"'$SESSION_ID'","message":"What is the maternity leave policy?","user_id":"EMP001"}'
response4=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message4" \
    "$CHATBOT_URL/chat/message")

echo "$response4" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Intent:', data.get('intent', 'unknown'))
print('Agent Used:', data.get('agent_used', 'unknown'))
print('\nResponse:')
print(data.get('response', 'No response')[:600])
"

echo ""
echo "---"
sleep 2

# Test 5: Probation Policy
echo -e "${BLUE}[TEST 5]${NC} Policy Question: Probation Period"
message5='{"session_id":"'$SESSION_ID'","message":"What is the probation period for new employees?","user_id":"EMP001"}'
response5=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message5" \
    "$CHATBOT_URL/chat/message")

echo "$response5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Intent:', data.get('intent', 'unknown'))
print('Agent Used:', data.get('agent_used', 'unknown'))
print('\nResponse:')
print(data.get('response', 'No response')[:600])
"

echo ""
echo "======================================"
echo -e "${GREEN}✓ RAG Flow Test Completed${NC}"
echo "======================================"
