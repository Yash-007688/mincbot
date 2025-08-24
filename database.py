#!/usr/bin/env python3
"""
Database System - Minecraft Bot Hub User Authentication & Bot Deployment
Handles user accounts, sessions, and bot deployment configurations
"""

import sqlite3
import json
import hashlib
import uuid
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """User account information"""
    id: int
    username: str
    password_hash: str
    email: Optional[str]
    role: str  # "admin", "moderator", "user"
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    permissions: List[str]

@dataclass
class BotDeployment:
    """Bot deployment configuration"""
    id: int
    user_id: int
    deployment_name: str
    bot_count: int
    server_ip: str
    server_name: str
    server_port: int
    deployment_status: str  # "pending", "deploying", "active", "stopped", "error"
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    configuration: Dict[str, any]

@dataclass
class UserSession:
    """User session information"""
    session_id: str
    user_id: int
    username: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str

class DatabaseManager:
    """
    Database management system for Minecraft Bot Hub
    Handles users, sessions, and bot deployments
    """
    
    def __init__(self, db_file: str = "minecraft_bot_hub.db"):
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Threading and synchronization
        self.lock = threading.RLock()
        
        # Initialize database
        self.init_database()
        self.create_default_user()
        
        logger.info("Database Manager initialized successfully")
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT,
                        role TEXT DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        permissions TEXT DEFAULT '[]'
                    )
                ''')
                
                # Create bot_deployments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_deployments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        deployment_name TEXT NOT NULL,
                        bot_count INTEGER NOT NULL,
                        server_ip TEXT NOT NULL,
                        server_name TEXT NOT NULL,
                        server_port INTEGER NOT NULL,
                        deployment_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP,
                        stopped_at TIMESTAMP,
                        configuration TEXT DEFAULT '{}',
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Create user_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_user_id ON bot_deployments (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions (expires_at)')
                
                conn.commit()
                logger.info("Database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_default_user(self):
        """Create default user 'yash' with password 'yash'"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_username("yash")
            if existing_user:
                logger.info("Default user 'yash' already exists")
                return
            
            # Create default user
            password_hash = self.hash_password("yash")
            user_data = {
                "username": "yash",
                "password_hash": password_hash,
                "email": "yash@mcfleet.net",
                "role": "admin",
                "permissions": ["admin.all", "user.basic", "bot.deploy", "bot.manage"]
            }
            
            user_id = self.create_user(user_data)
            if user_id:
                logger.info("Default user 'yash' created successfully")
                
                # Create default deployment configuration
                self.create_default_deployment(user_id)
            else:
                logger.error("Failed to create default user")
                
        except Exception as e:
            logger.error(f"Error creating default user: {e}")
    
    def create_default_deployment(self, user_id: int):
        """Create default deployment configuration for yash"""
        try:
            deployment_data = {
                "user_id": user_id,
                "deployment_name": "MCFleet Main",
                "bot_count": 4,
                "server_ip": "play.mcfleet.net",
                "server_name": "mcfleet",
                "server_port": 25565,
                "deployment_status": "pending",
                "configuration": {
                    "auto_restart": True,
                    "max_bots": 10,
                    "deployment_zone": "main",
                    "priority": "high"
                }
            }
            
            deployment_id = self.create_bot_deployment(deployment_data)
            if deployment_id:
                logger.info("Default deployment configuration created successfully")
            else:
                logger.error("Failed to create default deployment")
                
        except Exception as e:
            logger.error(f"Error creating default deployment: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return self.hash_password(password) == password_hash
    
    # User Management Methods
    
    def create_user(self, user_data: Dict[str, any]) -> Optional[int]:
        """Create a new user"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, email, role, permissions)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_data["username"],
                        user_data["password_hash"],
                        user_data.get("email"),
                        user_data.get("role", "user"),
                        json.dumps(user_data.get("permissions", []))
                    ))
                    
                    user_id = cursor.lastrowid
                    conn.commit()
                    
                    logger.info(f"Created user: {user_data['username']} (ID: {user_id})")
                    return user_id
                    
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT id, username, password_hash, email, role, created_at, last_login, is_active, permissions
                        FROM users WHERE username = ?
                    ''', (username,))
                    
                    row = cursor.fetchone()
                    if row:
                        return User(
                            id=row[0],
                            username=row[1],
                            password_hash=row[2],
                            email=row[3],
                            role=row[4],
                            created_at=datetime.fromisoformat(row[5]),
                            last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                            is_active=bool(row[7]),
                            permissions=json.loads(row[8])
                        )
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting user by username: {e}")
                return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT id, username, password_hash, email, role, created_at, last_login, is_active, permissions
                        FROM users WHERE id = ?
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return User(
                            id=row[0],
                            username=row[1],
                            password_hash=row[2],
                            email=row[3],
                            role=row[4],
                            created_at=datetime.fromisoformat(row[5]),
                            last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                            is_active=bool(row[7]),
                            permissions=json.loads(row[8])
                        )
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting user by ID: {e}")
                return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.is_active and self.verify_password(password, user.password_hash):
            # Update last login
            self.update_user_last_login(user.id)
            return user
        return None
    
    def update_user_last_login(self, user_id: int):
        """Update user's last login time"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (user_id,))
                    
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Error updating user last login: {e}")
    
    # Session Management Methods
    
    def create_session(self, user_id: int, username: str, ip_address: str = "", user_agent: str = "") -> Optional[str]:
        """Create a new user session"""
        with self.lock:
            try:
                session_id = str(uuid.uuid4())
                expires_at = datetime.now() + timedelta(hours=24)  # 24 hour expiry
                
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO user_sessions (session_id, user_id, username, expires_at, ip_address, user_agent)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (session_id, user_id, username, expires_at.isoformat(), ip_address, user_agent))
                    
                    conn.commit()
                    
                    logger.info(f"Created session for user: {username}")
                    return session_id
                    
            except Exception as e:
                logger.error(f"Error creating session: {e}")
                return None
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT session_id, user_id, username, created_at, expires_at, ip_address, user_agent
                        FROM user_sessions WHERE session_id = ?
                    ''', (session_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        session = UserSession(
                            session_id=row[0],
                            user_id=row[1],
                            username=row[2],
                            created_at=datetime.fromisoformat(row[3]),
                            expires_at=datetime.fromisoformat(row[4]),
                            ip_address=row[5],
                            user_agent=row[6]
                        )
                        
                        # Check if session is expired
                        if datetime.now() > session.expires_at:
                            self.delete_session(session_id)
                            return None
                        
                        return session
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting session: {e}")
                return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM user_sessions WHERE session_id = ?', (session_id,))
                    conn.commit()
                    
                    logger.info(f"Deleted session: {session_id}")
                    return True
                    
            except Exception as e:
                logger.error(f"Error deleting session: {e}")
                return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP')
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} expired sessions")
                        
            except Exception as e:
                logger.error(f"Error cleaning up expired sessions: {e}")
    
    # Bot Deployment Methods
    
    def create_bot_deployment(self, deployment_data: Dict[str, any]) -> Optional[int]:
        """Create a new bot deployment"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO bot_deployments (user_id, deployment_name, bot_count, server_ip, server_name, server_port, configuration)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        deployment_data["user_id"],
                        deployment_data["deployment_name"],
                        deployment_data["bot_count"],
                        deployment_data["server_ip"],
                        deployment_data["server_name"],
                        deployment_data["server_port"],
                        json.dumps(deployment_data.get("configuration", {}))
                    ))
                    
                    deployment_id = cursor.lastrowid
                    conn.commit()
                    
                    logger.info(f"Created bot deployment: {deployment_data['deployment_name']} (ID: {deployment_id})")
                    return deployment_id
                    
            except Exception as e:
                logger.error(f"Error creating bot deployment: {e}")
                return None
    
    def get_user_deployments(self, user_id: int) -> List[BotDeployment]:
        """Get all deployments for a user"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT id, user_id, deployment_name, bot_count, server_ip, server_name, server_port, 
                               deployment_status, created_at, started_at, stopped_at, configuration
                        FROM bot_deployments WHERE user_id = ? ORDER BY created_at DESC
                    ''', (user_id,))
                    
                    deployments = []
                    for row in cursor.fetchall():
                        deployment = BotDeployment(
                            id=row[0],
                            user_id=row[1],
                            deployment_name=row[2],
                            bot_count=row[3],
                            server_ip=row[4],
                            server_name=row[5],
                            server_port=row[6],
                            deployment_status=row[7],
                            created_at=datetime.fromisoformat(row[8]),
                            started_at=datetime.fromisoformat(row[9]) if row[9] else None,
                            stopped_at=datetime.fromisoformat(row[10]) if row[10] else None,
                            configuration=json.loads(row[11])
                        )
                        deployments.append(deployment)
                    
                    return deployments
                    
            except Exception as e:
                logger.error(f"Error getting user deployments: {e}")
                return []
    
    def get_deployment_by_id(self, deployment_id: int) -> Optional[BotDeployment]:
        """Get deployment by ID"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT id, user_id, deployment_name, bot_count, server_ip, server_name, server_port, 
                               deployment_status, created_at, started_at, stopped_at, configuration
                        FROM bot_deployments WHERE id = ?
                    ''', (deployment_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return BotDeployment(
                            id=row[0],
                            user_id=row[1],
                            deployment_name=row[2],
                            bot_count=row[3],
                            server_ip=row[4],
                            server_name=row[5],
                            server_port=row[6],
                            deployment_status=row[7],
                            created_at=datetime.fromisoformat(row[8]),
                            started_at=datetime.fromisoformat(row[9]) if row[9] else None,
                            stopped_at=datetime.fromisoformat(row[10]) if row[10] else None,
                            configuration=json.loads(row[11])
                        )
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting deployment by ID: {e}")
                return None
    
    def update_deployment_status(self, deployment_id: int, status: str, started_at: bool = False, stopped_at: bool = False):
        """Update deployment status"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    if started_at:
                        cursor.execute('''
                            UPDATE bot_deployments 
                            SET deployment_status = ?, started_at = CURRENT_TIMESTAMP 
                            WHERE id = ?
                        ''', (status, deployment_id))
                    elif stopped_at:
                        cursor.execute('''
                            UPDATE bot_deployments 
                            SET deployment_status = ?, stopped_at = CURRENT_TIMESTAMP 
                            WHERE id = ?
                        ''', (status, deployment_id))
                    else:
                        cursor.execute('''
                            UPDATE bot_deployments 
                            SET deployment_status = ? 
                            WHERE id = ?
                        ''', (status, deployment_id))
                    
                    conn.commit()
                    
                    logger.info(f"Updated deployment {deployment_id} status to: {status}")
                    
            except Exception as e:
                logger.error(f"Error updating deployment status: {e}")
    
    def delete_deployment(self, deployment_id: int) -> bool:
        """Delete a deployment"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM bot_deployments WHERE id = ?', (deployment_id,))
                    conn.commit()
                    
                    logger.info(f"Deleted deployment: {deployment_id}")
                    return True
                    
            except Exception as e:
                logger.error(f"Error deleting deployment: {e}")
                return False
    
    # Utility Methods
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT id, username, password_hash, email, role, created_at, last_login, is_active, permissions
                        FROM users ORDER BY created_at DESC
                    ''')
                    
                    users = []
                    for row in cursor.fetchall():
                        user = User(
                            id=row[0],
                            username=row[1],
                            password_hash=row[2],
                            email=row[3],
                            role=row[4],
                            created_at=datetime.fromisoformat(row[5]),
                            last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                            is_active=bool(row[7]),
                            permissions=json.loads(row[8])
                        )
                        users.append(user)
                    
                    return users
                    
            except Exception as e:
                logger.error(f"Error getting all users: {e}")
                return []
    
    def get_database_stats(self) -> Dict[str, any]:
        """Get database statistics"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    # Count users
                    cursor.execute('SELECT COUNT(*) FROM users')
                    user_count = cursor.fetchone()[0]
                    
                    # Count active users
                    cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                    active_user_count = cursor.fetchone()[0]
                    
                    # Count deployments
                    cursor.execute('SELECT COUNT(*) FROM bot_deployments')
                    deployment_count = cursor.fetchone()[0]
                    
                    # Count active deployments
                    cursor.execute('SELECT COUNT(*) FROM bot_deployments WHERE deployment_status = "active"')
                    active_deployment_count = cursor.fetchone()[0]
                    
                    # Count sessions
                    cursor.execute('SELECT COUNT(*) FROM user_sessions')
                    session_count = cursor.fetchone()[0]
                    
                    return {
                        "total_users": user_count,
                        "active_users": active_user_count,
                        "total_deployments": deployment_count,
                        "active_deployments": active_deployment_count,
                        "active_sessions": session_count,
                        "database_file": str(self.db_file),
                        "last_updated": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Error getting database stats: {e}")
                return {}
    
    def cleanup(self):
        """Cleanup database resources"""
        logger.info("Cleaning up Database Manager...")
        self.cleanup_expired_sessions()
        logger.info("Database Manager cleanup completed")

# Example usage
if __name__ == "__main__":
    try:
        # Create database manager instance
        db_manager = DatabaseManager()
        
        # Print database stats
        print("=== Database Statistics ===")
        stats = db_manager.get_database_stats()
        print(json.dumps(stats, indent=2))
        
        # Test authentication
        print("\n=== Testing Authentication ===")
        user = db_manager.authenticate_user("yash", "yash")
        if user:
            print(f"✅ Authentication successful for user: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Permissions: {user.permissions}")
        else:
            print("❌ Authentication failed")
        
        # Test session creation
        if user:
            print("\n=== Testing Session Creation ===")
            session_id = db_manager.create_session(user.id, user.username, "127.0.0.1", "Test Agent")
            if session_id:
                print(f"✅ Session created: {session_id}")
                
                # Test session retrieval
                session = db_manager.get_session(session_id)
                if session:
                    print(f"✅ Session retrieved for user: {session.username}")
                else:
                    print("❌ Session retrieval failed")
            else:
                print("❌ Session creation failed")
        
        # Test deployment retrieval
        if user:
            print("\n=== Testing Deployment Retrieval ===")
            deployments = db_manager.get_user_deployments(user.id)
            print(f"Found {len(deployments)} deployments for user {user.username}")
            for deployment in deployments:
                print(f"  - {deployment.deployment_name}: {deployment.bot_count} bots on {deployment.server_ip}:{deployment.server_port}")
        
        print("\n=== Database test completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db_manager' in locals():
            db_manager.cleanup()