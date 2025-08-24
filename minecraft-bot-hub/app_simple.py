#!/usr/bin/env python3
"""
Minecraft Bot Hub - Simplified Flask Application
Fixed routing and simplified for production deployment
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
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Simple in-memory storage for demo
users = {
    'yash': {
        'username': 'yash',
        'password': 'yash',
        'role': 'admin'
    }
}

sessions = {}
deployments = []

def generate_default_bot_names(bot_count):
    """Generate default bot names for deployment"""
    gamer_names = [
        'IronMiner', 'WoodCutter', 'StoneBreaker', 'DiamondHunter',
        'NetherExplorer', 'EndVoyager', 'RedstoneMaster', 'Enchanter',
        'PotionBrewer', 'Archer', 'Swordsman', 'Miner',
        'Farmer', 'Builder', 'Explorer', 'Trader',
        'Guardian', 'Scout', 'Navigator', 'Artisan'
    ]
    
    if bot_count <= len(gamer_names):
        return gamer_names[:bot_count]
    else:
        return [f'Bot{i}' for i in range(1, bot_count + 1)]

def create_session_id():
    """Create a unique session ID"""
    return secrets.token_hex(32)

def is_authenticated():
    """Check if user is authenticated"""
    session_id = request.cookies.get('session_id')
    return session_id in sessions

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
    if not is_authenticated():
        return redirect(url_for('login'))
    
    session_data = sessions.get(request.cookies.get('session_id'))
    username = session_data['username'] if session_data else 'Unknown'
    return render_template('prompt.html', username=username)

# Authentication routes
@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Check credentials
        if username in users and users[username]['password'] == password:
            # Create session
            session_id = create_session_id()
            sessions[session_id] = {
                'username': username,
                'role': users[username]['role'],
                'created_at': datetime.now()
            }
            
            response = jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "username": username,
                    "role": users[username]['role']
                }
            })
            
            # Set session cookie
            response.set_cookie('session_id', session_id, max_age=86400, httponly=True, secure=False)
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Handle user logout"""
    try:
        session_id = request.cookies.get('session_id')
        if session_id in sessions:
            del sessions[session_id]
        
        response = jsonify({"success": True, "message": "Logout successful"})
        response.delete_cookie('session_id')
        return response
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/auth/check')
def auth_check():
    """Check if user is authenticated"""
    try:
        if is_authenticated():
            session_data = sessions.get(request.cookies.get('session_id'))
            return jsonify({
                "authenticated": True,
                "user": {
                    "username": session_data['username'],
                    "role": session_data['role']
                }
            })
        else:
            return jsonify({"authenticated": False})
    except Exception as e:
        logger.error(f"Auth check error: {e}")
        return jsonify({"authenticated": False})

# API Routes
@app.route('/api/system/info')
def system_info():
    """Get system information"""
    try:
        return jsonify({
            "success": True,
            "system": {
                "name": "Minecraft Bot Hub",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"System info error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/deployments/list')
def list_deployments():
    """List all deployments"""
    try:
        return jsonify({
            "success": True,
            "deployments": deployments
        })
    except Exception as e:
        logger.error(f"List deployments error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/deployments/create', methods=['POST'])
def create_deployment():
    """Create a new deployment"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        deployment = {
            'id': len(deployments) + 1,
            'name': data.get('name', 'Deployment'),
            'bot_count': data.get('bot_count', 1),
            'server_name': data.get('server_name', 'mcfleet'),
            'server_ip': data.get('server_ip', 'play.mcfleet.net'),
            'server_port': data.get('server_port', 25565),
            'bot_names': data.get('bot_names', generate_default_bot_names(data.get('bot_count', 1))),
            'status': 'created',
            'created_at': datetime.now().isoformat()
        }
        
        deployments.append(deployment)
        
        return jsonify({
            "success": True,
            "deployment": deployment
        })
    except Exception as e:
        logger.error(f"Create deployment error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/deployments/<int:deployment_id>/bot-names')
def get_deployment_bot_names(deployment_id):
    """Get bot names for a deployment"""
    try:
        deployment = next((d for d in deployments if d['id'] == deployment_id), None)
        if not deployment:
            return jsonify({"error": "Deployment not found"}), 404
        
        return jsonify({
            "success": True,
            "bot_names": deployment.get('bot_names', [])
        })
    except Exception as e:
        logger.error(f"Get bot names error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/deployments/<int:deployment_id>/deploy', methods=['POST'])
def deploy_bots(deployment_id):
    """Deploy bots for a deployment"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        deployment = next((d for d in deployments if d['id'] == deployment_id), None)
        if not deployment:
            return jsonify({"error": "Deployment not found"}), 404
        
        # Simulate deployment
        deployment['status'] = 'deploying'
        deployment['deployed_at'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "message": f"Deploying {deployment['bot_count']} bots to {deployment['server_name']}",
            "deployment": deployment
        })
    except Exception as e:
        logger.error(f"Deploy bots error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/deployments/<int:deployment_id>/stop', methods=['POST'])
def stop_deployment(deployment_id):
    """Stop a deployment"""
    try:
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        
        deployment = next((d for d in deployments if d['id'] == deployment_id), None)
        if not deployment:
            return jsonify({"error": "Deployment not found"}), 404
        
        deployment['status'] = 'stopped'
        deployment['stopped_at'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "message": "Deployment stopped successfully",
            "deployment": deployment
        })
    except Exception as e:
        logger.error(f"Stop deployment error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# SocketIO events
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

# Health check
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Minecraft Bot Hub"
    })

if __name__ == '__main__':
    logger.info("Starting Minecraft Bot Hub Flask Application...")
    
    # Create necessary directories
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    try:
        # Run the application
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)