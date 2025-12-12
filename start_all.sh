#!/bin/bash

# Start backend
echo "Starting backend on port 8000..."
cd /Volumes/SAMSUNG/apps/f1-dash
/Volumes/SAMSUNG/apps/f1-dash/.venv/bin/python -m uvicorn api.app:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on port 5173..."
cd /Volumes/SAMSUNG/apps/f1-dash/frontend
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo "✓ Backend running on http://localhost:8000"
echo "✓ Frontend running on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
