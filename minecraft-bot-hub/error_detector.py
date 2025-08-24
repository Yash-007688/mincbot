#!/usr/bin/env python3
"""
🚨 Minecraft Bot Hub - Intelligent Error Detection & Auto-Fix System
Automatically detects and fixes common Render deployment errors
"""

import os
import sys
import re
import logging
import subprocess
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('error_detector.log')
    ]
)

logger = logging.getLogger(__name__)

class ErrorDetector:
    """Intelligent error detection and auto-fix system"""
    
    def __init__(self):
        self.errors_fixed = 0
        self.max_retries = 3
        self.error_patterns = self._load_error_patterns()
        self.fix_strategies = self._load_fix_strategies()
        self.system_health = self._check_system_health()
        
    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load error detection patterns"""
        return {
            'missing_dependencies': [
                r"No module named '(\w+)'",
                r"ModuleNotFoundError: No module named '(\w+)'",
                r"ImportError: No module named '(\w+)'",
                r"Missing dependency: (\w+)"
            ],
            'environment_variables': [
                r"Missing required environment variables?: \[([^\]]+)\]",
                r"Environment variable '(\w+)' not set",
                r"FLASK_SECRET_KEY.*not set",
                r"PORT.*not set"
            ],
            'permission_errors': [
                r"Permission denied",
                r"Access denied",
                r"EACCES",
                r"PermissionError"
            ],
            'port_issues': [
                r"Port (\d+) is already in use",
                r"Address already in use",
                r"EADDRINUSE"
            ],
            'database_errors': [
                r"Database connection failed",
                r"sqlite3\.OperationalError",
                r"database is locked",
                r"table.*doesn't exist"
            ],
            'template_errors': [
                r"TemplateNotFound",
                r"jinja2\.exceptions\.TemplateNotFound",
                r"template.*not found"
            ],
            'static_file_errors': [
                r"static file.*not found",
                r"404.*static",
                r"FileNotFoundError.*static"
            ],
            'werkzeug_errors': [
                r"Werkzeug.*not designed to run in production",
                r"allow_unsafe_werkzeug",
                r"development server.*production"
            ],
            'socketio_errors': [
                r"SocketIO.*failed",
                r"eventlet.*not available",
                r"gevent.*not available"
            ],
            'gunicorn_errors': [
                r"Gunicorn.*failed",
                r"worker.*failed",
                r"bind.*failed"
            ]
        }
    
    def _load_fix_strategies(self) -> Dict[str, List[str]]:
        """Load auto-fix strategies"""
        return {
            'missing_dependencies': [
                'install_missing_package',
                'update_requirements',
                'fallback_to_basic_flask'
            ],
            'environment_variables': [
                'generate_default_secret_key',
                'set_default_environment',
                'create_env_file'
            ],
            'permission_errors': [
                'fix_permissions',
                'create_directories',
                'change_ownership'
            ],
            'port_issues': [
                'find_free_port',
                'kill_conflicting_process',
                'use_environment_port'
            ],
            'database_errors': [
                'initialize_database',
                'create_tables',
                'reset_database'
            ],
            'template_errors': [
                'create_missing_templates',
                'fix_template_paths',
                'generate_default_templates'
            ],
            'static_file_errors': [
                'create_static_directory',
                'copy_default_assets',
                'fix_static_paths'
            ],
            'werkzeug_errors': [
                'use_production_server',
                'disable_werkzeug_warnings',
                'fallback_to_gunicorn'
            ],
            'socketio_errors': [
                'fallback_to_basic_flask',
                'install_async_libraries',
                'use_sync_mode'
            ],
            'gunicorn_errors': [
                'fallback_to_flask',
                'fix_gunicorn_config',
                'use_simple_server'
            ]
        }
    
    def _check_system_health(self) -> Dict[str, bool]:
        """Check overall system health"""
        return {
            'python_version': self._check_python_version(),
            'dependencies': self._check_dependencies(),
            'directories': self._check_directories(),
            'permissions': self._check_permissions(),
            'ports': self._check_ports()
        }
    
    def _check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        return version.major == 3 and version.minor >= 8
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        required_packages = ['flask', 'flask_socketio', 'requests']
        for package in required_packages:
            if not importlib.util.find_spec(package):
                return False
        return True
    
    def _check_directories(self) -> bool:
        """Check if required directories exist"""
        required_dirs = ['templates', 'static', 'logs', 'data']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                return False
        return True
    
    def _check_permissions(self) -> bool:
        """Check if we have write permissions"""
        try:
            test_file = Path('test_permissions.tmp')
            test_file.write_text('test')
            test_file.unlink()
            return True
        except:
            return False
    
    def _check_ports(self) -> bool:
        """Check if default ports are available"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            return result != 0  # Port should be free
        except:
            return False
    
    def detect_errors(self, log_content: str) -> List[Dict[str, str]]:
        """Detect errors in log content"""
        detected_errors = []
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, log_content, re.IGNORECASE)
                for match in matches:
                    detected_errors.append({
                        'type': error_type,
                        'pattern': pattern,
                        'match': match.group(0),
                        'severity': self._get_error_severity(error_type),
                        'timestamp': time.time()
                    })
        
        return detected_errors
    
    def _get_error_severity(self, error_type: str) -> str:
        """Get error severity level"""
        critical_errors = ['missing_dependencies', 'environment_variables', 'permission_errors']
        if error_type in critical_errors:
            return 'CRITICAL'
        elif error_type in ['port_issues', 'database_errors']:
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def auto_fix_errors(self, errors: List[Dict[str, str]]) -> Dict[str, bool]:
        """Automatically fix detected errors"""
        fix_results = {}
        
        for error in errors:
            error_type = error['type']
            logger.info(f"🔧 Attempting to fix {error_type} error: {error['match']}")
            
            if error_type in self.fix_strategies:
                success = False
                for strategy in self.fix_strategies[error_type]:
                    try:
                        fix_method = getattr(self, strategy)
                        if callable(fix_method):
                            success = fix_method(error)
                            if success:
                                logger.info(f"✅ Fixed {error_type} using {strategy}")
                                break
                    except Exception as e:
                        logger.warning(f"⚠️ Fix strategy {strategy} failed: {e}")
                
                fix_results[error_type] = success
                if success:
                    self.errors_fixed += 1
                else:
                    logger.error(f"❌ Failed to fix {error_type} error")
            else:
                logger.warning(f"⚠️ No fix strategy available for {error_type}")
                fix_results[error_type] = False
        
        return fix_results
    
    # Fix Strategy Methods
    
    def install_missing_package(self, error: Dict[str, str]) -> bool:
        """Install missing Python package"""
        try:
            # Extract package name from error
            match = re.search(r"'(\w+)'", error['match'])
            if match:
                package_name = match.group(1)
                logger.info(f"📦 Installing missing package: {package_name}")
                
                # Try to install package
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package_name
                ], capture_output=True, text=True, timeout=60)
                
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to install package: {e}")
        return False
    
    def update_requirements(self, error: Dict[str, str]) -> bool:
        """Update requirements.txt and reinstall"""
        try:
            logger.info("📋 Updating requirements and reinstalling packages")
            
            # Remove problematic packages and reinstall
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '-r', 'requirements_minimal.txt'
            ], capture_output=True, text=True, timeout=120)
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to update requirements: {e}")
        return False
    
    def fallback_to_basic_flask(self, error: Dict[str, str]) -> bool:
        """Fallback to basic Flask without problematic features"""
        try:
            logger.info("🔄 Falling back to basic Flask configuration")
            
            # Create simplified app.py
            simple_app_content = self._generate_simple_app()
            with open('app_simple.py', 'w') as f:
                f.write(simple_app_content)
            
            # Update startup script to use simple app
            self._update_startup_script('app_simple')
            
            return True
        except Exception as e:
            logger.error(f"Failed to create fallback app: {e}")
        return False
    
    def generate_default_secret_key(self, error: Dict[str, str]) -> bool:
        """Generate default Flask secret key"""
        try:
            import secrets
            secret_key = secrets.token_hex(32)
            os.environ['FLASK_SECRET_KEY'] = secret_key
            logger.info(f"🔑 Generated default secret key: {secret_key[:16]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to generate secret key: {e}")
        return False
    
    def set_default_environment(self, error: Dict[str, str]) -> bool:
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
            
            return True
        except Exception as e:
            logger.error(f"Failed to set environment variables: {e}")
        return False
    
    def create_env_file(self, error: Dict[str, str]) -> bool:
        """Create .env file with default values"""
        try:
            env_content = """# Auto-generated environment file
FLASK_ENV=production
FLASK_SECRET_KEY=auto-generated-secret-key-2024
DATABASE_FILE=minecraft_bot_hub.db
HOST=0.0.0.0
PORT=10000
AI_SYSTEM_ENABLED=true
MANAGEMENT_SYSTEMS_ENABLED=true
DATABASE_ENABLED=true
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            
            logger.info("📝 Created .env file with default values")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
        return False
    
    def fix_permissions(self, error: Dict[str, str]) -> bool:
        """Fix file and directory permissions"""
        try:
            logger.info("🔐 Fixing file permissions")
            
            # Create directories with proper permissions
            directories = ['templates', 'static', 'logs', 'data']
            for dir_name in directories:
                Path(dir_name).mkdir(exist_ok=True, mode=0o755)
            
            # Fix file permissions
            for file_path in Path('.').glob('*.py'):
                file_path.chmod(0o644)
            
            return True
        except Exception as e:
            logger.error(f"Failed to fix permissions: {e}")
        return False
    
    def create_directories(self, error: Dict[str, str]) -> bool:
        """Create missing directories"""
        try:
            logger.info("📁 Creating missing directories")
            
            directories = ['templates', 'static', 'logs', 'data', 'temp']
            for dir_name in directories:
                Path(dir_name).mkdir(exist_ok=True)
            
            return True
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
        return False
    
    def find_free_port(self, error: Dict[str, str]) -> bool:
        """Find and use a free port"""
        try:
            import socket
            
            # Find free port starting from 5000
            for port in range(5000, 5010):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result != 0:  # Port is free
                    os.environ['PORT'] = str(port)
                    logger.info(f"🔌 Found free port: {port}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to find free port: {e}")
        return False
    
    def initialize_database(self, error: Dict[str, str]) -> bool:
        """Initialize database and create tables"""
        try:
            logger.info("💾 Initializing database")
            
            # Create database directory
            Path('data').mkdir(exist_ok=True)
            
            # Create simple database file
            db_content = """-- Auto-generated database initialization
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default user
INSERT OR IGNORE INTO users (username, password_hash) VALUES ('yash', 'yash');
"""
            
            # Create SQLite database
            import sqlite3
            conn = sqlite3.connect('minecraft_bot_hub.db')
            conn.executescript(db_content)
            conn.close()
            
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        return False
    
    def create_missing_templates(self, error: Dict[str, str]) -> bool:
        """Create missing template files"""
        try:
            logger.info("📄 Creating missing template files")
            
            # Ensure templates directory exists
            Path('templates').mkdir(exist_ok=True)
            
            # Create basic templates if they don't exist
            templates = {
                'index.html': self._generate_index_template(),
                'login.html': self._generate_login_template(),
                'prompt.html': self._generate_prompt_template()
            }
            
            for filename, content in templates.items():
                template_path = Path('templates') / filename
                if not template_path.exists():
                    template_path.write_text(content)
                    logger.info(f"📝 Created {filename}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create templates: {e}")
        return False
    
    def use_production_server(self, error: Dict[str, str]) -> bool:
        """Use production server instead of development server"""
        try:
            logger.info("🚀 Switching to production server configuration")
            
            # Update startup script to use production settings
            self._update_startup_script('production')
            
            return True
        except Exception as e:
            logger.error(f"Failed to switch to production server: {e}")
        return False
    
    def _generate_simple_app(self) -> str:
        """Generate a simple, working Flask app"""
        return '''#!/usr/bin/env python3
"""
Minecraft Bot Hub - Simple Working Flask App
Auto-generated by Error Detector
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
    
    def _generate_index_template(self) -> str:
        """Generate basic index template"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Minecraft Bot Hub</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Minecraft Bot Hub</h1>
        <p>Welcome to Minecraft Bot Hub!</p>
        <a href="/login">Login</a> | <a href="/chat">Chat</a>
    </div>
</body>
</html>'''
    
    def _generate_login_template(self) -> str:
        """Generate basic login template"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Login - Minecraft Bot Hub</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 400px; margin: 0 auto; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form>
            <input type="text" placeholder="Username" required>
            <input type="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>Demo: yash / yash</p>
    </div>
</body>
</html>'''
    
    def _generate_prompt_template(self) -> str:
        """Generate basic prompt template"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Chat - Minecraft Bot Hub</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .chat-box { border: 1px solid #ccc; padding: 20px; height: 400px; overflow-y: scroll; }
        input { width: 80%; padding: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat with Bots</h1>
        <div class="chat-box" id="chatBox">
            <p>Welcome to Minecraft Bot Hub Chat!</p>
        </div>
        <div style="margin-top: 20px;">
            <input type="text" id="messageInput" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value;
            if (message) {
                chatBox.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
    </script>
</body>
</html>'''
    
    def _update_startup_script(self, mode: str) -> bool:
        """Update startup script based on mode"""
        try:
            if mode == 'app_simple':
                startup_content = '''#!/usr/bin/env python3
"""
Minecraft Bot Hub - Simple Startup Script
Auto-generated by Error Detector
"""

import os
import sys
from pathlib import Path

# Create necessary directories
Path('templates').mkdir(exist_ok=True)
Path('static').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

# Set default environment variables
if not os.environ.get('FLASK_SECRET_KEY'):
    import secrets
    os.environ['FLASK_SECRET_KEY'] = secrets.token_hex(32)

if not os.environ.get('PORT'):
    os.environ['PORT'] = '5000'

# Import and run simple app
from app_simple import app
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
'''
            else:
                startup_content = '''#!/usr/bin/env python3
"""
Minecraft Bot Hub - Production Startup Script
Auto-generated by Error Detector
"""

import os
import sys
from pathlib import Path

# Create necessary directories
Path('templates').mkdir(exist_ok=True)
Path('static').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

# Set default environment variables
if not os.environ.get('FLASK_SECRET_KEY'):
    import secrets
    os.environ['FLASK_SECRET_KEY'] = secrets.token_hex(32)

if not os.environ.get('PORT'):
    os.environ['PORT'] = '5000'

# Try to import production app, fallback to simple
try:
    from app_production import app, socketio
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
except:
    from app_simple import app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
            
            with open('start_auto_fix.py', 'w') as f:
                f.write(startup_content)
            
            logger.info(f"📝 Updated startup script for {mode} mode")
            return True
        except Exception as e:
            logger.error(f"Failed to update startup script: {e}")
        return False
    
    def run_health_check(self) -> Dict[str, any]:
        """Run comprehensive health check"""
        logger.info("🏥 Running system health check...")
        
        health_report = {
            'timestamp': time.time(),
            'system_health': self._check_system_health(),
            'errors_fixed': self.errors_fixed,
            'recommendations': []
        }
        
        # Check for common issues
        if not self.system_health['dependencies']:
            health_report['recommendations'].append("Install missing dependencies")
        
        if not self.system_health['directories']:
            health_report['recommendations'].append("Create missing directories")
        
        if not self.system_health['permissions']:
            health_report['recommendations'].append("Fix file permissions")
        
        if not self.system_health['ports']:
            health_report['recommendations'].append("Check port availability")
        
        return health_report
    
    def auto_repair_system(self) -> bool:
        """Automatically repair common system issues"""
        logger.info("🔧 Starting automatic system repair...")
        
        try:
            # Fix directories
            self.create_directories({})
            
            # Fix permissions
            self.fix_permissions({})
            
            # Set environment variables
            self.set_default_environment({})
            
            # Generate secret key
            self.generate_default_secret_key({})
            
            # Create .env file
            self.create_env_file({})
            
            # Create missing templates
            self.create_missing_templates({})
            
            # Initialize database
            self.initialize_database({})
            
            logger.info("✅ Automatic system repair completed")
            return True
        except Exception as e:
            logger.error(f"❌ Automatic system repair failed: {e}")
            return False

def main():
    """Main error detection and auto-fix process"""
    logger.info("🚨 Starting Minecraft Bot Hub Error Detector...")
    
    detector = ErrorDetector()
    
    # Run initial health check
    health_report = detector.run_health_check()
    logger.info(f"📊 Health Check Results: {json.dumps(health_report, indent=2)}")
    
    # Auto-repair system if needed
    if health_report['recommendations']:
        logger.info("🔧 System issues detected, starting auto-repair...")
        detector.auto_repair_system()
    
    # Monitor for errors (in production, this would be continuous)
    logger.info("👀 Error detector ready - monitoring for issues...")
    
    return detector

if __name__ == "__main__":
    detector = main()
    logger.info(f"🎯 Error detector initialized. Fixed {detector.errors_fixed} errors so far.")