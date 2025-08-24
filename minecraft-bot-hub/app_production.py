#!/usr/bin/env python3
"""
Minecraft Bot Hub - Production Flask Application for Render
Main web server integrating HTML interface with AI commands system
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time
import threading
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Configure for production
os.environ['FLASK_ENV'] = 'production'

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

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'minecraft-bot-hub-secret-key-2024')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
bot_manager = None
action_handler = None
ai_bots = {}
db_manager = None

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
            
            # Create some default bots
            bot_properties = [
                BotProperties("Alpha", "miner", "overworld"),
                BotProperties("Beta", "farmer", "overworld"),
                BotProperties("Gamma", "explorer", "nether"),
                BotProperties("Delta", "builder", "overworld")
            ]
            
            for props in bot_properties:
                bot = BotAI(props)
                self.bots[props.name] = bot
                self.bot_ips[props.name] = self.ip_manager.get_next_ip()
            
            logger.info(f"Initialized {len(self.bots)} AI bots")
            
        except Exception as e:
            logger.error(f"Error initializing AI bots: {e}")
            self.create_mock_bots()
    
    def create_mock_bots(self):
        """Create mock bots for testing"""
        mock_bots = ["Alpha", "Beta", "Gamma", "Delta"]
        for bot_name in mock_bots:
            self.bots[bot_name] = {"name": bot_name, "status": "offline"}
            self.bot_ips[bot_name] = "192.168.1.100"
        
        logger.info("Created mock bots for testing")
    
    def get_bot_status(self):
        """Get status of all bots"""
        status = {}
        for name, bot in self.bots.items():
            if isinstance(bot, dict):
                status[name] = bot.get("status", "unknown")
            else:
                status[name] = "online" if hasattr(bot, 'is_active') and bot.is_active else "offline"
        return status
    
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
        global db_manager
        if db_manager:
            try:
                db_manager.cleanup()
                logger.info("Database Manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Database Manager: {e}")

# Initialize global instances
def initialize_app():
    """Initialize the application"""
    global bot_manager, db_manager
    
    try:
        # Initialize database manager
        if DATABASE_AVAILABLE:
            db_manager = DatabaseManager()
            logger.info("Database Manager initialized")
        
        # Initialize bot manager
        bot_manager = BotManager()
        logger.info("Bot Manager initialized")
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing application: {e}")

# Initialize on startup
initialize_app()

# Routes
@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/chat')
def chat():
    """Chat interface - requires authentication"""
    # Check if user is authenticated via session cookie
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect('/login')
    
    if not db_manager:
        return redirect('/login')
    
    # Verify session
    session = db_manager.get_session(session_id)
    if not session:
        return redirect('/login')
    
    return render_template('prompt.html')

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
    session = db_manager.create_session(user.id, user.username)
    if not session:
        return jsonify({"error": "Failed to create session"}), 500
    
    # Update last login
    db_manager.update_user_last_login(user.id)
    
    response = jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    })
    
    # Set session cookie
    response.set_cookie(
        'session_id',
        session.session_id,
        max_age=86400,  # 24 hours
        httponly=True,
        secure=True,
        samesite='Lax'
    )
    
    return response

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Handle user logout"""
    if not db_manager:
        return jsonify({"error": "Database system not available"}), 500
    
    session_id = request.cookies.get('session_id')
    if session_id:
        db_manager.delete_session(session_id)
    
    response = jsonify({"success": True, "message": "Logout successful"})
    response.delete_cookie('session_id')
    return response

@app.route('/auth/check')
def auth_check():
    """Check authentication status"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db_manager:
        return jsonify({"authenticated": False}), 401
    
    session = db_manager.get_session(session_id)
    if not session:
        return jsonify({"authenticated": False}), 401
    
    return jsonify({"authenticated": True, "username": session.username})

# API Routes
@app.route('/api/system/info')
def get_system_info():
    """Get system information"""
    try:
        # Get bot status
        bot_status = {}
        if bot_manager:
            bot_status = bot_manager.get_bot_status()
        
        # Get management system stats
        management_stats = {}
        if bot_manager and bot_manager.server_manager:
            management_stats['players'] = len(bot_manager.server_manager.players)
            management_stats['bots'] = len(bot_manager.server_manager.bots)
            management_stats['regions'] = len(bot_manager.server_manager.regions)
        
        if bot_manager and bot_manager.inventory_manager:
            management_stats['items'] = len(bot_manager.inventory_manager.items)
            management_stats['inventories'] = len(bot_manager.inventory_manager.inventories)
        
        if bot_manager and bot_manager.command_handler:
            management_stats['commands'] = len(bot_manager.command_handler.commands)
        
        # Get database stats
        db_stats = {}
        if db_manager:
            db_stats['users'] = len(db_manager.get_all_users())
            db_stats['deployments'] = len(db_manager.get_all_deployments())
            db_stats['sessions'] = len(db_manager.get_all_sessions())
        
        return jsonify({
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "ai_system_available": AI_SYSTEM_AVAILABLE,
            "management_systems_available": MANAGEMENT_SYSTEMS_AVAILABLE,
            "database_available": DATABASE_AVAILABLE,
            "bot_status": bot_status,
            "management_stats": management_stats,
            "database_stats": db_stats,
            "uptime": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({"error": str(e)}), 500

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
        "message": f"Deployment {deployment.deployment_name} stopped successfully"
    })

# Management System API Endpoints
@app.route('/api/players/list')
def get_players_list():
    """API endpoint to get list of players"""
    if not bot_manager or not bot_manager.server_manager:
        return jsonify({"error": "Server manager not available"}), 500
    
    players = bot_manager.server_manager.get_all_players()
    return jsonify({"players": [asdict(player) for player in players]})

@app.route('/api/players/<player_id>/info')
def get_player_info(player_id):
    """API endpoint to get player information"""
    if not bot_manager or not bot_manager.server_manager:
        return jsonify({"error": "Server manager not available"}), 500
    
    player = bot_manager.server_manager.get_player(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    return jsonify({"player": asdict(player)})

@app.route('/api/players/<player_id>/coordinates')
def get_player_coordinates(player_id):
    """API endpoint to get player coordinates"""
    if not bot_manager or not bot_manager.server_manager:
        return jsonify({"error": "Server manager not available"}), 500
    
    player = bot_manager.server_manager.get_player(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    return jsonify({
        "player_id": player_id,
        "coordinates": player.coordinates,
        "dimension": player.dimension
    })

@app.route('/api/inventory/<player_id>')
def get_player_inventory(player_id):
    """API endpoint to get player inventory"""
    if not bot_manager or not bot_manager.inventory_manager:
        return jsonify({"error": "Inventory manager not available"}), 500
    
    inventory = bot_manager.inventory_manager.get_player_inventory(player_id)
    if not inventory:
        return jsonify({"error": "Inventory not found"}), 404
    
    return jsonify({"inventory": asdict(inventory)})

@app.route('/api/economy/<player_id>/balance')
def get_player_balance(player_id):
    """API endpoint to get player economy balance"""
    if not bot_manager or not bot_manager.inventory_manager:
        return jsonify({"error": "Inventory manager not available"}), 500
    
    balance = bot_manager.inventory_manager.get_player_balance(player_id)
    return jsonify({"player_id": player_id, "balance": balance})

@app.route('/api/commands/list')
def get_commands_list():
    """API endpoint to get list of available commands"""
    if not bot_manager or not bot_manager.command_handler:
        return jsonify({"error": "Command handler not available"}), 500
    
    commands = bot_manager.command_handler.get_available_commands()
    return jsonify({"commands": commands})

@app.route('/api/warps/list')
def get_warps_list():
    """API endpoint to get list of warps"""
    if not bot_manager or not bot_manager.command_handler:
        return jsonify({"error": "Command handler not available"}), 500
    
    warps = bot_manager.command_handler.get_all_warps()
    return jsonify({"warps": warps})

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

# Health check endpoint for Render
@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Minecraft Bot Hub",
        "version": "2.0.0"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """Handle client joining a room"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('status', {'msg': f'Joined room: {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Handle client leaving a room"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('status', {'msg': f'Left room: {room}'}, room=room)

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Minecraft Bot Hub on {host}:{port}")
    
    try:
        # Run with SocketIO for production
        socketio.run(app, host=host, port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        if bot_manager:
            bot_manager.cleanup()
            bot_manager.cleanup_database()
        raise