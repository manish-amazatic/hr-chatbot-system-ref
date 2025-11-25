#!/bin/bash

# HR Chatbot System - Run All Tests

set -e

echo "=================================="
echo "Running All Tests"
echo "=================================="

echo ""
echo "1. Testing HRMS Mock API..."
echo "----------------------------"
cd services/hrms-mock-api
source venv/bin/activate 2>/dev/null || true
pytest
cd ../..

echo ""
echo "2. Testing HR Chatbot Service..."
echo "---------------------------------"
cd services/hr-chatbot-service
source venv/bin/activate 2>/dev/null || true
pytest
cd ../..

echo ""
echo "3. Testing HR Chatbot UI..."
echo "---------------------------"
cd services/hr-chatbot-ui
npm test
cd ../..

echo ""
echo "=================================="
echo "✅ All Tests Passed!"
echo "=================================="
echo ""
