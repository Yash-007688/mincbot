#!/bin/bash

# 🚀 Minecraft Bot Hub - Startup Script
# This script starts the complete Minecraft Bot Hub system

echo "🚀 Starting Minecraft Bot Hub..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    pip install flask flask-socketio flask-session requests
    echo "✅ Basic dependencies installed"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p templates static/css static/js static/images logs
echo "✅ Directories created"

# Check if database exists
if [ ! -f "minecraft_bot_hub.db" ]; then
    echo "🗄️  Initializing database..."
    python3 -c "from database import DatabaseManager; db = DatabaseManager(); print('✅ Database initialized')"
fi

# Check if all required files exist
echo "🔍 Checking required files..."
required_files=("app.py" "database.py" "server_manager.py" "inventory_manager.py" "command_handler.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing required files: ${missing_files[*]}"
    echo "Please ensure all files are present before starting."
    exit 1
fi

echo "✅ All required files present"

# Start the application
echo "🚀 Starting Flask application..."
echo "🌐 Access the system at: http://localhost:5000"
echo "🔑 Default login: yash / yash"
echo "⏹️  Press Ctrl+C to stop the application"
echo ""

# Run the application
python3 run.py

echo ""
echo "👋 Minecraft Bot Hub stopped"