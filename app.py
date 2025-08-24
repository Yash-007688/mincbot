#!/usr/bin/env python3
"""
Bot Vision Commander - Flask Web Application
Main Flask app that serves the web interface for bot vision and command system
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import json
import time
import threading
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import math
import random
from bot_brain import BotBrain, TaskPriority, BotState

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bot_vision_commander_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global commander instance
commander = None

class BotVisionCommander:
    def __init__(self):
        self.brain = BotBrain()
        self.bot_visions = {}
        self.world_map = {
            'width': 100,
            'height': 100,
            'blocks': {},
            'entities': {},
            'last_update': datetime.now()
        }
        self.command_history = []
        self.live_commands = []
        self.is_running = False
        self.update_interval = 1.0
        self.view_distance = 16
        self.connected_clients = 0
        
        # Initialize with sample bot data
        self._initialize_sample_bots()
        
    def _initialize_sample_bots(self):
        """Initialize with sample bot data for demonstration"""
        sample_bots = [
            {
                "name": "Bot1",
                "position": (100, 64, 200),
                "looking_at": (105, 64, 205),
                "state": "mining",
                "health": 20.0,
                "food": 18.0,
                "team": "mining_team"
            },
            {
                "name": "Bot2", 
                "position": (150, 64, 250),
                "looking_at": (155, 64, 255),
                "state": "building",
                "health": 19.0,
                "food": 20.0,
                "team": "building_team"
            },
            {
                "name": "Bot3",
                "position": (200, 64, 300),
                "looking_at": (205, 64, 305),
                "state": "exploring",
                "health": 18.0,
                "food": 17.0,
                "team": "exploration_team"
            },
            {
                "name": "Bot4",
                "position": (250, 64, 350),
                "looking_at": (255, 64, 355),
                "state": "farming",
                "health": 20.0,
                "food": 19.0,
                "team": "farming_team"
            },
            {
                "name": "Bot5",
                "position": (300, 64, 400),
                "looking_at": (305, 64, 405),
                "state": "crafting",
                "health": 17.0,
                "food": 16.0,
                "team": "crafting_team"
            }
        ]
        
        for bot_data in sample_bots:
            self._update_bot_vision(bot_data["name"], bot_data)
    
    def _update_bot_vision(self, bot_name: str, data: Dict[str, Any]):
        """Update the vision data for a specific bot"""
        nearby_blocks = self._generate_nearby_blocks(data["position"])
        nearby_entities = self._generate_nearby_entities(data["position"])
        
        vision = {
            "bot_name": bot_name,
            "position": data["position"],
            "looking_at": data["looking_at"],
            "nearby_blocks": nearby_blocks,
            "nearby_entities": nearby_entities,
            "inventory": self._generate_sample_inventory(),
            "health": data["health"],
            "food": data["food"],
            "state": data["state"],
            "team": data.get("team", "unassigned"),
            "last_update": datetime.now().isoformat(),
            "view_distance": self.view_distance
        }
        
        self.bot_visions[bot_name] = vision
        self._update_world_map(vision)
        
        # Emit update to connected clients
        socketio.emit('bot_update', {
            'bot_name': bot_name,
            'vision': vision
        })
    
    def _generate_nearby_blocks(self, position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """Generate sample nearby blocks for a bot position"""
        blocks = []
        x, y, z = position
        
        for dx in range(-self.view_distance, self.view_distance + 1):
            for dy in range(-8, 8 + 1):
                for dz in range(-self.view_distance, self.view_distance + 1):
                    if abs(dx) + abs(dy) + abs(dz) <= self.view_distance:
                        block_x, block_y, block_z = x + dx, y + dy, z + dz
                        block_type = self._get_block_type_at(block_x, block_y, block_z)
                        
                        if block_type != "air":
                            blocks.append({
                                "position": (block_x, block_y, block_z),
                                "type": block_type,
                                "distance": math.sqrt(dx*dx + dy*dy + dz*dz)
                            })
        
        return blocks[:50]
    
    def _generate_nearby_entities(self, position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """Generate sample nearby entities for a bot position"""
        entities = []
        x, y, z = position
        
        entity_types = ["zombie", "skeleton", "creeper", "cow", "pig", "chicken", "villager", "spider"]
        
        for i in range(random.randint(0, 5)):
            dx = random.randint(-10, 10)
            dy = random.randint(-5, 5)
            dz = random.randint(-10, 10)
            
            entity_type = random.choice(entity_types)
            entity_x, entity_y, entity_z = x + dx, y + dy, z + dz
            
            entities.append({
                "position": (entity_x, entity_y, entity_z),
                "type": entity_type,
                "distance": math.sqrt(dx*dx + dy*dy + dz*dz),
                "health": random.randint(1, 20) if entity_type in ["zombie", "skeleton", "creeper", "spider"] else 10
            })
        
        return entities
    
    def _get_block_type_at(self, x: float, y: float, z: float) -> str:
        """Determine block type at given coordinates"""
        if y < 60:
            return "stone"
        elif y < 64:
            return "dirt"
        elif y < 65:
            return "grass"
        elif y < 70:
            if random.random() < 0.3:
                return "tree"
            else:
                return "air"
        else:
            return "air"
    
    def _generate_sample_inventory(self) -> Dict[str, int]:
        """Generate sample inventory for bots"""
        items = ["wood", "stone", "iron_ore", "coal", "diamond", "food", "torch", "pickaxe", "axe", "sword"]
        inventory = {}
        
        for item in random.sample(items, random.randint(3, 6)):
            inventory[item] = random.randint(1, 20)
        
        return inventory
    
    def _update_world_map(self, vision: Dict[str, Any]):
        """Update the world map with bot vision data"""
        x, y, z = vision["position"]
        
        for block in vision["nearby_blocks"]:
            bx, by, bz = block["position"]
            map_key = (int(bx/10), int(bz/10))
            
            if map_key not in self.world_map["blocks"]:
                self.world_map["blocks"][map_key] = []
            
            if block["type"] not in self.world_map["blocks"][map_key]:
                self.world_map["blocks"][map_key].append(block["type"])
        
        for entity in vision["nearby_entities"]:
            ex, ey, ez = entity["position"]
            map_key = (int(ex/10), int(ez/10))
            
            if map_key not in self.world_map["entities"]:
                self.world_map["entities"][map_key] = []
            
            if entity["type"] not in self.world_map["entities"][map_key]:
                self.world_map["entities"][map_key].append(entity["type"])
        
        self.world_map["last_update"] = datetime.now().isoformat()
    
    def get_bot_vision_summary(self) -> Dict[str, Any]:
        """Get a summary of all bot visions"""
        summary = {
            "total_bots": len(self.bot_visions),
            "bot_status": {},
            "world_overview": {},
            "last_update": datetime.now().isoformat()
        }
        
        for bot_name, vision in self.bot_visions.items():
            summary["bot_status"][bot_name] = {
                "position": vision["position"],
                "state": vision["state"],
                "health": vision["health"],
                "food": vision["food"],
                "team": vision["team"],
                "nearby_blocks": len(vision["nearby_blocks"]),
                "nearby_entities": len(vision["nearby_entities"]),
                "inventory_count": len(vision["inventory"])
            }
        
        summary["world_overview"] = {
            "total_blocks": len(self.world_map["blocks"]),
            "total_entities": len(self.world_map["entities"]),
            "block_types": list(set([block for blocks in self.world_map["blocks"].values() for block in blocks])),
            "entity_types": list(set([entity for entities in self.world_map["entities"].values() for entity in entities]))
        }
        
        return summary
    
    def process_live_command(self, command: str) -> Dict[str, Any]:
        """Process a live command and return the result"""
        timestamp = datetime.now()
        
        self.command_history.append({
            "timestamp": timestamp.isoformat(),
            "command": command,
            "status": "processing"
        })
        
        try:
            analysis = self.brain.analyze_prompt(command)
            result = self._execute_command(analysis, command)
            
            self.command_history[-1]["status"] = "completed"
            self.command_history[-1]["result"] = result
            
            # Emit command result to clients
            socketio.emit('command_result', {
                'command': command,
                'result': result,
                'timestamp': timestamp.isoformat()
            })
            
            return {
                "success": True,
                "analysis": analysis,
                "result": result,
                "timestamp": timestamp.isoformat()
            }
            
        except Exception as e:
            self.command_history[-1]["status"] = "error"
            self.command_history[-1]["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": timestamp.isoformat()
            }
    
    def _execute_command(self, analysis: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Execute a command based on analysis"""
        intent = analysis["intent"]
        entities = analysis["entities"]
        
        if intent == "mining":
            return self._execute_mining_command(entities)
        elif intent == "building":
            return self._execute_building_command(entities)
        elif intent == "movement":
            return self._execute_movement_command(entities)
        elif intent == "status_request":
            return self._execute_status_command()
        else:
            return {"message": f"Command '{command}' processed with intent: {intent}"}
    
    def _execute_mining_command(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mining command"""
        bot_names = entities.get("bot_names", [])
        items = entities.get("items", [])
        
        if not bot_names:
            bot_names = list(self.bot_visions.keys())
        
        results = []
        for bot_name in bot_names:
            if bot_name in self.bot_visions:
                task_id = self.brain.create_task(
                    task_type="mining",
                    description=f"Mine {', '.join(items) if items else 'resources'}",
                    target_bot=bot_name,
                    parameters={"items": items, "auto": True},
                    priority=TaskPriority.HIGH
                )
                
                results.append({
                    "bot": bot_name,
                    "task_id": task_id,
                    "action": "mining_started"
                })
        
        return {
            "action": "mining",
            "bots_involved": bot_names,
            "tasks_created": results
        }
    
    def _execute_building_command(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a building command"""
        bot_names = entities.get("bot_names", [])
        locations = entities.get("locations", [])
        
        if not bot_names:
            bot_names = list(self.bot_visions.keys())
        
        results = []
        for bot_name in bot_names:
            if bot_name in self.bot_visions:
                task_id = self.brain.create_task(
                    task_type="building",
                    description="Build structure as requested",
                    target_bot=bot_name,
                    parameters={"auto_building": True, "locations": locations},
                    priority=TaskPriority.MEDIUM
                )
                
                results.append({
                    "bot": bot_name,
                    "task_id": task_id,
                    "action": "building_started"
                })
        
        return {
            "action": "building",
            "bots_involved": bot_names,
            "tasks_created": results
        }
    
    def _execute_movement_command(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a movement command"""
        bot_names = entities.get("bot_names", [])
        locations = entities.get("locations", [])
        
        if not bot_names:
            bot_names = list(self.bot_visions.keys())
        
        results = []
        for bot_name in bot_names:
            if bot_name in self.bot_visions:
                if locations:
                    for location in locations:
                        results.append({
                            "bot": bot_name,
                            "action": "moving",
                            "destination": location
                        })
                else:
                    results.append({
                        "bot": bot_name,
                        "action": "awaiting_destination"
                    })
        
        return {
            "action": "movement",
            "bots_involved": bot_names,
            "results": results
        }
    
    def _execute_status_command(self) -> Dict[str, Any]:
        """Execute a status command"""
        return {
            "action": "status_report",
            "data": self.get_bot_vision_summary()
        }
    
    def start_background_updates(self):
        """Start background updates for bot simulation"""
        def update_loop():
            while self.is_running:
                try:
                    for bot_name in list(self.bot_visions.keys()):
                        if random.random() < 0.3:
                            current_pos = self.bot_visions[bot_name]["position"]
                            new_x = current_pos[0] + random.randint(-5, 5)
                            new_z = current_pos[2] + random.randint(-5, 5)
                            new_pos = (new_x, current_pos[1], new_z)
                            
                            self._update_bot_vision(bot_name, {
                                "position": new_pos,
                                "looking_at": (new_x + 2, current_pos[1], new_z + 2),
                                "state": self.bot_visions[bot_name]["state"],
                                "health": self.bot_visions[bot_name]["health"],
                                "food": self.bot_visions[bot_name]["food"],
                                "team": self.bot_visions[bot_name]["team"]
                            })
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Background update error: {e}")
                    time.sleep(5)
        
        self.is_running = True
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

# Initialize commander
commander = BotVisionCommander()
commander.start_background_updates()

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard with bot status"""
    return render_template('dashboard.html')

@app.route('/bots')
def bots():
    """Individual bot management page"""
    return render_template('bots.html')

@app.route('/world')
def world():
    """World map and exploration page"""
    return render_template('world.html')

@app.route('/commands')
def commands():
    """Command center page"""
    return render_template('commands.html')

@app.route('/analytics')
def analytics():
    """Analytics and reports page"""
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    """Settings and configuration page"""
    return render_template('settings.html')

# API Routes
@app.route('/api/status')
def api_status():
    """Get current bot status"""
    return jsonify(commander.get_bot_vision_summary())

@app.route('/api/bots')
def api_bots():
    """Get detailed bot information"""
    return jsonify(commander.bot_visions)

@app.route('/api/world')
def api_world():
    """Get world map data"""
    return jsonify(commander.world_map)

@app.route('/api/commands')
def api_commands():
    """Get command history"""
    return jsonify({"commands": commander.command_history})

@app.route('/api/command', methods=['POST'])
def api_command():
    """Process a new command"""
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({"success": False, "error": "No command provided"})
    
    result = commander.process_live_command(command)
    return jsonify(result)

@app.route('/api/export')
def api_export():
    """Export all data"""
    export_data = {
        "bot_visions": commander.bot_visions,
        "world_map": commander.world_map,
        "command_history": commander.command_history,
        "export_timestamp": datetime.now().isoformat()
    }
    
    filename = f"bot_vision_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Save to file
    with open(f"exports/{filename}", 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return jsonify({
        "success": True,
        "filename": filename,
        "message": "Data exported successfully"
    })

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    commander.connected_clients += 1
    print(f"Client connected. Total clients: {commander.connected_clients}")
    
    # Send initial data
    emit('connected', {
        'message': 'Connected to Bot Vision Commander',
        'total_bots': len(commander.bot_visions)
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    commander.connected_clients -= 1
    print(f"Client disconnected. Total clients: {commander.connected_clients}")

@socketio.on('request_update')
def handle_update_request():
    """Handle update requests from clients"""
    emit('bot_update', {
        'all_bots': commander.bot_visions,
        'world_map': commander.world_map
    })

if __name__ == '__main__':
    # Create exports directory if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    print("🚀 Starting Bot Vision Commander Flask App...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📱 Dashboard: http://localhost:5000/dashboard")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Flask app...")
        commander.is_running = False
        print("✅ Bot Vision Commander Flask app stopped.")