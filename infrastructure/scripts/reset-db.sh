#!/bin/bash

# HR Chatbot System - Reset Databases

echo "⚠️  This will delete all data!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Stopping services..."
docker-compose down

echo ""
echo "Removing volumes..."
docker volume rm hr-chatbot-system_hrms_data 2>/dev/null || true
docker volume rm hr-chatbot-system_chatbot_data 2>/dev/null || true
docker volume rm hr-chatbot-system_milvus_data 2>/dev/null || true

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "Seeding HRMS database..."
docker-compose exec hrms-mock-api python scripts/seed_data.py

echo ""
echo "Generating HR policies..."
docker-compose exec hr-chatbot-service python scripts/generate_hr_policies.py

echo ""
echo "Ingesting to Milvus..."
docker-compose exec hr-chatbot-service python scripts/ingest_to_milvus.py

echo ""
echo "✅ Databases reset successfully!"
echo ""
