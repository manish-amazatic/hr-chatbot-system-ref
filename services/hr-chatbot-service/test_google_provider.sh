#!/bin/bash
# Test HR Chatbot Service with Google Provider (Gemini + Google Embeddings)

echo "======================================"
echo "HR Chatbot Service Test - Google Provider"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Testing Health Endpoint${NC}"
curl -s "${BASE_URL}/api/v1/health" | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}2. Creating Auth Token${NC}"
# Create a simple test token (using the login endpoint might require a user, so let's use a test token)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6InRlc3RfdXNlciIsImV4cCI6MTc2NDE0OTA5Nn0.nhVKiWEKuAiKSxLJLjHMcue3OKbLsJjjBGLjYnfi_XI"
echo "Using test token: ${TOKEN:0:50}..."
echo ""
echo ""

echo -e "${BLUE}3. Creating Chat Session${NC}"
SESSION_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/chat/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)

if [ -z "$SESSION_ID" ]; then
  echo "Failed to create session"
  echo "$SESSION_RESPONSE" | python3 -m json.tool
  exit 1
fi

echo "Session created: $SESSION_ID"
echo ""
echo ""

echo -e "${BLUE}4. Testing RAG Query (Uses Google Gemini + Google Embeddings)${NC}"
echo "Query: What is the company's leave policy for annual leave?"
echo ""

CHAT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/chat/${SESSION_ID}/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the company'\''s leave policy for annual leave?"
  }')

echo "$CHAT_RESPONSE" | python3 -m json.tool
echo ""
echo ""

echo -e "${BLUE}5. Testing General Query (Direct LLM - Google Gemini)${NC}"
echo "Query: What day is today?"
echo ""

CHAT_RESPONSE2=$(curl -s -X POST "${BASE_URL}/api/v1/chat/${SESSION_ID}/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What day is today?"
  }')

echo "$CHAT_RESPONSE2" | python3 -m json.tool
echo ""
echo ""

echo -e "${GREEN}======================================"
echo "Test Complete!"
echo "======================================${NC}"
echo ""
echo "Service Configuration:"
echo "  LLM Provider: Google"
echo "  LLM Model: gemini-2.5-flash"
echo "  Embedding Provider: Google"
echo "  Embedding Model: text-embedding-004"
echo "  Embedding Dimensions: 768"
echo ""
