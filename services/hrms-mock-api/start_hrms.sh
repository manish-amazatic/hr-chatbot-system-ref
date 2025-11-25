#!/bin/bash

# Start HRMS Mock API Service

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "Starting HRMS Mock API..."
echo "PYTHONPATH: $PYTHONPATH"

uvicorn api.main:app --host 127.0.0.1 --port 8001
