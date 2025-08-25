#!/usr/bin/env python3
"""
Minecraft Bot Hub - Flask Application
Main web server integrating HTML interface with AI commands system
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import time
import threading
from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
import sys
from dataclasses import asdict

# Import our AI commands system
try:
    from ai_commands.bot_ip_manager import BotIPManager
    from ai_commands.input.bot_ai import BotAI, BotProperties, BotState
    from ai_commands.commands.actions.action_handler import ActionHandler
    AI_SYSTEM_AVAILABLE = True
except ImportError:
    AI_SYSTEM_AVAILABLE = False
    print("Warning: AI commands system not available")

# Import our new management systems
try:
    from server_manager import ServerManager
    from inventory_manager import InventoryManager
    from command_handler import CommandHandler
    MANAGEMENT_SYSTEMS_AVAILABLE = True
except ImportError:
    MANAGEMENT_SYSTEMS_AVAILABLE = False
    print("Warning: Management systems not available")

# Import database system
try:
    from database import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Warning: Database system not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minecraft-bot-hub-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
bot_manager = None
action_handler = None
ai_bots = {}

def generate_default_bot_names(bot_count):
    """Generate default bot names for deployment"""
    gamer_names = [
        'IronMiner', 'WoodCutter', 'StoneBreaker', 'DiamondHunter',
        'NetherExplorer', 'EndVoyager', 'RedstoneMaster', 'Enchanter',
        'PotionBrewer', 'Archer', 'Swordsman', 'Miner',
        'Farmer', 'Builder', 'Explorer', 'Trader',
        'Guardian', 'Scout', 'Navigator', 'Artisan'
    ]
    
    # Return the first N names, or generate generic names if more than 20
    if bot_count <= len(gamer_names):
        return gamer_names[:bot_count]
    else:
        return [f'Bot{i}' for i in range(1, bot_count + 1)]

class BotManager:
    """Manages bot instances and operations"""
    
    def __init__(self):
        self.bots = {}
        self.bot_ips = {}
        self.bot_locations = {}
        
        # Initialize management systems
        self.server_manager = None
        self.inventory_manager = None
        self.command_handler = None
        
        if MANAGEMENT_SYSTEMS_AVAILABLE:
            try:
                self.server_manager = ServerManager()
                self.inventory_manager = InventoryManager()
                self.command_handler = CommandHandler()
                
                # Link the systems together
                self.command_handler.set_server_manager(self.server_manager)
                self.command_handler.set_inventory_manager(self.inventory_manager)
                
                logger.info("Management systems initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing management systems: {e}")
        
        self.initialize_bots()
    
    def initialize_bots(self):
        """Initialize bot instances"""
        if not AI_SYSTEM_AVAILABLE:
            # Create mock bots if AI system unavailable
            self.create_mock_bots()
            return
        
        try:
            # Initialize IP manager
            self.ip_manager = BotIPManager()
            
            # Initialize action handler
            self.action_handler = ActionHandler()
            
            # Create bot instances
            bot_configs = [
                {"name": "Alpha", "camera_type": "main_camera"},
                {"name": "Beta", "camera_type": "thermal_vision"},
                {"name": "Gamma", "camera_type": "depth_sensor"},
                {"name": "Delta", "camera_type": "object_detection"}
            ]
            
            for config in bot_configs:
                bot_props = BotProperties(
                    name=f"Bot {config['name']}",
                    team_members=[f"Bot {c['name']}" for c in bot_configs if c['name'] != config['name']],
                    camera_type=config['camera_type']
                )
                
                bot_ai = BotAI(bot_props)
                self.bots[config['name'].lower()] = bot_ai
                
                # Get current IP from IP manager
                ip_status = self.ip_manager.get_bot_ip(config['name'].lower())
                if ip_status:
                    self.bot_ips[config['name'].lower()] = {
                        'ip': ip_status['ip'],
                        'port': ip_status['port']
                    }
            
            logger.info(f"Initialized {len(self.bots)} AI bots")
            
        except Exception as e:
            logger.error(f"Error initializing AI bots: {e}")
            self.create_mock_bots()
    
    def create_mock_bots(self):
        """Create mock bots for testing"""
        mock_bots = {
            'alpha': {'ip': '192.168.1.101', 'port': 8080, 'status': 'online'},
            'beta': {'ip': '192.168.1.102', 'port': 8081, 'status': 'online'},
            'gamma': {'ip': '192.168.1.103', 'port': 8082, 'status': 'online'},
            'delta': {'ip': '192.168.1.104', 'port': 8083, 'status': 'online'}
        }
        
        for bot_id, config in mock_bots.items():
            self.bots[bot_id] = config
            self.bot_ips[bot_id] = config
            # Initialize simple location tracking for each mock bot
            self.bot_locations[bot_id] = {
                'coordinates': (0, 64, 0),
                'location_name': 'Spawn',
                'last_target': None,
                'last_updated': datetime.now().isoformat(),
                'world': 'survival-1'
            }
        
        logger.info("Created mock bots for testing")
    
    def get_bot_status(self, bot_id):
        """Get status of a specific bot"""
        if bot_id in self.bots:
            if AI_SYSTEM_AVAILABLE and hasattr(self.bots[bot_id], 'get_status_summary'):
                return self.bots[bot_id].get_status_summary()
            else:
                # Mock status
                return {
                    'name': f"Bot {bot_id.capitalize()}",
                    'status': 'online',
                    'ip': self.bot_ips[bot_id]['ip'],
                    'port': self.bot_ips[bot_id]['port']
                }
        return None
    
    def get_all_bot_statuses(self):
        """Get status of all bots"""
        statuses = {}
        for bot_id in self.bots:
            statuses[bot_id] = self.get_bot_status(bot_id)
        return statuses
    
    def execute_command(self, bot_id, command, parameters=None):
        """Execute a command on a specific bot"""
        if bot_id in self.bots:
            if AI_SYSTEM_AVAILABLE and hasattr(self.bots[bot_id], 'execute_action'):
                result = self.bots[bot_id].execute_action(command, parameters or {})
                # Best-effort update of local location tracker based on command semantics
                self._update_location_tracker(bot_id, command, parameters or {})
                return result
            else:
                # Mock command execution
                self._update_location_tracker(bot_id, command, parameters or {})
                return f"Mock command '{command}' executed on {bot_id}"
        return f"Bot {bot_id} not found"

    def _update_location_tracker(self, bot_id, command, parameters):
        """Update simple location/target info for a bot based on high-level commands."""
        try:
            if bot_id not in self.bot_locations:
                self.bot_locations[bot_id] = {
                    'coordinates': (0, 64, 0),
                    'location_name': 'Spawn',
                    'last_target': None,
                    'last_updated': datetime.now().isoformat()
                }
            info = self.bot_locations[bot_id]
            if command == 'warp':
                destination = (parameters or {}).get('destination', '').lower()
                if 'moon city' in destination:
                    # Static coordinates stub for Moon City
                    info['coordinates'] = (1500, 64, 1500)
                    info['location_name'] = 'Moon City'
                    info['world'] = 'survival-2'
                else:
                    info['location_name'] = f"Warp: {(parameters or {}).get('destination', 'unknown')}"
                info['last_target'] = None
                info['last_updated'] = datetime.now().isoformat()
            elif command == 'tp':
                player = (parameters or {}).get('player')
                info['last_target'] = f"player:{player}" if player else 'player:unknown'
                # Keep coordinates as-is; in a real system, this would be updated from the game server
                info['location_name'] = f"Near {player}" if player else 'Teleport'
                info['last_updated'] = datetime.now().isoformat()
            else:
                # Other commands do not affect location tracking in this stub
                pass
            self.bot_locations[bot_id] = info
        except Exception:
            # Non-fatal; do not break command flow
            pass
    
    def rotate_bot_ip(self, bot_id):
        """Rotate IP for a specific bot"""
        if AI_SYSTEM_AVAILABLE and hasattr(self, 'ip_manager'):
            try:
                self.ip_manager.rotate_bot_ip(bot_id)
                # Update local IP cache
                ip_status = self.ip_manager.get_bot_ip(bot_id)
                if ip_status:
                    self.bot_ips[bot_id] = {
                        'ip': ip_status['ip'],
                        'port': ip_status['port']
                    }
                return {"success": True, "message": f"IP rotated for {bot_id}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # Mock IP rotation
            new_ip = f"192.168.1.{100 + hash(bot_id) % 100}"
            new_port = 8000 + hash(bot_id) % 1000
            self.bot_ips[bot_id] = {'ip': new_ip, 'port': new_port}
            return {"success": True, "message": f"Mock IP rotated for {bot_id}"}
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Bot Manager...")
        
        # Cleanup management systems
        if self.server_manager:
            try:
                self.server_manager.cleanup()
                logger.info("Server Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Server Manager: {e}")
        
        if self.inventory_manager:
            try:
                self.inventory_manager.cleanup()
                logger.info("Inventory Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Inventory Manager: {e}")
        
        if self.command_handler:
            try:
                self.command_handler.cleanup()
                logger.info("Command Handler cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Command Handler: {e}")
        
        # Cleanup AI systems if available
        if AI_SYSTEM_AVAILABLE and hasattr(self, 'ip_manager'):
            try:
                self.ip_manager.cleanup()
                logger.info("IP Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up IP Manager: {e}")
        
        logger.info("Bot Manager cleanup completed")
    
    def cleanup_database(self):
        """Cleanup database resources"""
        if db_manager:
            try:
                db_manager.cleanup()
                logger.info("Database Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Database Manager: {e}")

# Initialize managers
bot_manager = BotManager()
db_manager = None

if DATABASE_AVAILABLE:
    try:
        db_manager = DatabaseManager()
        logger.info("Database Manager initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Database Manager: {e}")
        db_manager = None

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/chat')
def chat():
    """Chat/prompt page"""
    # Check if user is authenticated
    session_id = request.cookies.get('session_id')
    if not session_id or not db_manager:
        return redirect(url_for('login'))
    
    session = db_manager.get_session(session_id)
    if not session:
        return redirect(url_for('login'))
    
    return render_template('prompt.html', username=session.username)

# Authentication routes
@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Handle user login"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Authenticate user
    user = db_manager.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Create session
    session_id = db_manager.create_session(
        user.id, 
        user.username, 
        request.remote_addr,
        request.headers.get('User-Agent', '')
    )
    
    if not session_id:
        return jsonify({"error": "Failed to create session"}), 500
    
    response = jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "permissions": user.permissions
        }
    })
    
    # Set session cookie
    response.set_cookie('session_id', session_id, max_age=86400, httponly=True, secure=False)
    return response

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Handle user logout"""
    session_id = request.cookies.get('session_id')
    if session_id and db_manager:
        db_manager.delete_session(session_id)
    
    response = jsonify({"success": True, "message": "Logout successful"})
    response.delete_cookie('session_id')
    return response

@app.route('/auth/check')
def auth_check():
    """Check if user is authenticated"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db_manager:
        return jsonify({"authenticated": False})
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"authenticated": False})
    
    return jsonify({
        "authenticated": True,
        "user": {
            "username": session.username,
            "session_id": session.session_id
        }
    })

@app.route('/api/bots/status')
def get_bot_statuses():
    """API endpoint to get all bot statuses"""
    if bot_manager:
        return jsonify(bot_manager.get_all_bot_statuses())
    return jsonify({"error": "Bot manager not available"})

@app.route('/api/bots/<bot_id>/status')
def get_bot_status(bot_id):
    """API endpoint to get specific bot status"""
    if bot_manager:
        status = bot_manager.get_bot_status(bot_id)
        if status:
            return jsonify(status)
        return jsonify({"error": "Bot not found"}), 404
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/bots/<bot_id>/rotate', methods=['POST'])
def rotate_bot_ip(bot_id):
    """API endpoint to rotate bot IP"""
    if bot_manager:
        result = bot_manager.rotate_bot_ip(bot_id)
        return jsonify(result)
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/bots/<bot_id>/command', methods=['POST'])
def execute_bot_command(bot_id):
    """API endpoint to execute bot command"""
    if bot_manager:
        data = request.get_json()
        command = data.get('command')
        parameters = data.get('parameters', {})
        
        if command:
            result = bot_manager.execute_command(bot_id, command, parameters)
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"error": "No command specified"}), 400
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/bots/<bot_id>/location', methods=['GET'])
def get_bot_location(bot_id):
    """API endpoint to get a bot's current tracked location (stub)."""
    if bot_manager:
        info = getattr(bot_manager, 'bot_locations', {}).get(bot_id)
        if not info:
            return jsonify({"error": "Location not available"}), 404
        x, y, z = info.get('coordinates', (0, 0, 0))
        return jsonify({
            "bot_id": bot_id,
            "location_name": info.get('location_name'),
            "coordinates": {"x": x, "y": y, "z": z},
            "last_target": info.get('last_target'),
            "last_updated": info.get('last_updated'),
            "world": info.get('world')
        })
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/settings/server', methods=['POST'])
def update_server_config():
    """API endpoint to update server configuration"""
    data = request.get_json()
    server_name = data.get('server_name')
    server_port = data.get('server_port')
    server_ip = data.get('server_ip')
    
    # Here you would update the actual server configuration
    # For now, we'll just return success
    
    return jsonify({
        "success": True,
        "message": f"Server configuration updated: {server_name} ({server_ip}:{server_port})"
    })

@app.route('/api/settings/bots/<bot_id>/ping', methods=['POST'])
def ping_bot(bot_id):
    """API endpoint to ping a bot"""
    if bot_manager:
        # Simulate ping
        import random
        ping_time = random.randint(10, 100)
        status = "online" if ping_time < 50 else "slow"
        
        return jsonify({
            "bot_id": bot_id,
            "ping_ms": ping_time,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/settings/bots/<bot_id>/restart', methods=['POST'])
def restart_bot(bot_id):
    """API endpoint to restart a bot"""
    if bot_manager:
        # Simulate restart
        return jsonify({
            "bot_id": bot_id,
            "status": "restarted",
            "message": f"Bot {bot_id} has been restarted",
            "timestamp": datetime.now().isoformat()
        })
    return jsonify({"error": "Bot manager not available"}), 500

@app.route('/api/system/info')
def get_system_info():
    """API endpoint to get system information"""
    system_info = {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": "2h 15m",  # Mock uptime
        "active_connections": len(bot_manager.bots) if bot_manager else 0,
        "system_status": "operational",
        "ai_system_available": AI_SYSTEM_AVAILABLE,
        "management_systems_available": MANAGEMENT_SYSTEMS_AVAILABLE,
        "database_available": DATABASE_AVAILABLE
    }
    
    # Add server manager info if available
    if bot_manager and bot_manager.server_manager:
        server_status = bot_manager.server_manager.get_server_status()
        system_info.update({
            "server_status": server_status,
            "total_players": server_status.get("total_players", 0),
            "online_players": server_status.get("online_players", 0),
            "regions": server_status.get("regions", 0)
        })
    
    # Add inventory manager info if available
    if bot_manager and bot_manager.inventory_manager:
        market_info = bot_manager.inventory_manager.get_market_info()
        system_info.update({
            "total_items": market_info.get("total_items", 0),
            "total_transactions": market_info.get("total_transactions", 0),
            "currency": market_info.get("currency", "Unknown")
        })
    
    # Add command handler info if available
    if bot_manager and bot_manager.command_handler:
        commands = bot_manager.command_handler.get_all_commands()
        system_info.update({
            "total_commands": len(commands),
            "command_categories": list(bot_manager.command_handler.categories.keys())
        })
    
    # Add database info if available
    if db_manager:
        db_stats = db_manager.get_database_stats()
        system_info.update({
            "database_stats": db_stats,
            "total_users": db_stats.get("total_users", 0),
            "total_deployments": db_stats.get("total_deployments", 0),
            "active_deployments": db_stats.get("active_deployments", 0)
        })
    
    return jsonify(system_info)

@app.route('/api/chat/message', methods=['POST'])
def process_chat_message():
    """API endpoint to process chat messages with improved AI responses"""
    data = request.get_json()
    message = data.get('message', '')
    user = data.get('user', 'User')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Process message through AI system if available
    if AI_SYSTEM_AVAILABLE and bot_manager and bot_manager.bots:
        # Use first available bot for AI processing
        first_bot = list(bot_manager.bots.values())[0]
        if hasattr(first_bot, 'process_chat_command'):
            ai_response = first_bot.process_chat_command(message, user)
        else:
            ai_response = generate_enhanced_ai_response(message)
    else:
        ai_response = generate_enhanced_ai_response(message)
    
    return jsonify({
        "success": True,
        "response": ai_response,
        "timestamp": datetime.now().isoformat(),
        "user": user
    })

def generate_enhanced_ai_response(message):
    """Generate enhanced AI responses with coordinates and world detection"""
    message_lower = message.lower()
    
    # Check for coordinate-related queries
    if any(word in message_lower for word in ['spawn', 'respawn', 'location', 'where', 'coordinates', 'cords']):
        return generate_spawn_location_response()
    
    # Check for queue-related queries for Moon City
    if ('queue' in message_lower) and ("moon city" in message_lower or "survival moon city" in message_lower):
        return generate_moon_city_queue_response()
    
    # Check for world-related queries
    if any(word in message_lower for word in ['world', 'big world', 'server', 'area', 'zone']):
        return generate_world_detection_response()
    
    # Check for vision-related queries
    if any(word in message_lower for word in ['vision', 'see', 'camera', 'view', 'stream']):
        return generate_vision_response()
    
    # Check for bot-related queries
    if any(word in message_lower for word in ['bot', 'ai', 'assistant']):
        return generate_bot_status_response()
    
    # Default enhanced responses
    responses = [
        f"I've analyzed your request: {message}. Based on the current bot vision data, I can see that the environment is stable and all systems are operational.",
        f"Interesting question! Let me check the live bot vision streams. I can see multiple data points that suggest we should proceed with your request.",
        f"Based on the real-time analysis from our vision systems, I recommend the following approach for: {message}. The bots are currently detecting optimal conditions for this operation.",
        f"I've processed your prompt through our AI brain. The bot vision streams show that we have sufficient data to provide you with a comprehensive response about: {message}",
        f"Excellent question! Our vision systems are actively monitoring the environment. Based on the live feeds, I can give you detailed insights about: {message}"
    ]
    
    return responses[hash(message) % len(responses)]

def generate_spawn_location_response():
    """Generate response with spawn location and coordinates"""
    return """🎯 **SPAWN LOCATIONS & COORDINATES** 🎯

📍 **Main Spawn**: X: 0, Y: 64, Z: 0 (Central hub)
📍 **Survival World**: X: 1000, Y: 64, Z: 1000 (Resource gathering area)
📍 **Lobby Hub**: X: -1000, Y: 64, Z: -1000 (Social area & games)
📍 **Bedwars Arena**: X: 2000, Y: 64, Z: 2000 (PvP minigame zone)
📍 **Arcade Zone**: X: -2000, Y: 64, Z: -2000 (Fun activities & games)

💡 **Quick Navigation Tips**:
• Use `/spawn` to return to main spawn
• Use `/warp <area>` to teleport between zones
• Use `/home` to set personal spawn points
• Each area has unique features and resources!"""

def generate_moon_city_queue_response():
    """Return Moon City queue status details (stub/static for now)."""
    # Static stub data that could later be wired to a real data source
    queue_info = {
        "location": "Moon City",
        "mode": "Survival",
        "has_queue": True,
        "queue_length": 3,
        "estimated_wait_minutes": 5,
        "last_updated": datetime.now().isoformat()
    }
    return (
        "🛰️ Moon City Queue Status\n\n"
        f"• Location: {queue_info['location']} ({queue_info['mode']})\n"
        f"• Queue present: {'Yes' if queue_info['has_queue'] else 'No'}\n"
        f"• People in queue: {queue_info['queue_length']}\n"
        f"• Estimated wait: {queue_info['estimated_wait_minutes']} min\n"
        f"• Updated: {queue_info['last_updated']}"
    )

@app.route('/api/queues/moon-city', methods=['GET'])
def get_moon_city_queue():
    """API endpoint to fetch Moon City queue status (stub)."""
    data = {
        "location": "Moon City",
        "mode": "Survival",
        "has_queue": True,
        "queue_length": 3,
        "estimated_wait_minutes": 5,
        "last_updated": datetime.now().isoformat()
    }
    return jsonify({
        "success": True,
        "queue": data
    })

def generate_world_detection_response():
    """Generate response for world detection and navigation"""
    return """🌍 **WORLD DETECTION & NAVIGATION** 🌍

🔍 **Server Analysis**: This is a **BIG PUBLIC SERVER** with multiple distinct worlds!

🎮 **Available Worlds**:
• **Survival**: Main gameplay with resource gathering
• **Lobbies**: Social areas and game waiting rooms  
• **Bedwars**: Competitive PvP minigame
• **Arcades**: Fun mini-games and activities

🧭 **Navigation Assistance**:
• **Big World Detected**: Multiple spawn points available
• **Cross-World Travel**: Use warps and portals
• **Area Specialization**: Each zone has unique features
• **Community Hubs**: Lobby areas for meeting players

💬 **Where would you like to go? What would you like to do?**
I can help guide you to the perfect area for your needs!"""

def generate_vision_response():
    """Generate response for vision system queries"""
    return """👁️ **LIVE BOT VISION STREAMS** 👁️

📡 **Active Vision Systems**:
• **Bot Alpha**: Main camera (1920x1080, 30fps)
• **Bot Beta**: Thermal vision (heat detection)
• **Bot Gamma**: Depth sensor (3D mapping)
• **Bot Delta**: Object detection (AI analysis)

🔍 **Real-Time Data**:
• Environmental monitoring active
• Multiple camera feeds streaming
• AI analysis in real-time
• Object and player detection

💡 **Vision Features**:
• Live preview available
• Multi-angle views
• Environmental data (light, temperature, humidity)
• Object count and classification

🎯 **Use the "Show Vision" button to see live feeds!**"""

def generate_bot_status_response():
    """Generate response for bot status queries"""
    return """🤖 **AI BOT STATUS & CAPABILITIES** 🤖

✅ **System Status**: All AI systems operational
🧠 **Brain Integration**: Advanced prompt analysis active
👁️ **Vision Systems**: Multi-camera monitoring enabled
🎯 **Task Management**: Intelligent task prioritization
🌐 **World Awareness**: Server and coordinate detection

💡 **What I Can Do**:
• Analyze your prompts intelligently
• Provide coordinate and location data
• Detect world types and features
• Offer navigation recommendations
• Monitor bot vision streams
• Process complex requests

🚀 **Ready to help with any Minecraft or server-related questions!**"""

# New Management System API Endpoints

@app.route('/api/players/list')
def get_players_list():
    """API endpoint to get list of all players"""
    if bot_manager and bot_manager.server_manager:
        online_players = bot_manager.server_manager.get_online_players()
        all_players = bot_manager.server_manager.get_player_statistics()
        return jsonify({
            "online_players": online_players,
            "statistics": all_players
        })
    return jsonify({"error": "Server manager not available"}), 500

@app.route('/api/players/<player_id>/info')
def get_player_info(player_id):
    """API endpoint to get player information"""
    if bot_manager and bot_manager.server_manager:
        player = bot_manager.server_manager.get_player(player_id)
        if player:
            return jsonify({
                "player": {
                    "uuid": player.uuid,
                    "username": player.username,
                    "display_name": player.display_name,
                    "is_bot": player.is_bot,
                    "coordinates": player.coordinates,
                    "dimension": player.dimension,
                    "health": player.health,
                    "food": player.food,
                    "level": player.level,
                    "team": player.team
                }
            })
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"error": "Server manager not available"}), 500

@app.route('/api/players/<player_id>/coordinates', methods=['POST'])
def update_player_coordinates(player_id):
    """API endpoint to update player coordinates"""
    if bot_manager and bot_manager.server_manager:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        z = data.get('z')
        dimension = data.get('dimension', 'overworld')
        
        if x is not None and y is not None and z is not None:
            bot_manager.server_manager.update_player_coordinates(player_id, (x, y, z), dimension)
            return jsonify({
                "success": True,
                "message": f"Updated coordinates for {player_id} to ({x}, {y}, {z})"
            })
        else:
            return jsonify({"error": "Missing coordinates"}), 400
    return jsonify({"error": "Server manager not available"}), 500

@app.route('/api/inventory/<player_id>')
def get_player_inventory(player_id):
    """API endpoint to get player inventory"""
    if bot_manager and bot_manager.inventory_manager:
        inventory = bot_manager.inventory_manager.get_inventory_contents(player_id)
        balance = bot_manager.inventory_manager.get_balance(player_id)
        return jsonify({
            "inventory": inventory,
            "balance": balance
        })
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/inventory/<player_id>/add', methods=['POST'])
def add_item_to_inventory(player_id):
    """API endpoint to add item to player inventory"""
    if bot_manager and bot_manager.inventory_manager:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        slot_id = data.get('slot_id')
        durability = data.get('durability')
        
        if item_id:
            success = bot_manager.inventory_manager.add_item_to_inventory(
                player_id, item_id, quantity, slot_id, durability
            )
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Added {quantity}x {item_id} to {player_id}'s inventory"
                })
            else:
                return jsonify({"error": "Failed to add item"}), 500
        else:
            return jsonify({"error": "Missing item_id"}), 400
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/inventory/<player_id>/remove', methods=['POST'])
def remove_item_from_inventory(player_id):
    """API endpoint to remove item from player inventory"""
    if bot_manager and bot_manager.inventory_manager:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        slot_id = data.get('slot_id')
        
        if item_id:
            success = bot_manager.inventory_manager.remove_item_from_inventory(
                player_id, item_id, quantity, slot_id
            )
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Removed {quantity}x {item_id} from {player_id}'s inventory"
                })
            else:
                return jsonify({"error": "Failed to remove item"}), 500
        else:
            return jsonify({"error": "Missing item_id"}), 400
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/economy/<player_id>/balance')
def get_player_balance(player_id):
    """API endpoint to get player balance"""
    if bot_manager and bot_manager.inventory_manager:
        balance = bot_manager.inventory_manager.get_balance(player_id)
        stats = bot_manager.inventory_manager.get_player_statistics(player_id)
        return jsonify({
            "balance": balance,
            "statistics": stats
        })
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/economy/<player_id>/add', methods=['POST'])
def add_money_to_player(player_id):
    """API endpoint to add money to player"""
    if bot_manager and bot_manager.inventory_manager:
        data = request.get_json()
        amount = data.get('amount')
        reason = data.get('reason', 'deposit')
        
        if amount is not None:
            success = bot_manager.inventory_manager.add_money(player_id, amount, reason)
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Added {amount} coins to {player_id}"
                })
            else:
                return jsonify({"error": "Failed to add money"}), 500
        else:
            return jsonify({"error": "Missing amount"}), 400
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/economy/transfer', methods=['POST'])
def transfer_money():
    """API endpoint to transfer money between players"""
    if bot_manager and bot_manager.inventory_manager:
        data = request.get_json()
        sender = data.get('sender')
        receiver = data.get('receiver')
        amount = data.get('amount')
        reason = data.get('reason', 'transfer')
        
        if sender and receiver and amount is not None:
            success = bot_manager.inventory_manager.transfer_money(sender, receiver, amount, reason)
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Transferred {amount} coins from {sender} to {receiver}"
                })
            else:
                return jsonify({"error": "Transfer failed"}), 500
        else:
            return jsonify({"error": "Missing sender, receiver, or amount"}), 400
    return jsonify({"error": "Inventory manager not available"}), 500

@app.route('/api/commands/list')
def get_commands_list():
    """API endpoint to get list of all commands"""
    if bot_manager and bot_manager.command_handler:
        commands = bot_manager.command_handler.get_all_commands()
        categories = bot_manager.command_handler.categories
        return jsonify({
            "commands": commands,
            "categories": categories
        })
    return jsonify({"error": "Command handler not available"}), 500

@app.route('/api/commands/<command_name>/info')
def get_command_info(command_name):
    """API endpoint to get command information"""
    if bot_manager and bot_manager.command_handler:
        command_info = bot_manager.command_handler.get_command_info(command_name)
        if command_info:
            return jsonify({"command": command_info})
        return jsonify({"error": "Command not found"}), 404
    return jsonify({"error": "Command handler not available"}), 500

@app.route('/api/commands/execute', methods=['POST'])
def execute_command():
    """API endpoint to execute a command"""
    if bot_manager and bot_manager.command_handler:
        data = request.get_json()
        player_uuid = data.get('player_uuid')
        player_name = data.get('player_name', 'Unknown')
        coordinates = data.get('coordinates', (0, 64, 0))
        dimension = data.get('dimension', 'overworld')
        gamemode = data.get('gamemode', 'survival')
        permissions = data.get('permissions', [])
        command_input = data.get('command')
        
        if player_uuid and command_input:
            result = bot_manager.command_handler.execute_command(
                player_uuid, player_name, coordinates, dimension, gamemode, permissions, command_input
            )
            return jsonify({
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "error": result.error,
                "execution_time": result.execution_time
            })
        else:
            return jsonify({"error": "Missing player_uuid or command"}), 400
    return jsonify({"error": "Command handler not available"}), 500

@app.route('/api/warps/list')
def get_warps_list():
    """API endpoint to get list of all warps"""
    if bot_manager and bot_manager.command_handler:
        warps = bot_manager.command_handler.get_warps()
        return jsonify({"warps": warps})
    return jsonify({"error": "Command handler not available"}), 500

@app.route('/api/homes/<player_id>')
def get_player_homes(player_id):
    """API endpoint to get player homes"""
    if bot_manager and bot_manager.command_handler:
        homes = bot_manager.command_handler.get_player_homes(player_id)
        return jsonify({"homes": homes})
    return jsonify({"error": "Command handler not available"}), 500

@app.route('/api/market/info')
def get_market_info():
    """API endpoint to get market information"""
    if bot_manager and bot_manager.inventory_manager:
        market_info = bot_manager.inventory_manager.get_market_info()
        return jsonify(market_info)
    return jsonify({"error": "Inventory manager not available"}), 500

# Bot Deployment API Endpoints
@app.route('/api/deployments/list')
def get_deployments_list():
    """API endpoint to get list of bot deployments"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    # Get user from session
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "Authentication required"}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    deployments = db_manager.get_user_deployments(session.user_id)
    return jsonify({"deployments": [asdict(deployment) for deployment in deployments]})

@app.route('/api/deployments/create', methods=['POST'])
def create_deployment():
    """API endpoint to create a new bot deployment"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    # Get user from session
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "Authentication required"}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    data = request.get_json()
    
    # Extract bot names from the request
    bot_names = data.get('bot_names', [])
    
    # Generate default bot names if none provided
    if not bot_names:
        bot_names = generate_default_bot_names(data.get('bot_count', 1))
    
    deployment_data = {
        "user_id": session.user_id,
        "deployment_name": data.get('deployment_name', 'New Deployment'),
        "bot_count": data.get('bot_count', 1),
        "server_ip": data.get('server_ip', 'localhost'),
        "server_name": data.get('server_name', 'minecraft'),
        "server_port": data.get('server_port', 25565),
        "bot_names": bot_names,
        "configuration": data.get('configuration', {})
    }
    
    deployment_id = db_manager.create_bot_deployment(deployment_data)
    if deployment_id:
        return jsonify({
            "success": True,
            "message": "Deployment created successfully",
            "deployment_id": deployment_id
        })
    else:
        return jsonify({"error": "Failed to create deployment"}), 500

@app.route('/api/deployments/<deployment_id>/deploy', methods=['POST'])
def deploy_bots(deployment_id):
    """API endpoint to deploy bots"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    # Get user from session
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "Authentication required"}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get deployment
    deployment = db_manager.get_deployment_by_id(int(deployment_id))
    if not deployment:
        return jsonify({"error": "Deployment not found"}), 404
    
    # Check if user owns this deployment
    if deployment.user_id != session.user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Update deployment status to deploying
    db_manager.update_deployment_status(deployment.id, "deploying")
    
    # Here you would integrate with your bot deployment system
    # For now, we'll simulate deployment
    try:
        # Simulate bot deployment
        bot_count = deployment.bot_count
        server_info = f"{deployment.server_ip}:{deployment.server_port}"
        
        # Update status to active after successful deployment
        db_manager.update_deployment_status(deployment.id, "active", started_at=True)
        
        return jsonify({
            "success": True,
            "message": f"Successfully deployed {bot_count} bots to {server_info}",
            "deployment": asdict(deployment)
        })
        
    except Exception as e:
        db_manager.update_deployment_status(deployment.id, "error")
        return jsonify({"error": f"Deployment failed: {str(e)}"}), 500

@app.route('/api/deployments/<deployment_id>/bot-names')
def get_deployment_bot_names(deployment_id):
    """API endpoint to get bot names for a specific deployment"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    # Get user from session
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "Authentication required"}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get deployment
    deployment = db_manager.get_deployment_by_id(int(deployment_id))
    if not deployment:
        return jsonify({"error": "Deployment not found"}), 404
    
    # Check if user owns this deployment
    if deployment.user_id != session.user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Return bot names from deployment configuration
    bot_names = deployment.configuration.get('bot_names', [])
    if not bot_names:
        # Generate default names if none stored
        bot_names = generate_default_bot_names(deployment.bot_count)
    
    return jsonify({
        "success": True,
        "deployment_id": deployment_id,
        "bot_names": bot_names,
        "bot_count": deployment.bot_count
    })

@app.route('/api/deployments/<deployment_id>/stop', methods=['POST'])
def stop_deployment(deployment_id):
    """API endpoint to stop bot deployment"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    # Get user from session
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "Authentication required"}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 401
    
    # Get deployment
    deployment = db_manager.get_deployment_by_id(int(deployment_id))
    if not deployment:
        return jsonify({"error": "Deployment not found"}), 404
    
    # Check if user owns this deployment
    if deployment.user_id != session.user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Update deployment status to stopped
    db_manager.update_deployment_status(deployment.id, "stopped", stopped_at=True)
    
    return jsonify({
        "success": True,
        "message": "Deployment stopped successfully",
        "deployment": asdict(deployment)
    })

# Add new API endpoints for live preview and bot vision
@app.route('/api/bots/vision/live', methods=['GET'])
def get_live_bot_vision():
    """API endpoint to get live bot vision data"""
    if not bot_manager or not bot_manager.bots:
        return jsonify({"error": "No bots available"}), 404
    
    vision_data = {}
    for bot_id, bot in bot_manager.bots.items():
        if hasattr(bot, 'get_vision_data'):
            vision_data[bot_id] = bot.get_vision_data()
        else:
            # Mock vision data for bots without vision system
            vision_data[bot_id] = {
                "camera_type": bot.get('camera_type', 'main_camera'),
                "status": "active",
                "resolution": "1920x1080",
                "fps": 30,
                "timestamp": datetime.now().isoformat(),
                "environment_data": {
                    "light_level": random.randint(0, 15),
                    "temperature": random.uniform(15, 25),
                    "humidity": random.uniform(30, 70),
                    "objects_detected": random.randint(0, 10)
                }
            }
    
    return jsonify({
        "success": True,
        "vision_data": vision_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/bots/vision/stream/<bot_id>', methods=['GET'])
def get_bot_vision_stream(bot_id):
    """API endpoint to get specific bot vision stream"""
    if not bot_manager or bot_id not in bot_manager.bots:
        return jsonify({"error": "Bot not found"}), 404
    
    bot = bot_manager.bots[bot_id]
    if hasattr(bot, 'get_vision_data'):
        vision_data = bot.get_vision_data()
    else:
        vision_data = {
            "camera_type": bot.get('camera_type', 'main_camera'),
            "status": "active",
            "resolution": "1920x1080",
            "fps": 30,
            "timestamp": datetime.now().isoformat(),
            "environment_data": {
                "light_level": random.randint(0, 15),
                "temperature": random.uniform(15, 25),
                "humidity": random.uniform(30, 70),
                "objects_detected": random.randint(0, 10)
            }
        }
    
    return jsonify({
        "success": True,
        "bot_id": bot_id,
        "vision_data": vision_data
    })

@app.route('/api/bots/world/detect', methods=['POST'])
def detect_world_type():
    """API endpoint to detect world type and provide navigation assistance"""
    data = request.get_json()
    coordinates = data.get('coordinates', {})
    dimension = data.get('dimension', 'overworld')
    
    # Analyze world type based on coordinates and dimension
    world_info = analyze_world_type(coordinates, dimension)
    
    return jsonify({
        "success": True,
        "world_info": world_info,
        "recommendations": generate_navigation_recommendations(world_info)
    })

def analyze_world_type(coordinates, dimension):
    """Analyze the type of world based on coordinates and dimension"""
    x, y, z = coordinates.get('x', 0), coordinates.get('y', 0), coordinates.get('z', 0)
    
    world_info = {
        "dimension": dimension,
        "coordinates": coordinates,
        "world_type": "unknown",
        "size_category": "medium",
        "features": [],
        "spawn_points": []
    }
    
    # Determine world type based on dimension
    if dimension == "overworld":
        if abs(x) > 10000 or abs(z) > 10000:
            world_info["world_type"] = "big_world"
            world_info["size_category"] = "large"
            world_info["features"].extend(["multiple_biomes", "diverse_terrain", "extended_networks"])
        elif abs(x) > 5000 or abs(z) > 5000:
            world_info["world_type"] = "medium_world"
            world_info["size_category"] = "medium"
            world_info["features"].extend(["mixed_biomes", "moderate_terrain"])
        else:
            world_info["world_type"] = "small_world"
            world_info["size_category"] = "small"
            world_info["features"].extend(["local_biome", "focused_area"])
    
    elif dimension == "nether":
        world_info["world_type"] = "nether_dimension"
        world_info["features"].extend(["nether_fortresses", "soul_sand_valleys", "crimson_forests"])
    
    elif dimension == "end":
        world_info["world_type"] = "end_dimension"
        world_info["features"].extend(["end_cities", "chorus_fruits", "end_stone"])
    
    # Add spawn points based on world type
    if world_info["world_type"] == "big_world":
        world_info["spawn_points"] = [
            {"name": "Main Spawn", "coordinates": {"x": 0, "y": 64, "z": 0}, "description": "Central spawn point"},
            {"name": "Survival World", "coordinates": {"x": 1000, "y": 64, "z": 1000}, "description": "Survival gameplay area"},
            {"name": "Lobby Hub", "coordinates": {"x": -1000, "y": 64, "z": -1000}, "description": "Main lobby and social area"},
            {"name": "Bedwars Arena", "coordinates": {"x": 2000, "y": 64, "z": 2000}, "description": "Bedwars minigame area"},
            {"name": "Arcade Zone", "coordinates": {"x": -2000, "y": 64, "z": -2000}, "description": "Arcade games and activities"}
        ]
    else:
        world_info["spawn_points"] = [
            {"name": "Main Spawn", "coordinates": {"x": 0, "y": 64, "z": 0}, "description": "Central spawn point"}
        ]
    
    return world_info

def generate_navigation_recommendations(world_info):
    """Generate navigation recommendations based on world analysis"""
    recommendations = []
    
    if world_info["world_type"] == "big_world":
        recommendations.extend([
            "This is a large public server with multiple distinct worlds!",
            "Available areas: Survival, Lobbies, Bedwars, and Arcades",
            "Use /warp or /home commands to navigate between areas",
            "Consider using the lobby hub as a central meeting point",
            "Each area has its own spawn point and unique features"
        ])
    elif world_info["world_type"] == "medium_world":
        recommendations.extend([
            "This is a medium-sized world with good exploration opportunities",
            "Use /spawn to return to the main spawn point",
            "Explore nearby biomes for resources and adventure"
        ])
    else:
        recommendations.extend([
            "This is a focused world area",
            "Use /spawn to return to the main spawn point",
            "Explore the local environment for resources"
        ])
    
    return recommendations

# SocketIO events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Minecraft Bot Hub'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_bot_room')
def handle_join_bot_room(data):
    """Handle joining bot-specific room for updates"""
    bot_id = data.get('bot_id')
    if bot_id:
        join_room(f"bot_{bot_id}")
        emit('joined_room', {'bot_id': bot_id, 'message': f'Joined room for bot {bot_id}'})

@socketio.on('leave_bot_room')
def handle_leave_bot_room(data):
    """Handle leaving bot-specific room"""
    bot_id = data.get('bot_id')
    if bot_id:
        leave_room(f"bot_{bot_id}")
        emit('left_room', {'bot_id': bot_id, 'message': f'Left room for bot {bot_id}'})

def broadcast_bot_updates():
    """Background task to broadcast bot updates"""
    while True:
        try:
            if bot_manager:
                # Get current bot statuses
                statuses = bot_manager.get_all_bot_statuses()
                
                # Broadcast to all connected clients
                socketio.emit('bot_status_update', {
                    'statuses': statuses,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Broadcast individual bot updates
                for bot_id, status in statuses.items():
                    socketio.emit('bot_update', {
                        'bot_id': bot_id,
                        'status': status,
                        'timestamp': datetime.now().isoformat()
                    }, room=f"bot_{bot_id}")
            
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in bot update broadcast: {e}")
            time.sleep(10)

# Start background update thread
update_thread = threading.Thread(target=broadcast_bot_updates, daemon=True)
update_thread.start()

if __name__ == '__main__':
    import signal
    
    def signal_handler(signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        if 'bot_manager' in globals():
            bot_manager.cleanup()
            bot_manager.cleanup_database()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Minecraft Bot Hub Flask Application...")
    logger.info(f"AI System Available: {AI_SYSTEM_AVAILABLE}")
    logger.info(f"Management Systems Available: {MANAGEMENT_SYSTEMS_AVAILABLE}")
    
    # Create templates directory if it doesn't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    try:
        # Run the application
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        if 'bot_manager' in globals():
            bot_manager.cleanup()
    except Exception as e:
        logger.error(f"Application error: {e}")
        if 'bot_manager' in globals():
            bot_manager.cleanup()
        sys.exit(1)