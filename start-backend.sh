#!/bin/bash
echo "Starting K2 Training API on http://localhost:8000 ..."
source venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
