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

# Import our AI commands system
try:
    from ai_commands.bot_ip_manager import BotIPManager
    from ai_commands.input.bot_ai import BotAI, BotProperties, BotState
    from ai_commands.commands.actions.action_handler import ActionHandler
    AI_SYSTEM_AVAILABLE = True
except ImportError:
    AI_SYSTEM_AVAILABLE = False
    print("Warning: AI commands system not available")

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

class BotManager:
    """Manages bot instances and operations"""
    
    def __init__(self):
        self.bots = {}
        self.bot_ips = {}
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
                return self.bots[bot_id].execute_action(command, parameters or {})
            else:
                # Mock command execution
                return f"Mock command '{command}' executed on {bot_id}"
        return f"Bot {bot_id} not found"
    
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

# Initialize bot manager
bot_manager = BotManager()

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
    return render_template('prompt.html')

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
    return jsonify({
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": "2h 15m",  # Mock uptime
        "active_connections": len(bot_manager.bots) if bot_manager else 0,
        "system_status": "operational",
        "ai_system_available": AI_SYSTEM_AVAILABLE
    })

@app.route('/api/chat/message', methods=['POST'])
def process_chat_message():
    """API endpoint to process chat messages"""
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
            ai_response = f"AI system processing: {message}"
    else:
        # Mock AI response
        responses = [
            f"I've analyzed your request: {message}. Based on the current bot vision data, I can see that the environment is stable.",
            f"Interesting question! Let me check the live bot vision streams. I can see multiple data points that suggest we should proceed.",
            f"Based on the real-time analysis from our vision systems, I recommend the following approach for: {message}"
        ]
        ai_response = responses[hash(message) % len(responses)]
    
    return jsonify({
        "success": True,
        "response": ai_response,
        "timestamp": datetime.now().isoformat(),
        "user": user
    })

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
    logger.info("Starting Minecraft Bot Hub Flask Application...")
    logger.info(f"AI System Available: {AI_SYSTEM_AVAILABLE}")
    
    # Create templates directory if it doesn't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)