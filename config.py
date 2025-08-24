#!/usr/bin/env python3
"""
Configuration file for Minecraft Bot Hub Flask Application
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'minecraft-bot-hub-secret-key-2024'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = Path('flask_session')
    
    # Application Configuration
    APP_NAME = 'Minecraft Bot Hub'
    APP_VERSION = '1.0.0'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # AI System Configuration
    AI_SYSTEM_ENABLED = os.environ.get('AI_SYSTEM_ENABLED', 'True').lower() == 'true'
    AI_CONFIG_PATH = os.environ.get('AI_CONFIG_PATH', 'ai_commands/config')
    
    # Bot Configuration
    BOT_UPDATE_INTERVAL = int(os.environ.get('BOT_UPDATE_INTERVAL', 5))  # seconds
    MAX_BOTS = int(os.environ.get('MAX_BOTS', 10))
    
    # Security Configuration
    ENABLE_HTTPS = os.environ.get('ENABLE_HTTPS', 'False').lower() == 'true'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', '')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', '')
    
    # Database Configuration (optional)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///minecraft_bot_hub.db')
    
    # Redis Configuration (optional)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'minecraft_bot_hub.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'json', 'py'}
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    SOCKETIO_PING_TIMEOUT = int(os.environ.get('SOCKETIO_PING_TIMEOUT', 60))
    SOCKETIO_PING_INTERVAL = int(os.environ.get('SOCKETIO_PING_INTERVAL', 25))
    
    # Monitoring Configuration
    ENABLE_MONITORING = os.environ.get('ENABLE_MONITORING', 'True').lower() == 'true'
    METRICS_INTERVAL = int(os.environ.get('METRICS_INTERVAL', 60))  # seconds
    
    # Backup Configuration
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', 3600))  # 1 hour
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 7))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SOCKETIO_ASYNC_MODE = 'threading'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    ENABLE_HTTPS = True
    RATELIMIT_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])

def create_directories():
    """Create necessary directories"""
    directories = [
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'uploads',
        'logs',
        'backups',
        'flask_session'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def load_environment_variables():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded environment variables from .env file")

# Load environment variables on import
load_environment_variables()