import json
import time
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

class BotState(Enum):
    IDLE = "idle"
    GATHERING_WOOD = "gathering_wood"
    BUILDING = "building"
    EXPLORING = "exploring"
    ATTACKING = "attacking"
    HEALING = "healing"
    SLEEPING = "sleeping"
    CRAFTING = "crafting"
    FOLLOWING = "following"
    MINING = "mining"
    FARMING = "farming"
    DEFENDING = "defending"
    VISION_ANALYSIS = "vision_analysis"
    SETTINGS_MANAGEMENT = "settings_management"

@dataclass
class BotProperties:
    name: str
    team_members: List[str]
    state: BotState = BotState.IDLE
    health: int = 20
    food: int = 20
    saturation: float = 5.0
    inventory: Dict[str, int] = None
    equipment: Dict[str, Optional[str]] = None
    last_chat_time: float = 0
    chat_cooldown: int = 5000  # 5 seconds in milliseconds
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_position: Optional[Tuple[float, float, float]] = None
    target_entity: Optional[str] = None
    is_sleeping: bool = False
    is_attacking: bool = False
    is_following: bool = False
    vision_enabled: bool = True
    camera_type: str = "main_camera"
    ip_address: str = "192.168.1.100"
    port: int = 8080
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {}
        if self.equipment is None:
            self.equipment = {
                "hand": None,
                "head": None,
                "torso": None,
                "legs": None,
                "feet": None
            }

class BotAI:
    def __init__(self, bot_properties: BotProperties):
        self.bot = bot_properties
        self.memory_dir = Path("ai_commands/input/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / f"{self.bot.name}_memory.json"
        self.config_file = Path("ai_commands/config/ai_config.json")
        self.load_memory()
        self.load_config()
        
        # Priority levels for different actions
        self.action_priorities = {
            BotState.HEALING: 1,
            BotState.ATTACKING: 2,
            BotState.DEFENDING: 2,
            BotState.SLEEPING: 3,
            BotState.FOLLOWING: 4,
            BotState.VISION_ANALYSIS: 4,
            BotState.GATHERING_WOOD: 5,
            BotState.MINING: 5,
            BotState.FARMING: 5,
            BotState.CRAFTING: 6,
            BotState.BUILDING: 7,
            BotState.EXPLORING: 8,
            BotState.SETTINGS_MANAGEMENT: 9,
            BotState.IDLE: 10
        }

    def load_memory(self):
        """Load bot's memory from JSON file"""
        try:
            with open(self.memory_file, 'r') as f:
                memory = json.load(f)
                self.bot.inventory = memory.get('inventory', {})
                self.bot.equipment = memory.get('equipment', {})
                self.bot.state = BotState(memory.get('state', 'idle'))
                self.bot.position = tuple(memory.get('position', (0.0, 0.0, 0.0)))
                self.bot.target_position = tuple(memory.get('target_position', (0.0, 0.0, 0.0))) if memory.get('target_position') else None
                self.bot.vision_enabled = memory.get('vision_enabled', True)
                self.bot.camera_type = memory.get('camera_type', 'main_camera')
                self.bot.ip_address = memory.get('ip_address', '192.168.1.100')
                self.bot.port = memory.get('port', 8080)
        except FileNotFoundError:
            self.save_memory()  # Create new memory file if none exists

    def load_config(self):
        """Load AI configuration from config file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {self.config_file} not found")
            self.config = {}

    def save_memory(self):
        """Save bot's current state to JSON file"""
        memory = {
            'inventory': self.bot.inventory,
            'equipment': self.bot.equipment,
            'state': self.bot.state.value,
            'position': self.bot.position,
            'target_position': self.bot.target_position,
            'vision_enabled': self.bot.vision_enabled,
            'camera_type': self.bot.camera_type,
            'ip_address': self.bot.ip_address,
            'port': self.bot.port
        }
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)

    def update_vision_status(self, enabled: bool, camera_type: str = None):
        """Update bot's vision system status"""
        self.bot.vision_enabled = enabled
        if camera_type:
            self.bot.camera_type = camera_type
        self.save_memory()
        return f"Vision system {'enabled' if enabled else 'disabled'} for {self.bot.name}"

    def update_network_config(self, ip_address: str, port: int):
        """Update bot's network configuration"""
        self.bot.ip_address = ip_address
        self.bot.port = port
        self.save_memory()
        return f"Network config updated for {self.bot.name}: {ip_address}:{port}"

    def get_vision_data(self):
        """Get current vision data from bot's camera"""
        if not self.bot.vision_enabled:
            return {"error": "Vision system disabled"}
        
        # Simulate vision data based on camera type
        vision_data = {
            "bot_name": self.bot.name,
            "camera_type": self.bot.camera_type,
            "timestamp": time.time(),
            "position": self.bot.position,
            "status": "active"
        }
        
        if self.bot.camera_type == "main_camera":
            vision_data.update({
                "environment": "stable",
                "blocks_detected": len(self.bot.inventory),
                "entities_nearby": 0
            })
        elif self.bot.camera_type == "thermal_vision":
            vision_data.update({
                "temperature": "normal",
                "heat_sources": 0,
                "thermal_anomalies": 0
            })
        elif self.bot.camera_type == "depth_sensor":
            vision_data.update({
                "depth_map": "generated",
                "obstacles": 0,
                "clear_path": True
            })
        elif self.bot.camera_type == "object_detection":
            vision_data.update({
                "objects_detected": list(self.bot.inventory.keys()),
                "target_entities": 0,
                "item_recognition": "active"
            })
        
        return vision_data

    def ping_bot(self):
        """Ping the bot to check if it's online"""
        try:
            # Simulate ping response
            response_time = 10 + (hash(self.bot.name) % 50)  # Simulate realistic ping
            return {
                "bot_name": self.bot.name,
                "status": "online",
                "ping_ms": response_time,
                "health": self.bot.health,
                "position": self.bot.position
            }
        except Exception as e:
            return {
                "bot_name": self.bot.name,
                "status": "error",
                "error": str(e)
            }

    def restart_bot(self):
        """Simulate restarting the bot"""
        try:
            # Reset some properties
            self.bot.state = BotState.IDLE
            self.bot.is_attacking = False
            self.bot.is_following = False
            self.bot.target_position = None
            self.bot.target_entity = None
            
            # Save state
            self.save_memory()
            
            return {
                "bot_name": self.bot.name,
                "status": "restarted",
                "new_state": "idle",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "bot_name": self.bot.name,
                "status": "restart_failed",
                "error": str(e)
            }

    def get_server_config(self):
        """Get current server configuration"""
        server_config = self.config.get('ai_settings', {}).get('server_config', {})
        return {
            "server_name": server_config.get('server_name', 'Minecraft Bot Hub'),
            "default_port": server_config.get('default_port', 25565),
            "default_ip": server_config.get('default_ip', '192.168.1.100'),
            "max_connections": server_config.get('max_connections', 50)
        }

    def update_server_config(self, server_name: str, port: int, ip: str):
        """Update server configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            config['ai_settings']['server_config'].update({
                'server_name': server_name,
                'default_port': port,
                'default_ip': ip
            })
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return f"Server configuration updated: {server_name} ({ip}:{port})"
        except Exception as e:
            return f"Error updating server config: {str(e)}"

    def get_system_info(self):
        """Get current system information"""
        return {
            "current_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": f"{int(time.time() / 3600)}h {int((time.time() % 3600) / 60)}m",
            "active_connections": len(self.team_members) + 1,
            "bot_status": self.bot.state.value,
            "vision_system": "active" if self.bot.vision_enabled else "inactive"
        }

    def process_chat_command(self, command: str, user: str = "User"):
        """Process chat commands from the web interface"""
        command_lower = command.lower()
        
        if "vision" in command_lower or "see" in command_lower:
            vision_data = self.get_vision_data()
            return f"I'm currently monitoring the live bot vision streams. I can see multiple camera feeds showing real-time environmental data, thermal imaging, depth analysis, and object detection. What specific aspect would you like me to focus on?"
        
        elif "bot" in command_lower or "ai" in command_lower:
            return f"Our AI bots are actively processing information through their vision systems. I can see live streams from Bot Alpha (main camera), Bot Beta (thermal vision), Bot Gamma (depth sensor), and Bot Delta (object detection). They're all working together to provide comprehensive environmental analysis."
        
        elif "minecraft" in command_lower or "block" in command_lower:
            return f"Ah, you're interested in the Minecraft-style interface! Our system combines the familiar blocky aesthetic with advanced AI capabilities. The bots can analyze block patterns, detect structures, and provide insights about the virtual world they're observing."
        
        elif "settings" in command_lower or "config" in command_lower:
            server_config = self.get_server_config()
            return f"Current server configuration: {server_config['server_name']} running on {server_config['default_ip']}:{server_config['default_port']}. You can modify these settings in the settings panel."
        
        else:
            # Default AI responses
            responses = [
                f"I've analyzed your request through our brain system. Based on the current bot vision data, I can see that the environment is stable and all systems are operational.",
                f"Interesting question! Let me check the live bot vision streams. I can see multiple data points that suggest we should proceed with your request.",
                f"Based on the real-time analysis from our vision systems, I recommend the following approach. The bots are currently detecting optimal conditions for this operation."
            ]
            return responses[hash(command) % len(responses)]

    def execute_action(self, action: str, parameters: Dict[str, any]):
        """Execute a specific action command"""
        try:
            if action == "mine":
                return self._execute_mine(parameters)
            elif action == "build":
                return self._execute_build(parameters)
            elif action == "collect":
                return self._execute_collect(parameters)
            elif action == "move":
                return self._execute_move(parameters)
            elif action == "vision":
                return self._execute_vision(parameters)
            else:
                return f"Unknown action: {action}"
        except Exception as e:
            return f"Error executing {action}: {str(e)}"

    def _execute_mine(self, parameters: Dict[str, any]):
        """Execute mining action"""
        block_type = parameters.get('block_type', 'stone')
        self.bot.state = BotState.MINING
        self.bot.inventory[block_type] = self.bot.inventory.get(block_type, 0) + 1
        self.save_memory()
        return f"{self.bot.name} is now mining {block_type}. Inventory updated."

    def _execute_build(self, parameters: Dict[str, any]):
        """Execute building action"""
        structure_type = parameters.get('structure_type', 'house')
        self.bot.state = BotState.BUILDING
        return f"{self.bot.name} is now building a {structure_type}."

    def _execute_collect(self, parameters: Dict[str, any]):
        """Execute collection action"""
        item_type = parameters.get('item_type', 'wood')
        self.bot.state = BotState.GATHERING_WOOD
        self.bot.inventory[item_type] = self.bot.inventory.get(item_type, 0) + 1
        self.save_memory()
        return f"{self.bot.name} is now collecting {item_type}. Inventory updated."

    def _execute_move(self, parameters: Dict[str, any]):
        """Execute movement action"""
        x = parameters.get('x', 0)
        y = parameters.get('y', 64)
        z = parameters.get('z', 0)
        self.bot.target_position = (x, y, z)
        self.bot.state = BotState.FOLLOWING
        self.save_memory()
        return f"{self.bot.name} is moving to coordinates ({x}, {y}, {z})."

    def _execute_vision(self, parameters: Dict[str, any]):
        """Execute vision-related action"""
        vision_type = parameters.get('vision_type', 'analyze')
        if vision_type == "analyze":
            vision_data = self.get_vision_data()
            return f"Vision analysis complete for {self.bot.name}: {vision_data}"
        elif vision_type == "toggle":
            enabled = parameters.get('enabled', not self.bot.vision_enabled)
            return self.update_vision_status(enabled)
        else:
            return f"Unknown vision action: {vision_type}"

    def get_status_summary(self):
        """Get a comprehensive status summary of the bot"""
        return {
            "name": self.bot.name,
            "state": self.bot.state.value,
            "health": self.bot.health,
            "food": self.bot.food,
            "position": self.bot.position,
            "vision_enabled": self.bot.vision_enabled,
            "camera_type": self.bot.camera_type,
            "ip_address": self.bot.ip_address,
            "port": self.bot.port,
            "inventory_count": len(self.bot.inventory),
            "team_members": self.bot.team_members
        }
