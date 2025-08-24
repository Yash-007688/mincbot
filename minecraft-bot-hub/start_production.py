#!/usr/bin/env python3
"""
🚀 Minecraft Bot Hub - Production Startup Script for Render
Optimized for cloud hosting with proper error handling and logging
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
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
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
    
    # Check production server (optional)
    try:
        import gunicorn
        logger.info("✅ Gunicorn available")
    except ImportError:
        logger.warning("⚠️ Gunicorn not available, will use basic Flask")
    
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
    
    try:
        # Import and start the production app
        logger.info("🔄 Attempting to load production application...")
        from app_production import app, socketio
        
        logger.info("✅ Production application loaded successfully")
        logger.info("🌐 Starting production server with SocketIO...")
        
        # Start the production server
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            log_output=True
        )
        
    except ImportError as e:
        logger.warning(f"Production app import failed: {e}")
        logger.info("🔄 Falling back to basic Flask app...")
        
        try:
            # Fallback to basic Flask app
            from app import app
            
            logger.info("✅ Basic Flask app loaded successfully")
            logger.info("🌐 Starting basic Flask server...")
            
            app.run(
                host=host,
                port=port,
                debug=False
            )
            
        except ImportError as e2:
            logger.error(f"❌ Failed to import basic Flask app: {e2}")
            logger.error("Please check that app.py exists and is properly formatted")
            sys.exit(1)
        except Exception as e2:
            logger.error(f"❌ Failed to start basic Flask server: {e2}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Failed to start production server: {e}")
        logger.info("🔄 Attempting to start with basic Flask as fallback...")
        
        try:
            # Final fallback to basic Flask app
            from app import app
            
            logger.info("✅ Basic Flask app loaded successfully")
            logger.info("🌐 Starting basic Flask server in production mode...")
            
            # Use production-safe settings
            app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True,
                allow_unsafe_werkzeug=True  # Allow production use
            )
            
        except ImportError as e3:
            logger.error(f"❌ Failed to import basic Flask app: {e3}")
            sys.exit(1)
        except Exception as e3:
            logger.error(f"❌ Failed to start basic Flask server: {e3}")
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