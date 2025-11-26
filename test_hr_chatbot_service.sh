#!/bin/bash

# HR Chatbot Service - Complete Test Suite
# Tests chat endpoints and HRMS API integration

set -e  # Exit on error

CHATBOT_URL="http://127.0.0.1:8000/api/v1"
HRMS_URL="http://127.0.0.1:8001/api/v1"
TOKEN=""
SESSION_ID=""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "HR Chatbot Service - Complete Test"
echo "======================================"
echo ""

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} $description"
    echo "  → $method $endpoint"

    if [ "$method" = "GET" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" "$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$endpoint")
        fi
    elif [ "$method" = "POST" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$data" "$endpoint")
        fi
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE -H "Authorization: Bearer $TOKEN" "$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$body" | python3 -m json.tool 2>/dev/null | head -20 || echo "$body" | head -20
    else
        echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo ""
    sleep 0.5
}

echo "================================"
echo "1. SERVICE HEALTH CHECK"
echo "================================"
echo ""

test_endpoint "GET" "$CHATBOT_URL/health" "" "Check chatbot service health"

echo "================================"
echo "2. AUTHENTICATION"
echo "================================"
echo ""

# Login to HRMS API to get token
echo -e "${BLUE}Logging in to HRMS API...${NC}"
login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"manish.w@amazatic.com","password":"password123"}' \
    "$HRMS_URL/auth/login")

TOKEN=$(echo $login_response | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to get access token. Login response:${NC}"
    echo "$login_response"
    exit 1
fi

echo -e "${GREEN}✓ Successfully obtained access token${NC}"
echo "  Token: ${TOKEN:0:50}..."
echo ""

echo "================================"
echo "3. SESSION MANAGEMENT"
echo "================================"
echo ""

# Create a new session
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} Create new chat session"
echo "  → POST $CHATBOT_URL/chat/sessions"

create_session_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"user_id":"EMP001","title":"Test Session"}' \
    "$CHATBOT_URL/chat/sessions")

http_code=$(echo "$create_session_response" | tail -n1)
body=$(echo "$create_session_response" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    SESSION_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    echo "  Session ID: $SESSION_ID"
    echo "$body" | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
    echo "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
sleep 1

# List sessions
test_endpoint "GET" "$CHATBOT_URL/chat/sessions?user_id=EMP001" "" "List user sessions"

echo "================================"
echo "4. CHAT MESSAGES (LEAVE QUERIES)"
echo "================================"
echo ""

# Test 1: Check leave balance
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} Send message: Check leave balance"
echo "  → POST $CHATBOT_URL/chat/message"

message1='{"session_id":"'$SESSION_ID'","message":"What is my current leave balance?","user_id":"EMP001"}'
chat_response1=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message1" \
    "$CHATBOT_URL/chat/message")

http_code=$(echo "$chat_response1" | tail -n1)
body=$(echo "$chat_response1" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${YELLOW}  Agent Response:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('response', 'No response')[:500])" 2>/dev/null || echo "$body"
    echo ""
    echo -e "${YELLOW}  Agent Used:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('agent_used', 'unknown'))" 2>/dev/null
else
    echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
    echo "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
sleep 2

# Test 2: Apply for leave
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} Send message: Apply for leave"
echo "  → POST $CHATBOT_URL/chat/message"

message2='{"session_id":"'$SESSION_ID'","message":"I want to apply for 2 days sick leave from 2025-12-15 to 2025-12-16","user_id":"EMP001"}'
chat_response2=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message2" \
    "$CHATBOT_URL/chat/message")

http_code=$(echo "$chat_response2" | tail -n1)
body=$(echo "$chat_response2" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${YELLOW}  Agent Response:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('response', 'No response')[:500])" 2>/dev/null || echo "$body"
    echo ""
    echo -e "${YELLOW}  Agent Used:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('agent_used', 'unknown'))" 2>/dev/null
else
    echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
    echo "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
sleep 2

# Test 3: View leave history
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} Send message: View leave history"
echo "  → POST $CHATBOT_URL/chat/message"

message3='{"session_id":"'$SESSION_ID'","message":"Show me my leave request history","user_id":"EMP001"}'
chat_response3=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message3" \
    "$CHATBOT_URL/chat/message")

http_code=$(echo "$chat_response3" | tail -n1)
body=$(echo "$chat_response3" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${YELLOW}  Agent Response:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('response', 'No response')[:500])" 2>/dev/null || echo "$body"
    echo ""
    echo -e "${YELLOW}  Agent Used:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('agent_used', 'unknown'))" 2>/dev/null
else
    echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
    echo "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
sleep 2

echo "================================"
echo "5. CHAT MESSAGES (POLICY QUERY)"
echo "================================"
echo ""

# Test 4: Policy question (RAG)
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} Send message: Policy question"
echo "  → POST $CHATBOT_URL/chat/message"

message4='{"session_id":"'$SESSION_ID'","message":"What is the company policy on remote work?","user_id":"EMP001"}'
chat_response4=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$message4" \
    "$CHATBOT_URL/chat/message")

http_code=$(echo "$chat_response4" | tail -n1)
body=$(echo "$chat_response4" | sed '$d')

if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${YELLOW}  Agent Response:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('response', 'No response')[:500])" 2>/dev/null || echo "$body"
    echo ""
    echo -e "${YELLOW}  Agent Used:${NC}"
    echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print('  ' + data.get('agent_used', 'unknown'))" 2>/dev/null
else
    echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
    echo "  Response: $body"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
sleep 2

echo "================================"
echo "6. GET SESSION MESSAGES"
echo "================================"
echo ""

test_endpoint "GET" "$CHATBOT_URL/chat/sessions/$SESSION_ID/messages" "" "Get session message history"

echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo -e "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
