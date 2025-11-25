#!/bin/bash

# HR Chatbot System - Development Startup Script

set -e

echo "=================================="
echo "HR Chatbot System - Starting Services"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and configure it."
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️  JWT_SECRET_KEY not set, using default (insecure!)"
fi

echo ""
echo "Starting services with Docker Compose..."
echo ""

# Start services
docker-compose up -d --build

echo ""
echo "=================================="
echo "Services started successfully!"
echo "=================================="
echo ""
echo "Access URLs:"
echo "  Frontend:     http://localhost:3000"
echo "  Chatbot API:  http://localhost:8000/docs"
echo "  HRMS API:     http://localhost:8001/docs"
echo "  Milvus:       localhost:19530"
echo ""
echo "Default credentials:"
echo "  Email:    manish.w@amazatic.com"
echo "  Password: password123"
echo ""
