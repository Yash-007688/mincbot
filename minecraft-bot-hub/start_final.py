#!/usr/bin/env python3
"""
🚀 Minecraft Bot Hub - Final Bulletproof Startup Script
Handles all Flask versions and provides multiple fallback options
"""

import os
import sys
import logging
import secrets
from pathlib import Path

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def generate_secret_key():
    """Generate a secure secret key for Flask"""
    return secrets.token_hex(32)

def check_environment():
    """Check and set environment variables with defaults"""
    # Only PORT is truly required for Render
    required_vars = ['PORT']
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your Render dashboard")
        return False
    
    # Set default values for optional variables
    if not os.environ.get('FLASK_SECRET_KEY'):
        secret_key = generate_secret_key()
        os.environ['FLASK_SECRET_KEY'] = secret_key
        logger.info(f"FLASK_SECRET_KEY not set, generated: {secret_key[:16]}...")
    
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
        logger.info("FLASK_ENV not set, defaulting to production")
    
    if not os.environ.get('DATABASE_FILE'):
        os.environ['DATABASE_FILE'] = 'minecraft_bot_hub.db'
        logger.info("DATABASE_FILE not set, defaulting to minecraft_bot_hub.db")
    
    if not os.environ.get('HOST'):
        os.environ['HOST'] = '0.0.0.0'
        logger.info("HOST not set, defaulting to 0.0.0.0")
    
    # Set additional defaults for Render
    if not os.environ.get('AI_SYSTEM_ENABLED'):
        os.environ['AI_SYSTEM_ENABLED'] = 'true'
        logger.info("AI_SYSTEM_ENABLED not set, defaulting to true")
    
    if not os.environ.get('MANAGEMENT_SYSTEMS_ENABLED'):
        os.environ['MANAGEMENT_SYSTEMS_ENABLED'] = 'true'
        logger.info("MANAGEMENT_SYSTEMS_ENABLED not set, defaulting to true")
    
    if not os.environ.get('DATABASE_ENABLED'):
        os.environ['DATABASE_ENABLED'] = 'true'
        logger.info("DATABASE_ENABLED not set, defaulting to true")
    
    logger.info("✅ Environment variables configured successfully")
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    # Check core Flask
    try:
        import flask
        logger.info("✅ Flask available")
    except ImportError:
        missing_deps.append("Flask")
    
    # Check SocketIO (optional)
    try:
        import flask_socketio
        logger.info("✅ Flask-SocketIO available")
    except ImportError:
        logger.warning("⚠️ Flask-SocketIO not available, will use basic Flask")
    
    # Check async libraries (optional)
    try:
        import eventlet
        logger.info("✅ Eventlet available")
    except ImportError:
        try:
            import gevent
            logger.info("✅ Gevent available")
        except ImportError:
            logger.warning("⚠️ No async library available, will use basic Flask")
    
    if missing_deps:
        logger.error(f"❌ Missing critical dependencies: {missing_deps}")
        return False
    
    logger.info("✅ Dependencies check completed")
    return True

def create_directories():
    """Create necessary directories for production"""
    try:
        dirs = ['templates', 'static', 'logs', 'data']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
        logger.info("✅ Production directories created")
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False

def start_socketio_eventlet(app, host, port):
    """Start with SocketIO and Eventlet"""
    try:
        from app_simple import app, socketio
        logger.info("✅ SocketIO app loaded successfully")
        socketio.run(app, host=host, port=port, debug=False, log_output=True)
        return True
    except Exception as e:
        logger.warning(f"SocketIO Eventlet failed: {e}")
        return False

def start_socketio_gevent(app, host, port):
    """Start with SocketIO and Gevent"""
    try:
        os.environ['SOCKETIO_ASYNC_MODE'] = 'gevent'
        from app_simple import app, socketio
        logger.info("✅ SocketIO app with Gevent loaded successfully")
        socketio.run(app, host=host, port=port, debug=False, log_output=True)
        return True
    except Exception as e:
        logger.warning(f"SocketIO Gevent failed: {e}")
        return False

def start_basic_flask(app, host, port):
    """Start with basic Flask (most compatible)"""
    try:
        from app_simple import app
        logger.info("✅ Basic Flask app loaded successfully")
        logger.info("🌐 Starting basic Flask server...")
        
        # Most basic and compatible settings - no version-specific parameters
        app.run(
            host=host,
            port=port,
            debug=False
        )
        return True
    except Exception as e:
        logger.warning(f"Basic Flask failed: {e}")
        return False

def main():
    """Main production startup function"""
    logger.info("🚀 Starting Minecraft Bot Hub Production Server...")
    
    # Check and set environment variables
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        logger.warning("⚠️ Some dependencies missing, will attempt to start with basic Flask")
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Get production configuration
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"📋 Production configuration:")
    logger.info(f"  🌐 Host: {host}")
    logger.info(f"  🔌 Port: {port}")
    logger.info(f"  🏭 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"  🔑 Secret Key: {'Set' if os.environ.get('FLASK_SECRET_KEY') else 'Generated'}")
    logger.info(f"  🤖 AI System: {os.environ.get('AI_SYSTEM_ENABLED', 'true')}")
    logger.info(f"  ⚙️ Management: {os.environ.get('MANAGEMENT_SYSTEMS_ENABLED', 'true')}")
    logger.info(f"  💾 Database: {os.environ.get('DATABASE_ENABLED', 'true')}")
    
    # Try multiple startup methods in order of preference
    startup_methods = [
        ("SocketIO with Eventlet", lambda: start_socketio_eventlet(None, host, port)),
        ("SocketIO with Gevent", lambda: start_socketio_gevent(None, host, port)),
        ("Basic Flask", lambda: start_basic_flask(None, host, port))
    ]
    
    for method_name, method_func in startup_methods:
        try:
            logger.info(f"🔄 Attempting to start with {method_name}...")
            
            if method_name == "SocketIO with Eventlet":
                if start_socketio_eventlet(None, host, port):
                    return  # Success
                continue
            
            elif method_name == "SocketIO with Gevent":
                if start_socketio_gevent(None, host, port):
                    return  # Success
                continue
            
            elif method_name == "Basic Flask":
                if start_basic_flask(None, host, port):
                    return  # Success
                continue
                    
        except Exception as e:
            logger.warning(f"{method_name} failed: {e}")
            continue
    
    # If we get here, all methods failed
    logger.error("❌ All startup methods failed. Cannot start the application.")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error during startup: {e}")
        sys.exit(1)