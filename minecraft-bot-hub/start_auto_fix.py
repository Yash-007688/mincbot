#!/usr/bin/env python3
"""
🚀 Minecraft Bot Hub - Auto-Fix Startup Script
Automatically detects and fixes errors, then starts the application
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_error_detector():
    """Run the error detector to fix any issues"""
    try:
        logger.info("🔍 Running error detector...")
        
        # Import and run error detector
        from error_detector import ErrorDetector
        detector = ErrorDetector()
        
        # Run health check and auto-repair
        health_report = detector.run_health_check()
        if health_report['recommendations']:
            logger.info("🔧 Issues detected, running auto-repair...")
            detector.auto_repair_system()
        
        return detector
    except Exception as e:
        logger.error(f"❌ Error detector failed: {e}")
        return None

def create_fallback_app():
    """Create a fallback app if needed"""
    try:
        fallback_content = '''#!/usr/bin/env python3
"""
Minecraft Bot Hub - Fallback App
Auto-generated fallback application
"""

from flask import Flask, render_template, request, jsonify
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/chat')
def chat():
    return render_template('prompt.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Minecraft Bot Hub"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
        
        with open('app_fallback.py', 'w') as f:
            f.write(fallback_content)
        
        logger.info("📝 Created fallback app")
        return True
    except Exception as e:
        logger.error(f"Failed to create fallback app: {e}")
        return False

def ensure_directories():
    """Ensure all necessary directories exist"""
    try:
        directories = ['templates', 'static', 'logs', 'data']
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
        logger.info("✅ Directories ensured")
        return True
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False

def set_default_environment():
    """Set default environment variables"""
    try:
        defaults = {
            'FLASK_ENV': 'production',
            'DATABASE_FILE': 'minecraft_bot_hub.db',
            'HOST': '0.0.0.0',
            'PORT': '10000',
            'AI_SYSTEM_ENABLED': 'true',
            'MANAGEMENT_SYSTEMS_ENABLED': 'true',
            'DATABASE_ENABLED': 'true'
        }
        
        for key, value in defaults.items():
            if not os.environ.get(key):
                os.environ[key] = value
                logger.info(f"🌍 Set {key} = {value}")
        
        # Generate secret key if not set
        if not os.environ.get('FLASK_SECRET_KEY'):
            import secrets
            secret_key = secrets.token_hex(32)
            os.environ['FLASK_SECRET_KEY'] = secret_key
            logger.info(f"🔑 Generated secret key: {secret_key[:16]}...")
        
        return True
    except Exception as e:
        logger.error(f"Failed to set environment: {e}")
        return False

def start_application():
    """Start the application with fallback options"""
    try:
        port = int(os.environ.get('PORT', 10000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"🚀 Starting application on {host}:{port}")
        
        # Try multiple startup methods in order of preference
        startup_methods = [
            ("Production App", lambda: start_production_app(host, port)),
            ("Simple App", lambda: start_simple_app(host, port)),
            ("Fallback App", lambda: start_fallback_app(host, port))
        ]
        
        for method_name, method_func in startup_methods:
            try:
                logger.info(f"🔄 Attempting to start with {method_name}...")
                if method_func():
                    logger.info(f"✅ Successfully started with {method_name}")
                    return True
            except Exception as e:
                logger.warning(f"⚠️ {method_name} failed: {e}")
                continue
        
        logger.error("❌ All startup methods failed")
        return False
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return False

def start_production_app(host: str, port: int) -> bool:
    """Start with production app"""
    try:
        from app_production import app, socketio
        socketio.run(app, host=host, port=port, debug=False, log_output=True)
        return True
    except Exception as e:
        logger.warning(f"Production app failed: {e}")
        return False

def start_simple_app(host: str, port: int) -> bool:
    """Start with simple app"""
    try:
        from app_simple import app
        app.run(host=host, port=port, debug=False)
        return True
    except Exception as e:
        logger.warning(f"Simple app failed: {e}")
        return False

def start_fallback_app(host: str, port: int) -> bool:
    """Start with fallback app"""
    try:
        from app_fallback import app
        app.run(host=host, port=port, debug=False)
        return True
    except Exception as e:
        logger.warning(f"Fallback app failed: {e}")
        return False

def main():
    """Main auto-fix startup process"""
    logger.info("🚀 Starting Minecraft Bot Hub Auto-Fix Startup...")
    
    try:
        # Step 1: Run error detector
        detector = run_error_detector()
        
        # Step 2: Ensure directories exist
        ensure_directories()
        
        # Step 3: Set default environment
        set_default_environment()
        
        # Step 4: Create fallback app if needed
        create_fallback_app()
        
        # Step 5: Start the application
        if start_application():
            logger.info("🎉 Application started successfully!")
        else:
            logger.error("💥 Failed to start application")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Critical startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)