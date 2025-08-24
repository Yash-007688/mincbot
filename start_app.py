#!/usr/bin/env python3
"""
Bot Vision Commander - Startup Script
Simple script to start the Flask web application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_socketio
        print("✅ Flask dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['templates', 'static/css', 'static/js', 'static/images', 'exports']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created/verified")

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Bot Vision Commander...")
    print("📱 Web interface will be available at: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Import and run the main application
        from bot_vision_commander import app, socketio
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
            except:
                pass  # Browser might not be available
        
        # Start browser thread
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the application
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 Bot Vision Commander - Startup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check if main application file exists
    if not os.path.exists('bot_vision_commander.py'):
        print("❌ bot_vision_commander.py not found!")
        print("Please ensure you're in the correct directory")
        sys.exit(1)
    
    # Start the application
    success = start_application()
    
    if success:
        print("\n✅ Application started successfully")
    else:
        print("\n❌ Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main()