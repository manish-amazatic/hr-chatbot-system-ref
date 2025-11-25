#!/bin/bash

# HRMS Mock API - Complete Test Suite
# Tests all 28+ endpoints according to IMPROVED_PROMPT.md requirements

set -e  # Exit on error

API_URL="http://127.0.0.1:8001/api/v1"
TOKEN=""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================"
echo "HRMS Mock API - Complete Test Suite"
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
            response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$API_URL$endpoint")
        fi
    elif [ "$method" = "POST" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$API_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$data" "$API_URL$endpoint")
        fi
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$data" "$API_URL$endpoint")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE -H "Authorization: Bearer $TOKEN" "$API_URL$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "  Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo ""
    sleep 0.2
}

echo "================================"
echo "1. HEALTH & SYSTEM ENDPOINTS"
echo "================================"
echo ""

test_endpoint "GET" "/health" "" "Health check endpoint"
test_endpoint "GET" "/system/stats" "" "System statistics endpoint"

echo "================================"
echo "2. AUTHENTICATION ENDPOINTS (5)"
echo "================================"
echo ""

# Login to get token
echo -e "${BLUE}Logging in to get access token...${NC}"
login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"manish.w@amazatic.com","password":"password123"}' \
    "$API_URL/auth/login")

TOKEN=$(echo $login_response | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to get access token. Login response:${NC}"
    echo "$login_response"
    exit 1
fi

echo -e "${GREEN}✓ Successfully obtained access token${NC}"
echo ""

test_endpoint "POST" "/auth/login" '{"email":"manish.w@amazatic.com","password":"password123"}' "Login with email/password"
test_endpoint "POST" "/auth/refresh" "" "Refresh JWT token"
test_endpoint "POST" "/auth/logout" "" "Logout user"
test_endpoint "GET" "/auth/me" "" "Get current user profile"
test_endpoint "GET" "/auth/verify" "" "Verify JWT token"

echo "================================"
echo "3. LEAVE MANAGEMENT ENDPOINTS (10)"
echo "================================"
echo ""

test_endpoint "GET" "/leave/balance" "" "Get current leave balance"
test_endpoint "GET" "/leave/balance/types" "" "Get balance by leave type"
test_endpoint "GET" "/leave/requests" "" "List all leave requests"
test_endpoint "POST" "/leave/requests" '{"leave_type":"casual","start_date":"2025-12-01","end_date":"2025-12-02","reason":"Personal work"}' "Apply for leave"

# Get a leave request ID from the list
leave_id=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/leave/requests" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else 'req001')" 2>/dev/null || echo "req001")

test_endpoint "GET" "/leave/requests/$leave_id" "" "Get specific leave request"
test_endpoint "PUT" "/leave/requests/$leave_id" '{"status":"approved"}' "Update leave request"
test_endpoint "PUT" "/leave/requests/$leave_id/cancel" "" "Cancel leave request"
test_endpoint "GET" "/leave/types" "" "Get available leave types"
test_endpoint "GET" "/leave/history" "" "Get leave history"
test_endpoint "GET" "/leave/calendar" "" "Get team leave calendar"

echo "================================"
echo "4. ATTENDANCE ENDPOINTS (8)"
echo "================================"
echo ""

test_endpoint "GET" "/attendance/today" "" "Get today's attendance"
test_endpoint "GET" "/attendance/records" "" "List attendance records"
test_endpoint "POST" "/attendance/check-in" '{"check_in_time":"09:00:00"}' "Mark check-in"
test_endpoint "POST" "/attendance/check-out" '{"check_out_time":"18:00:00"}' "Mark check-out"

# Get an attendance record ID
att_id=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/attendance/records" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else 'att001')" 2>/dev/null || echo "att001")

test_endpoint "PUT" "/attendance/records/$att_id" '{"status":"present"}' "Update attendance record"
test_endpoint "GET" "/attendance/summary/11/2025" "" "Monthly attendance summary"
test_endpoint "GET" "/attendance/status" "" "Current attendance status"
test_endpoint "GET" "/attendance/report" "" "Generate attendance report"

echo "================================"
echo "5. PAYROLL ENDPOINTS (7)"
echo "================================"
echo ""

test_endpoint "GET" "/payroll/current" "" "Current month payroll"
test_endpoint "GET" "/payroll/records" "" "List all salary slips"

# Get payroll record ID
payroll_id=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/payroll/records" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else 'pay001')" 2>/dev/null || echo "pay001")

test_endpoint "GET" "/payroll/payslip/11/2025" "" "Get specific salary slip"
test_endpoint "GET" "/payroll/records/$payroll_id/pdf" "" "Download salary slip PDF"
test_endpoint "GET" "/payroll/ytd-summary" "" "Year-to-date earnings"
test_endpoint "GET" "/payroll/tax-summary" "" "Tax summary (annual)"
test_endpoint "GET" "/payroll/breakdown" "" "Salary breakdown details"

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
