#!/usr/bin/env python3
"""
Production deployment script for Minecraft Bot Hub Flask Application
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

class ProductionDeployer:
    """Production deployment manager"""
    
    def __init__(self):
        self.processes = {}
        self.config = self.load_config()
    
    def load_config(self):
        """Load deployment configuration"""
        return {
            'host': os.environ.get('HOST', '0.0.0.0'),
            'port': int(os.environ.get('PORT', 5000)),
            'workers': int(os.environ.get('WORKERS', 4)),
            'bind': os.environ.get('BIND', '0.0.0.0:5000'),
            'log_level': os.environ.get('LOG_LEVEL', 'info'),
            'max_requests': int(os.environ.get('MAX_REQUESTS', 1000)),
            'timeout': int(os.environ.get('TIMEOUT', 30)),
            'keepalive': int(os.environ.get('KEEPALIVE', 2))
        }
    
    def start_gunicorn(self):
        """Start Gunicorn server"""
        print("🚀 Starting Gunicorn server...")
        
        cmd = [
            'gunicorn',
            '--bind', self.config['bind'],
            '--workers', str(self.config['workers']),
            '--worker-class', 'eventlet',
            '--log-level', self.config['log_level'],
            '--max-requests', str(self.config['max_requests']),
            '--timeout', str(self.config['timeout']),
            '--keepalive', str(self.config['keepalive']),
            '--access-logfile', 'logs/access.log',
            '--error-logfile', 'logs/error.log',
            '--pid', 'gunicorn.pid',
            'app:app'
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.processes['gunicorn'] = process
            print(f"✅ Gunicorn started with PID: {process.pid}")
            print(f"🌐 Server running on: http://{self.config['bind']}")
            
        except Exception as e:
            print(f"❌ Failed to start Gunicorn: {e}")
            return False
        
        return True
    
    def start_nginx(self):
        """Start Nginx reverse proxy (if available)"""
        try:
            # Check if nginx is available
            result = subprocess.run(['nginx', '-v'], capture_output=True, text=True)
            if result.returncode == 0:
                print("🌐 Starting Nginx reverse proxy...")
                
                # Create nginx config
                self.create_nginx_config()
                
                # Start nginx
                subprocess.run(['nginx'], check=True)
                print("✅ Nginx started successfully")
                return True
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ℹ️  Nginx not available, skipping...")
            return False
    
    def create_nginx_config(self):
        """Create Nginx configuration file"""
        nginx_config = f"""
server {{
    listen 80;
    server_name _;
    
    location / {{
        proxy_pass http://{self.config['bind']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
    
    location /static {{
        alias /app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        
        nginx_path = '/etc/nginx/sites-available/minecraft-bot-hub'
        try:
            with open(nginx_path, 'w') as f:
                f.write(nginx_config)
            
            # Enable site
            subprocess.run(['ln', '-sf', nginx_path, '/etc/nginx/sites-enabled/'], check=True)
            subprocess.run(['nginx', '-t'], check=True)
            
        except Exception as e:
            print(f"⚠️  Could not create Nginx config: {e}")
    
    def start_redis(self):
        """Start Redis server (if available)"""
        try:
            # Check if redis is running
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Redis is already running")
                return True
                
        except FileNotFoundError:
            print("ℹ️  Redis not available, skipping...")
            return False
        
        try:
            print("🔴 Starting Redis server...")
            subprocess.run(['redis-server', '--daemonize', 'yes'], check=True)
            print("✅ Redis started successfully")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not start Redis: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring and health checks"""
        print("📊 Starting monitoring system...")
        
        # Start health check script
        health_check_script = """
import time
import requests
import os

while True:
    try:
        response = requests.get('http://localhost:5000/api/system/info', timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {time.strftime('%H:%M:%S')}")
        else:
            print(f"⚠️  Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    time.sleep(60)
"""
        
        try:
            with open('health_check.py', 'w') as f:
                f.write(health_check_script)
            
            process = subprocess.Popen(
                [sys.executable, 'health_check.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes['monitoring'] = process
            print("✅ Monitoring started")
            
        except Exception as e:
            print(f"⚠️  Could not start monitoring: {e}")
    
    def create_systemd_service(self):
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=Minecraft Bot Hub Flask Application
After=network.target

[Service]
Type=exec
User={os.getenv('USER', 'root')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getenv('PATH')}
Environment=FLASK_ENV=production
ExecStart={sys.executable} {os.path.join(os.getcwd(), 'app.py')}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = '/etc/systemd/system/minecraft-bot-hub.service'
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            print(f"✅ Systemd service created: {service_path}")
            print("💡 To enable: sudo systemctl enable minecraft-bot-hub")
            print("💡 To start: sudo systemctl start minecraft-bot-hub")
            
        except PermissionError:
            print("⚠️  Could not create systemd service (requires sudo)")
        except Exception as e:
            print(f"⚠️  Error creating systemd service: {e}")
    
    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting production deployment...")
        print("=" * 60)
        
        # Create necessary directories
        Path('logs').mkdir(exist_ok=True)
        Path('backups').mkdir(exist_ok=True)
        
        # Start services
        success = True
        
        if not self.start_redis():
            print("⚠️  Redis not available, some features may not work")
        
        if not self.start_nginx():
            print("⚠️  Nginx not available, using direct Gunicorn")
        
        if not self.start_gunicorn():
            success = False
        
        if success:
            self.start_monitoring()
            self.create_systemd_service()
            
            print("=" * 60)
            print("✅ Deployment completed successfully!")
            print(f"🌐 Access your application at: http://{self.config['bind']}")
            print("📊 Monitor logs with: tail -f logs/error.log")
            print("🛑 Stop with: Ctrl+C")
            print("=" * 60)
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown()
        else:
            print("❌ Deployment failed!")
            sys.exit(1)
    
    def shutdown(self):
        """Shutdown all processes"""
        print("\n🛑 Shutting down...")
        
        for name, process in self.processes.items():
            try:
                print(f"🛑 Stopping {name}...")
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
        
        # Clean up PID file
        try:
            os.remove('gunicorn.pid')
        except FileNotFoundError:
            pass
        
        print("👋 Goodbye!")

def main():
    """Main entry point"""
    deployer = ProductionDeployer()
    
    try:
        deployer.deploy()
    except KeyboardInterrupt:
        deployer.shutdown()

if __name__ == '__main__':
    main()