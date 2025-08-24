#!/usr/bin/env python3
"""
Server Manager - Minecraft Bot Hub Server Management System
Handles bot names, player coordinates, and server-wide operations
"""

import json
import time
import uuid
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Player information and status"""
    uuid: str
    username: str
    display_name: str
    is_bot: bool
    is_online: bool
    last_seen: datetime
    coordinates: Tuple[float, float, float]
    dimension: str
    gamemode: str
    health: float
    food: float
    experience: int
    level: int
    team: Optional[str]
    permissions: List[str]
    join_date: datetime
    playtime: int  # in minutes
    achievements: List[str]
    statistics: Dict[str, int]

@dataclass
class BotPlayer(Player):
    """Bot-specific player information"""
    bot_type: str
    ai_version: str
    owner: str
    commands_executed: int
    tasks_completed: int
    last_command: Optional[str]
    auto_mode: bool
    skill_level: int
    specialization: str

@dataclass
class ServerRegion:
    """Server region/land claim information"""
    region_id: str
    name: str
    owner: str
    coordinates: Tuple[float, float, float]
    size: Tuple[int, int, int]  # width, height, depth
    type: str  # "claim", "spawn", "protected", "public"
    permissions: Dict[str, List[str]]
    created_date: datetime
    expiry_date: Optional[datetime]
    description: str
    flags: Dict[str, bool]

@dataclass
class ServerCommand:
    """Server command definition"""
    name: str
    description: str
    usage: str
    aliases: List[str]
    permissions: List[str]
    cooldown: int  # seconds
    category: str
    examples: List[str]
    enabled: bool

class ServerManager:
    """
    Comprehensive server management system for Minecraft Bot Hub
    Handles players, bots, coordinates, regions, and commands
    """
    
    def __init__(self, config_file: str = "server_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Core data structures
        self.players: Dict[str, Player] = {}
        self.bots: Dict[str, BotPlayer] = {}
        self.regions: Dict[str, ServerRegion] = {}
        self.commands: Dict[str, ServerCommand] = {}
        self.online_players: Set[str] = set()
        self.player_coordinates: Dict[str, Tuple[float, float, float]] = {}
        
        # Server state
        self.server_start_time = datetime.now()
        self.server_uptime = timedelta(0)
        self.max_players = 100
        self.current_players = 0
        self.server_status = "online"
        
        # Threading and synchronization
        self.lock = threading.RLock()
        self.update_thread = None
        self.stop_updates = threading.Event()
        
        # Initialize the system
        self.load_config()
        self.initialize_default_commands()
        self.initialize_default_regions()
        self.start_background_tasks()
        
        logger.info("Server Manager initialized successfully")
    
    def load_config(self):
        """Load server configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                    # Load players
                    for player_data in config_data.get('players', []):
                        if player_data.get('is_bot'):
                            player = BotPlayer(**player_data)
                            self.bots[player.uuid] = player
                        else:
                            player = Player(**player_data)
                            self.players[player.uuid] = player
                    
                    # Load regions
                    for region_data in config_data.get('regions', []):
                        region = ServerRegion(**region_data)
                        self.regions[region.region_id] = region
                    
                    # Load commands
                    for cmd_data in config_data.get('commands', []):
                        command = ServerCommand(**cmd_data)
                        self.commands[command.name] = command
                    
                    logger.info(f"Loaded {len(self.players)} players, {len(self.bots)} bots, {len(self.regions)} regions, {len(self.commands)} commands")
                    
            else:
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default server configuration"""
        logger.info("Creating default server configuration...")
        
        # Create default bot players
        bot_names = [
            "IronMiner", "WoodCutter", "StoneBuilder", "RedstoneEngineer",
            "DiamondHunter", "EmeraldTrader", "GoldSmith", "CoalCollector",
            "WheatFarmer", "ChickenBreeder", "CattleRancher", "FishCatcher"
        ]
        
        for i, name in enumerate(bot_names):
            bot = BotPlayer(
                uuid=str(uuid.uuid4()),
                username=name.lower(),
                display_name=name,
                is_bot=True,
                is_online=True,
                last_seen=datetime.now(),
                coordinates=(random.randint(-1000, 1000), 64, random.randint(-1000, 1000)),
                dimension="overworld",
                gamemode="survival",
                health=20.0,
                food=20.0,
                experience=0,
                level=1,
                team="AI_Bots",
                permissions=["bot.basic"],
                join_date=datetime.now(),
                playtime=0,
                achievements=[],
                statistics={},
                bot_type="utility",
                ai_version="1.0.0",
                owner="system",
                commands_executed=0,
                tasks_completed=0,
                last_command=None,
                auto_mode=True,
                skill_level=random.randint(1, 10),
                specialization=name.split()[0].lower()
            )
            
            self.bots[bot.uuid] = bot
            self.player_coordinates[bot.uuid] = bot.coordinates
        
        # Create default regions
        default_regions = [
            {
                "name": "Spawn",
                "type": "spawn",
                "coordinates": (0, 64, 0),
                "size": (100, 100, 100),
                "owner": "system",
                "permissions": {"public": ["build", "destroy", "interact"]}
            },
            {
                "name": "Bot Workshop",
                "type": "protected",
                "coordinates": (200, 64, 0),
                "size": (50, 50, 50),
                "owner": "system",
                "permissions": {"bots": ["build", "destroy", "interact"]}
            },
            {
                "name": "Trading Hub",
                "type": "public",
                "coordinates": (-200, 64, 0),
                "size": (80, 80, 80),
                "owner": "system",
                "permissions": {"public": ["build", "destroy", "interact", "trade"]}
            }
        ]
        
        for region_data in default_regions:
            region = ServerRegion(
                region_id=str(uuid.uuid4()),
                name=region_data["name"],
                owner=region_data["owner"],
                coordinates=region_data["coordinates"],
                size=region_data["size"],
                type=region_data["type"],
                permissions=region_data["permissions"],
                created_date=datetime.now(),
                expiry_date=None,
                description=f"Default {region_data['type']} region",
                flags={"pvp": False, "mob_spawning": True, "weather": True}
            )
            
            self.regions[region.region_id] = region
        
        # Save configuration
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "players": [asdict(player) for player in self.players.values()],
            "bots": [asdict(bot) for bot in self.bots.values()],
            "regions": [asdict(region) for region in self.regions.values()],
            "commands": [asdict(command) for command in self.commands.values()],
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def initialize_default_commands(self):
        """Initialize default server commands"""
        default_commands = [
            {
                "name": "tp",
                "description": "Teleport to coordinates or player",
                "usage": "/tp <x> <y> <z> or /tp <player>",
                "aliases": ["teleport"],
                "permissions": ["command.tp"],
                "cooldown": 5,
                "category": "movement",
                "examples": ["/tp 100 64 100", "/tp IronMiner"],
                "enabled": True
            },
            {
                "name": "claim",
                "description": "Claim land for building",
                "usage": "/claim <name> <size>",
                "aliases": ["land"],
                "permissions": ["command.claim"],
                "cooldown": 60,
                "category": "land",
                "examples": ["/claim MyHouse 20x20"],
                "enabled": True
            },
            {
                "name": "home",
                "description": "Set or teleport to home",
                "usage": "/home [set] [name]",
                "aliases": ["h"],
                "permissions": ["command.home"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/home", "/home set", "/home set Main"],
                "enabled": True
            },
            {
                "name": "spawn",
                "description": "Teleport to spawn",
                "usage": "/spawn",
                "aliases": ["s"],
                "permissions": ["command.spawn"],
                "cooldown": 30,
                "category": "movement",
                "examples": ["/spawn"],
                "enabled": True
            },
            {
                "name": "tpa",
                "description": "Request teleport to player",
                "usage": "/tpa <player>",
                "aliases": ["teleportask"],
                "permissions": ["command.tpa"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/tpa IronMiner"],
                "enabled": True
            },
            {
                "name": "balance",
                "description": "Check your balance",
                "usage": "/balance [player]",
                "aliases": ["bal", "money"],
                "permissions": ["command.balance"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/balance", "/balance IronMiner"],
                "enabled": True
            },
            {
                "name": "pay",
                "description": "Pay another player",
                "usage": "/pay <player> <amount>",
                "aliases": ["send"],
                "permissions": ["command.pay"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/pay IronMiner 100"],
                "enabled": True
            },
            {
                "name": "kit",
                "description": "Get a starter kit",
                "usage": "/kit [name]",
                "aliases": ["starter"],
                "permissions": ["command.kit"],
                "cooldown": 86400,  # 24 hours
                "category": "items",
                "examples": ["/kit", "/kit builder"],
                "enabled": True
            },
            {
                "name": "warp",
                "description": "Teleport to a warp point",
                "usage": "/warp <name>",
                "aliases": ["w"],
                "permissions": ["command.warp"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/warp shop", "/warp arena"],
                "enabled": True
            },
            {
                "name": "setwarp",
                "description": "Set a warp point",
                "usage": "/setwarp <name>",
                "aliases": ["sw"],
                "permissions": ["command.setwarp"],
                "cooldown": 0,
                "category": "movement",
                "examples": ["/setwarp shop"],
                "enabled": True
            }
        ]
        
        for cmd_data in default_commands:
            command = ServerCommand(**cmd_data)
            self.commands[command.name] = command
        
        logger.info(f"Initialized {len(self.commands)} default commands")
    
    def initialize_default_regions(self):
        """Initialize default server regions"""
        # This is handled in create_default_config()
        pass
    
    def start_background_tasks(self):
        """Start background update tasks"""
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Background update tasks started")
    
    def update_loop(self):
        """Main update loop for server management"""
        while not self.stop_updates.is_set():
            try:
                # Update server uptime
                self.server_uptime = datetime.now() - self.server_start_time
                
                # Update player counts
                self.current_players = len(self.online_players)
                
                # Update bot coordinates (simulate movement)
                self.update_bot_positions()
                
                # Clean up expired regions
                self.cleanup_expired_regions()
                
                # Save configuration periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.save_config()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(5)
    
    def update_bot_positions(self):
        """Update bot positions (simulate movement)"""
        with self.lock:
            for bot in self.bots.values():
                if bot.is_online and bot.auto_mode:
                    # Simulate random movement
                    if random.random() < 0.01:  # 1% chance per second
                        x, y, z = bot.coordinates
                        new_x = x + random.randint(-5, 5)
                        new_y = max(64, y + random.randint(-2, 2))
                        new_z = z + random.randint(-5, 5)
                        
                        bot.coordinates = (new_x, new_y, new_z)
                        self.player_coordinates[bot.uuid] = bot.coordinates
                        
                        # Update last seen
                        bot.last_seen = datetime.now()
    
    def cleanup_expired_regions(self):
        """Clean up expired regions"""
        current_time = datetime.now()
        expired_regions = []
        
        for region_id, region in self.regions.items():
            if region.expiry_date and current_time > region.expiry_date:
                expired_regions.append(region_id)
        
        for region_id in expired_regions:
            del self.regions[region_id]
            logger.info(f"Removed expired region: {region_id}")
    
    # Player Management Methods
    
    def add_player(self, username: str, display_name: str = None, is_bot: bool = False) -> str:
        """Add a new player to the server"""
        with self.lock:
            player_uuid = str(uuid.uuid4())
            display_name = display_name or username
            
            if is_bot:
                player = BotPlayer(
                    uuid=player_uuid,
                    username=username.lower(),
                    display_name=display_name,
                    is_bot=True,
                    is_online=True,
                    last_seen=datetime.now(),
                    coordinates=(0, 64, 0),
                    dimension="overworld",
                    gamemode="survival",
                    health=20.0,
                    food=20.0,
                    experience=0,
                    level=1,
                    team="AI_Bots",
                    permissions=["bot.basic"],
                    join_date=datetime.now(),
                    playtime=0,
                    achievements=[],
                    statistics={},
                    bot_type="utility",
                    ai_version="1.0.0",
                    owner="system",
                    commands_executed=0,
                    tasks_completed=0,
                    last_command=None,
                    auto_mode=True,
                    skill_level=1,
                    specialization="general"
                )
                self.bots[player_uuid] = player
            else:
                player = Player(
                    uuid=player_uuid,
                    username=username.lower(),
                    display_name=display_name,
                    is_bot=False,
                    is_online=True,
                    last_seen=datetime.now(),
                    coordinates=(0, 64, 0),
                    dimension="overworld",
                    gamemode="survival",
                    health=20.0,
                    food=20.0,
                    experience=0,
                    level=1,
                    team=None,
                    permissions=["player.basic"],
                    join_date=datetime.now(),
                    playtime=0,
                    achievements=[],
                    statistics={}
                )
                self.players[player_uuid] = player
            
            self.player_coordinates[player_uuid] = player.coordinates
            self.online_players.add(player_uuid)
            
            logger.info(f"Added {'bot' if is_bot else 'player'}: {username}")
            return player_uuid
    
    def remove_player(self, player_uuid: str) -> bool:
        """Remove a player from the server"""
        with self.lock:
            if player_uuid in self.players:
                del self.players[player_uuid]
                removed = True
            elif player_uuid in self.bots:
                del self.bots[player_uuid]
                removed = True
            else:
                return False
            
            if player_uuid in self.online_players:
                self.online_players.remove(player_uuid)
            
            if player_uuid in self.player_coordinates:
                del self.player_coordinates[player_uuid]
            
            logger.info(f"Removed player: {player_uuid}")
            return removed
    
    def get_player(self, identifier: str) -> Optional[Player]:
        """Get player by UUID, username, or display name"""
        with self.lock:
            # Try UUID first
            if identifier in self.players:
                return self.players[identifier]
            if identifier in self.bots:
                return self.bots[identifier]
            
            # Try username
            for player in self.players.values():
                if player.username == identifier.lower():
                    return player
            
            for bot in self.bots.values():
                if bot.username == identifier.lower():
                    return bot
            
            # Try display name
            for player in self.players.values():
                if player.display_name == identifier:
                    return player
            
            for bot in self.bots.values():
                if bot.display_name == identifier:
                    return bot
            
            return None
    
    def update_player_coordinates(self, player_uuid: str, coordinates: Tuple[float, float, float], dimension: str = None):
        """Update player coordinates"""
        with self.lock:
            player = self.get_player(player_uuid)
            if player:
                player.coordinates = coordinates
                player.last_seen = datetime.now()
                self.player_coordinates[player_uuid] = coordinates
                
                if dimension:
                    player.dimension = dimension
                
                logger.debug(f"Updated coordinates for {player.display_name}: {coordinates}")
    
    def get_players_in_region(self, region_id: str) -> List[Player]:
        """Get all players in a specific region"""
        region = self.regions.get(region_id)
        if not region:
            return []
        
        players_in_region = []
        rx, ry, rz = region.coordinates
        rw, rh, rd = region.size
        
        for player_uuid, coords in self.player_coordinates.items():
            px, py, pz = coords
            
            if (rx - rw/2 <= px <= rx + rw/2 and
                ry - rh/2 <= py <= ry + rh/2 and
                rz - rd/2 <= pz <= rz + rd/2):
                
                player = self.get_player(player_uuid)
                if player:
                    players_in_region.append(player)
        
        return players_in_region
    
    def get_players_near(self, coordinates: Tuple[float, float, float], radius: float) -> List[Player]:
        """Get all players within a radius of coordinates"""
        players_near = []
        cx, cy, cz = coordinates
        
        for player_uuid, coords in self.player_coordinates.items():
            px, py, pz = coords
            distance = math.sqrt((cx - px)**2 + (cy - py)**2 + (cz - pz)**2)
            
            if distance <= radius:
                player = self.get_player(player_uuid)
                if player:
                    players_near.append(player)
        
        return players_near
    
    # Region Management Methods
    
    def create_region(self, name: str, owner: str, coordinates: Tuple[float, float, float], 
                     size: Tuple[int, int, int], region_type: str = "claim") -> str:
        """Create a new region"""
        with self.lock:
            region_id = str(uuid.uuid4())
            
            region = ServerRegion(
                region_id=region_id,
                name=name,
                owner=owner,
                coordinates=coordinates,
                size=size,
                type=region_type,
                permissions={"owner": ["all"], "public": ["view"]},
                created_date=datetime.now(),
                expiry_date=None,
                description=f"Region created by {owner}",
                flags={"pvp": False, "mob_spawning": True, "weather": True}
            )
            
            self.regions[region_id] = region
            logger.info(f"Created region '{name}' by {owner}")
            return region_id
    
    def delete_region(self, region_id: str, requester: str) -> bool:
        """Delete a region"""
        with self.lock:
            region = self.regions.get(region_id)
            if not region:
                return False
            
            if requester != region.owner and "admin" not in self.get_player_permissions(requester):
                return False
            
            del self.regions[region_id]
            logger.info(f"Deleted region '{region.name}' by {requester}")
            return True
    
    # Command Management Methods
    
    def get_command(self, command_name: str) -> Optional[ServerCommand]:
        """Get command by name or alias"""
        command = self.commands.get(command_name)
        if command:
            return command
        
        # Check aliases
        for cmd in self.commands.values():
            if command_name in cmd.aliases:
                return cmd
        
        return None
    
    def get_commands_by_category(self, category: str) -> List[ServerCommand]:
        """Get all commands in a specific category"""
        return [cmd for cmd in self.commands.values() if cmd.category == category]
    
    def get_player_permissions(self, player_identifier: str) -> List[str]:
        """Get player permissions"""
        player = self.get_player(player_identifier)
        if player:
            return player.permissions
        return []
    
    def can_execute_command(self, player_identifier: str, command_name: str) -> bool:
        """Check if player can execute a command"""
        player = self.get_player(player_identifier)
        command = self.get_command(command_name)
        
        if not player or not command:
            return False
        
        if not command.enabled:
            return False
        
        # Check permissions
        for required_perm in command.permissions:
            if required_perm not in player.permissions:
                return False
        
        return True
    
    # Server Information Methods
    
    def get_server_status(self) -> Dict:
        """Get comprehensive server status"""
        return {
            "status": self.server_status,
            "uptime": str(self.server_uptime),
            "start_time": self.server_start_time.isoformat(),
            "max_players": self.max_players,
            "current_players": self.current_players,
            "online_players": len(self.online_players),
            "total_players": len(self.players) + len(self.bots),
            "bots_online": len([b for b in self.bots.values() if b.is_online]),
            "regions": len(self.regions),
            "commands": len(self.commands)
        }
    
    def get_online_players(self) -> List[Dict]:
        """Get list of online players"""
        online_players = []
        
        for player_uuid in self.online_players:
            player = self.get_player(player_uuid)
            if player:
                online_players.append({
                    "uuid": player.uuid,
                    "username": player.username,
                    "display_name": player.display_name,
                    "is_bot": player.is_bot,
                    "coordinates": player.coordinates,
                    "dimension": player.dimension,
                    "health": player.health,
                    "food": player.food,
                    "level": player.level
                })
        
        return online_players
    
    def get_player_statistics(self) -> Dict:
        """Get player statistics"""
        total_players = len(self.players) + len(self.bots)
        online_players = len(self.online_players)
        bots_online = len([b for b in self.bots.values() if b.is_online])
        
        return {
            "total_players": total_players,
            "online_players": online_players,
            "offline_players": total_players - online_players,
            "bots_total": len(self.bots),
            "bots_online": bots_online,
            "humans_total": len(self.players),
            "humans_online": online_players - bots_online,
            "regions": len(self.regions),
            "commands": len(self.commands)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Server Manager...")
        self.stop_updates.set()
        
        if self.update_thread:
            self.update_thread.join(timeout=5)
        
        self.save_config()
        logger.info("Server Manager cleanup completed")

# Example usage
if __name__ == "__main__":
    try:
        # Create server manager instance
        server_manager = ServerManager()
        
        # Print server status
        print("=== Server Manager Status ===")
        print(json.dumps(server_manager.get_server_status(), indent=2))
        
        # Print online players
        print("\n=== Online Players ===")
        online_players = server_manager.get_online_players()
        for player in online_players:
            print(f"{player['display_name']} ({player['username']}) at {player['coordinates']}")
        
        # Print available commands
        print("\n=== Available Commands ===")
        for cmd in server_manager.commands.values():
            print(f"/{cmd.name}: {cmd.description}")
        
        # Keep running for a while
        print("\n=== Running for 30 seconds to demonstrate functionality ===")
        time.sleep(30)
        
        # Print updated status
        print("\n=== Updated Status ===")
        print(json.dumps(server_manager.get_server_status(), indent=2))
        
        # Cleanup
        server_manager.cleanup()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        if 'server_manager' in locals():
            server_manager.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        if 'server_manager' in locals():
            server_manager.cleanup()