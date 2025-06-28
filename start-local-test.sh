#!/bin/bash

echo "🏥 Starting AI Medical Assistant Web App..."
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Dependencies check passed"

# Function to start backend
start_backend() {
    echo "🐍 Starting Python backend..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Start backend
    echo "🚀 Starting FastAPI server..."
    python main.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React frontend..."
    cd my-app
    
    # Install npm dependencies
    echo "📥 Installing Node.js dependencies..."
    npm install
    
    # Start frontend
    echo "🚀 Starting React development server..."
    npm start &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
}

# Start backend
start_backend

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 15

# Start frontend
start_frontend

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

echo ""
echo "🎉 AI Medical Assistant is now running!"
echo "========================================"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "💡 To stop the application, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping AI Medical Assistant..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    echo "👋 Goodbye!"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for user to stop
wait
