#!/bin/bash

# HR Chatbot System - View Logs

if [ -z "$1" ]; then
    echo "Usage: ./logs.sh [service_name]"
    echo ""
    echo "Available services:"
    echo "  - milvus"
    echo "  - hrms-mock-api"
    echo "  - hr-chatbot-service"
    echo "  - hr-chatbot-ui"
    echo "  - all (default)"
    echo ""
    echo "Examples:"
    echo "  ./logs.sh hrms-mock-api"
    echo "  ./logs.sh all"
    exit 1
fi

SERVICE=$1

if [ "$SERVICE" = "all" ]; then
    docker-compose logs -f
else
    docker-compose logs -f $SERVICE
fi
