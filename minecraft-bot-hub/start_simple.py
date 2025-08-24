#!/usr/bin/env python3
"""
🚀 Minecraft Bot Hub - Simple Production Startup Script for Render
Optimized for Render hosting with minimal dependencies
"""

import os
import sys
import logging
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

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['PORT']
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your Render dashboard")
        return False
    
    logger.info("Environment variables check passed")
    return True

def create_directories():
    """Create necessary directories for production"""
    try:
        dirs = ['templates', 'static', 'logs']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
        logger.info("Production directories created")
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False

def main():
    """Main production startup function"""
    logger.info("🚀 Starting Minecraft Bot Hub Production Server...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Get production configuration
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Production configuration:")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    try:
        # Import and start the production app
        from app_production import app, socketio
        
        logger.info("✅ Production application loaded successfully")
        logger.info("🌐 Starting production server...")
        
        # Start the production server
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            log_output=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import production app: {e}")
        logger.info("Trying to start with basic Flask app...")
        
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
            logger.error(f"Failed to import basic Flask app: {e2}")
            sys.exit(1)
        except Exception as e2:
            logger.error(f"Failed to start basic Flask server: {e2}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to start production server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        sys.exit(1)