#!/usr/bin/env python3
"""
Startup script for Minecraft Bot Hub Flask Application
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main startup function"""
    try:
        # Import configuration
        from config import get_config, create_directories
        
        # Create necessary directories
        create_directories()
        
        # Get configuration
        config = get_config()
        
        # Set environment variables
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = 'True'
        
        # Import and run the Flask app
        from app import app, socketio
        
        print("=" * 60)
        print("🤖 Minecraft Bot Hub - Flask Application")
        print("=" * 60)
        print(f"🚀 Starting server on {config.HOST}:{config.PORT}")
        print(f"🔧 Debug mode: {config.DEBUG}")
        print(f"🤖 AI System: {'Enabled' if config.AI_SYSTEM_ENABLED else 'Disabled'}")
        print(f"📡 WebSocket: Enabled (SocketIO)")
        print(f"🌐 Access: http://{config.HOST}:{config.PORT}")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the application
        socketio.run(
            app,
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False  # Disable reloader for SocketIO
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Check the configuration and try again")
        sys.exit(1)

if __name__ == '__main__':
    main()