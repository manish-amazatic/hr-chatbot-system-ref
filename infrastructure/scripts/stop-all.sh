#!/bin/bash

# HR Chatbot System - Stop All Services

echo "Stopping all services..."
docker-compose down

echo ""
echo "All services stopped."
echo ""
echo "To remove volumes (delete all data), run:"
echo "  docker-compose down -v"
echo ""
