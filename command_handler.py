#!/usr/bin/env python3
"""
Command Handler - Minecraft Bot Hub Command Management System
Handles all server commands, coordinates, and command execution
"""

import json
import time
import uuid
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set, Union, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
import math
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommandContext:
    """Context for command execution"""
    player_uuid: str
    player_name: str
    coordinates: Tuple[float, float, float]
    dimension: str
    gamemode: str
    permissions: List[str]
    timestamp: datetime
    command: str
    arguments: List[str]
    raw_input: str

@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Optional[Dict[str, any]]
    error: Optional[str]
    execution_time: float
    timestamp: datetime
    command: str
    player_uuid: str

@dataclass
class CommandCooldown:
    """Command cooldown tracking"""
    player_uuid: str
    command: str
    last_used: datetime
    uses_count: int

@dataclass
class CommandUsage:
    """Command usage statistics"""
    command: str
    total_uses: int
    successful_uses: int
    failed_uses: int
    average_execution_time: float
    last_used: datetime
    players_used: Set[str]

class CommandHandler:
    """
    Comprehensive command handling system for Minecraft Bot Hub
    Manages all server commands, coordinates, and execution
    """
    
    def __init__(self, config_file: str = "commands_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Core data structures
        self.commands: Dict[str, Dict[str, any]] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.cooldowns: Dict[str, CommandCooldown] = {}
        self.usage_stats: Dict[str, CommandUsage] = {}
        self.player_homes: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
        self.warps: Dict[str, Dict[str, any]] = {}
        self.land_claims: Dict[str, Dict[str, any]] = {}
        
        # Server managers (will be set externally)
        self.server_manager = None
        self.inventory_manager = None
        
        # Command categories
        self.categories = {
            "movement": ["tp", "home", "spawn", "warp", "tpa", "tpahere"],
            "land": ["claim", "unclaim", "info", "list", "trust", "untrust"],
            "economy": ["balance", "pay", "shop", "sell", "buy", "auction", "daily", "quest", "mine"],
            "items": ["kit", "give", "take", "repair", "enchant", "rename"],
            "social": ["msg", "tell", "reply", "ignore", "friend", "party"],
            "admin": ["ban", "kick", "mute", "op", "deop", "restart"],
            "info": ["help", "list", "who", "time", "weather", "seed"],
            "fun": ["hat", "ride", "jump", "fly", "speed", "effect"]
        }
        
        # Threading and synchronization
        self.lock = threading.RLock()
        self.update_thread = None
        self.stop_updates = threading.Event()
        
        # Initialize the system
        self.load_config()
        self.initialize_default_commands()
        self.initialize_default_warps()
        self.start_background_tasks()
        
        logger.info("Command Handler initialized successfully")
    
    def load_config(self):
        """Load command configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                    # Load commands
                    self.commands = config_data.get('commands', {})
                    
                    # Load player homes
                    self.player_homes = config_data.get('player_homes', {})
                    
                    # Load warps
                    self.warps = config_data.get('warps', {})
                    
                    # Load land claims
                    self.land_claims = config_data.get('land_claims', {})
                    
                    logger.info(f"Loaded {len(self.commands)} commands, {len(self.player_homes)} homes, {len(self.warps)} warps")
                    
            else:
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default command configuration"""
        logger.info("Creating default command configuration...")
        
        # Create default commands
        self.initialize_default_commands()
        
        # Create default warps
        self.initialize_default_warps()
        
        # Save configuration
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "commands": self.commands,
            "player_homes": self.player_homes,
            "warps": self.warps,
            "land_claims": self.land_claims,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def initialize_default_commands(self):
        """Initialize default server commands"""
        default_commands = {
            "tp": {
                "description": "Teleport to coordinates or player",
                "usage": "/tp <x> <y> <z> or /tp <player>",
                "aliases": ["teleport"],
                "permissions": ["command.tp"],
                "cooldown": 5,
                "category": "movement",
                "examples": ["/tp 100 64 100", "/tp IronMiner"],
                "enabled": True,
                "handler": "handle_tp_command"
            },
            "claim": {
                "description": "Claim land for building",
                "usage": "/claim <name> <size>",
                "aliases": ["land"],
                "permissions": ["command.claim"],
                "cooldown": 60,
                "category": "land",
                "examples": ["/claim MyHouse 20x20"],
                "enabled": True,
                "handler": "handle_claim_command"
            },
            "home": {
                "description": "Set or teleport to home",
                "usage": "/home [set] [name]",
                "aliases": ["h"],
                "permissions": ["command.home"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/home", "/home set", "/home set Main"],
                "enabled": True,
                "handler": "handle_home_command"
            },
            "spawn": {
                "description": "Teleport to spawn",
                "usage": "/spawn",
                "aliases": ["s"],
                "permissions": ["command.spawn"],
                "cooldown": 30,
                "category": "movement",
                "examples": ["/spawn"],
                "enabled": True,
                "handler": "handle_spawn_command"
            },
            "tpa": {
                "description": "Request teleport to player",
                "usage": "/tpa <player>",
                "aliases": ["teleportask"],
                "permissions": ["command.tpa"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/tpa IronMiner"],
                "enabled": True,
                "handler": "handle_tpa_command"
            },
            "balance": {
                "description": "Check your balance",
                "usage": "/balance [player]",
                "aliases": ["bal", "money"],
                "permissions": ["command.balance"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/balance", "/balance IronMiner"],
                "enabled": True,
                "handler": "handle_balance_command"
            },
            "pay": {
                "description": "Pay another player",
                "usage": "/pay <player> <amount>",
                "aliases": ["send"],
                "permissions": ["command.pay"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/pay IronMiner 100"],
                "enabled": True,
                "handler": "handle_pay_command"
            },
            "kit": {
                "description": "Get a starter kit",
                "usage": "/kit [name]",
                "aliases": ["starter"],
                "permissions": ["command.kit"],
                "cooldown": 86400,  # 24 hours
                "category": "items",
                "examples": ["/kit", "/kit builder"],
                "enabled": True,
                "handler": "handle_kit_command"
            },
            "warp": {
                "description": "Teleport to a warp point",
                "usage": "/warp <name>",
                "aliases": ["w"],
                "permissions": ["command.warp"],
                "cooldown": 10,
                "category": "movement",
                "examples": ["/warp shop", "/warp arena"],
                "enabled": True,
                "handler": "handle_warp_command"
            },
            "setwarp": {
                "description": "Set a warp point",
                "usage": "/setwarp <name>",
                "aliases": ["sw"],
                "permissions": ["command.setwarp"],
                "cooldown": 0,
                "category": "movement",
                "examples": ["/setwarp shop"],
                "enabled": True,
                "handler": "handle_setwarp_command"
            },
            "help": {
                "description": "Show available commands",
                "usage": "/help [category]",
                "aliases": ["h", "?"],
                "permissions": ["command.help"],
                "cooldown": 0,
                "category": "info",
                "examples": ["/help", "/help movement", "/help economy"],
                "enabled": True,
                "handler": "handle_help_command"
            },
            "list": {
                "description": "List online players",
                "usage": "/list",
                "aliases": ["who", "online"],
                "permissions": ["command.list"],
                "cooldown": 0,
                "category": "info",
                "examples": ["/list"],
                "enabled": True,
                "handler": "handle_list_command"
            },
            "time": {
                "description": "Show server time",
                "usage": "/time",
                "aliases": ["clock"],
                "permissions": ["command.time"],
                "cooldown": 0,
                "category": "info",
                "examples": ["/time"],
                "enabled": True,
                "handler": "handle_time_command"
            },
            "weather": {
                "description": "Show or change weather",
                "usage": "/weather [clear/rain/thunder]",
                "aliases": ["w"],
                "permissions": ["command.weather"],
                "cooldown": 0,
                "category": "info",
                "examples": ["/weather", "/weather clear"],
                "enabled": True,
                "handler": "handle_weather_command"
            },
            "sell": {
                "description": "Sell items for money",
                "usage": "/sell <item> <quantity>",
                "aliases": ["trade"],
                "permissions": ["command.sell"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/sell diamond 5", "/sell stone 64"],
                "enabled": True,
                "handler": "handle_sell_command"
            },
            "daily": {
                "description": "Claim daily reward",
                "usage": "/daily",
                "aliases": ["reward"],
                "permissions": ["command.daily"],
                "cooldown": 86400,  # 24 hours
                "category": "economy",
                "examples": ["/daily"],
                "enabled": True,
                "handler": "handle_daily_command"
            },
            "quest": {
                "description": "Manage quests for rewards",
                "usage": "/quest <list|accept|complete> [quest_name]",
                "aliases": ["mission"],
                "permissions": ["command.quest"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/quest list", "/quest accept Mining Master", "/quest complete Farmer"],
                "enabled": True,
                "handler": "handle_quest_command"
            },
            "mine": {
                "description": "Mine resources for money",
                "usage": "/mine <resource> [quantity]",
                "aliases": ["dig"],
                "permissions": ["command.mine"],
                "cooldown": 0,
                "category": "economy",
                "examples": ["/mine stone 64", "/mine diamond 1"],
                "enabled": True,
                "handler": "handle_mine_command"
            }
        }
        
        self.commands.update(default_commands)
        logger.info(f"Initialized {len(self.commands)} default commands")
    
    def initialize_default_warps(self):
        """Initialize default warp points"""
        default_warps = {
            "spawn": {
                "name": "Spawn",
                "coordinates": (0, 64, 0),
                "dimension": "overworld",
                "owner": "system",
                "description": "Server spawn point",
                "public": True,
                "created_date": datetime.now().isoformat()
            },
            "shop": {
                "name": "Shop",
                "coordinates": (100, 64, 0),
                "dimension": "overworld",
                "owner": "system",
                "description": "Trading area",
                "public": True,
                "created_date": datetime.now().isoformat()
            },
            "arena": {
                "name": "Arena",
                "coordinates": (-100, 64, 0),
                "dimension": "overworld",
                "owner": "system",
                "description": "PvP arena",
                "public": True,
                "created_date": datetime.now().isoformat()
            }
        }
        
        self.warps.update(default_warps)
        logger.info(f"Initialized {len(self.warps)} default warps")
    
    def start_background_tasks(self):
        """Start background update tasks"""
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Background update tasks started")
    
    def update_loop(self):
        """Main update loop for command handler"""
        while not self.stop_updates.is_set():
            try:
                # Clean up expired cooldowns
                self.cleanup_expired_cooldowns()
                
                # Save configuration periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.save_config()
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(300)
    
    def cleanup_expired_cooldowns(self):
        """Clean up expired command cooldowns"""
        current_time = datetime.now()
        expired_cooldowns = []
        
        for cooldown_key, cooldown in self.cooldowns.items():
            command_info = self.commands.get(cooldown.command)
            if command_info:
                cooldown_duration = command_info.get('cooldown', 0)
                if cooldown_duration > 0:
                    time_since_last = (current_time - cooldown.last_used).total_seconds()
                    if time_since_last > cooldown_duration:
                        expired_cooldowns.append(cooldown_key)
        
        for cooldown_key in expired_cooldowns:
            del self.cooldowns[cooldown_key]
    
    # Command Execution Methods
    
    def execute_command(self, player_uuid: str, player_name: str, coordinates: Tuple[float, float, float],
                       dimension: str, gamemode: str, permissions: List[str], command_input: str) -> CommandResult:
        """Execute a command for a player"""
        start_time = time.time()
        
        try:
            # Parse command input
            parts = command_input.strip().split()
            if not parts:
                return CommandResult(
                    success=False,
                    message="No command specified",
                    data=None,
                    error="Empty command",
                    execution_time=0,
                    timestamp=datetime.now(),
                    command="",
                    player_uuid=player_uuid
                )
            
            command_name = parts[0].lower().lstrip('/')
            arguments = parts[1:] if len(parts) > 1 else []
            
            # Create command context
            context = CommandContext(
                player_uuid=player_uuid,
                player_name=player_name,
                coordinates=coordinates,
                dimension=dimension,
                gamemode=gamemode,
                permissions=permissions,
                timestamp=datetime.now(),
                command=command_name,
                arguments=arguments,
                raw_input=command_input
            )
            
            # Check if command exists
            if command_name not in self.commands:
                return CommandResult(
                    success=False,
                    message=f"Unknown command: {command_name}",
                    data=None,
                    error="Command not found",
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    command=command_name,
                    player_uuid=player_uuid
                )
            
            command_info = self.commands[command_name]
            
            # Check if command is enabled
            if not command_info.get('enabled', True):
                return CommandResult(
                    success=False,
                    message=f"Command {command_name} is disabled",
                    data=None,
                    error="Command disabled",
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    command=command_name,
                    player_uuid=player_uuid
                )
            
            # Check permissions
            required_permissions = command_info.get('permissions', [])
            if required_permissions:
                has_permission = any(perm in permissions for perm in required_permissions)
                if not has_permission:
                    return CommandResult(
                        success=False,
                        message=f"You don't have permission to use {command_name}",
                        data=None,
                        error="Insufficient permissions",
                        execution_time=time.time() - start_time,
                        timestamp=datetime.now(),
                        command=command_name,
                        player_uuid=player_uuid
                    )
            
            # Check cooldown
            if not self.check_cooldown(player_uuid, command_name):
                cooldown_duration = command_info.get('cooldown', 0)
                return CommandResult(
                    success=False,
                    message=f"Command {command_name} is on cooldown. Wait {cooldown_duration} seconds.",
                    data=None,
                    error="Command on cooldown",
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    command=command_name,
                    player_uuid=player_uuid
                )
            
            # Execute command
            handler_name = command_info.get('handler', f'handle_{command_name}_command')
            handler = getattr(self, handler_name, None)
            
            if handler and callable(handler):
                result = handler(context)
                
                # Update cooldown
                self.update_cooldown(player_uuid, command_name)
                
                # Update usage statistics
                self.update_usage_stats(command_name, player_uuid, True, time.time() - start_time)
                
                return CommandResult(
                    success=True,
                    message=result.get('message', f'Command {command_name} executed successfully'),
                    data=result.get('data'),
                    error=None,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    command=command_name,
                    player_uuid=player_uuid
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"Command {command_name} has no handler",
                    data=None,
                    error="No handler found",
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    command=command_name,
                    player_uuid=player_uuid
                )
                
        except Exception as e:
            logger.error(f"Error executing command '{command_input}' for {player_uuid}: {e}")
            
            return CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}",
                data=None,
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=datetime.now(),
                command=command_input.split()[0] if command_input else "",
                player_uuid=player_uuid
            )
    
    def check_cooldown(self, player_uuid: str, command: str) -> bool:
        """Check if a command is on cooldown for a player"""
        cooldown_key = f"{player_uuid}:{command}"
        cooldown = self.cooldowns.get(cooldown_key)
        
        if not cooldown:
            return True
        
        command_info = self.commands.get(command, {})
        cooldown_duration = command_info.get('cooldown', 0)
        
        if cooldown_duration <= 0:
            return True
        
        time_since_last = (datetime.now() - cooldown.last_used).total_seconds()
        return time_since_last >= cooldown_duration
    
    def update_cooldown(self, player_uuid: str, command: str):
        """Update command cooldown for a player"""
        cooldown_key = f"{player_uuid}:{command}"
        
        if cooldown_key in self.cooldowns:
            cooldown = self.cooldowns[cooldown_key]
            cooldown.last_used = datetime.now()
            cooldown.uses_count += 1
        else:
            self.cooldowns[cooldown_key] = CommandCooldown(
                player_uuid=player_uuid,
                command=command,
                last_used=datetime.now(),
                uses_count=1
            )
    
    def update_usage_stats(self, command: str, player_uuid: str, success: bool, execution_time: float):
        """Update command usage statistics"""
        if command not in self.usage_stats:
            self.usage_stats[command] = CommandUsage(
                command=command,
                total_uses=0,
                successful_uses=0,
                failed_uses=0,
                average_execution_time=0.0,
                last_used=datetime.now(),
                players_used=set()
            )
        
        stats = self.usage_stats[command]
        stats.total_uses += 1
        stats.last_used = datetime.now()
        stats.players_used.add(player_uuid)
        
        if success:
            stats.successful_uses += 1
        else:
            stats.failed_uses += 1
        
        # Update average execution time
        if stats.total_uses == 1:
            stats.average_execution_time = execution_time
        else:
            stats.average_execution_time = (
                (stats.average_execution_time * (stats.total_uses - 1) + execution_time) / stats.total_uses
            )
    
    # Command Handlers
    
    def handle_tp_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle teleport command"""
        if not context.arguments:
            return {"message": "Usage: /tp <x> <y> <z> or /tp <player>", "data": None}
        
        if len(context.arguments) == 3:
            # Teleport to coordinates
            try:
                x = float(context.arguments[0])
                y = float(context.arguments[1])
                z = float(context.arguments[2])
                
                # Update player coordinates
                if self.server_manager:
                    self.server_manager.update_player_coordinates(context.player_uuid, (x, y, z))
                
                return {
                    "message": f"Teleported to coordinates ({x}, {y}, {z})",
                    "data": {"coordinates": (x, y, z)}
                }
            except ValueError:
                return {"message": "Invalid coordinates. Use numbers.", "data": None}
        
        elif len(context.arguments) == 1:
            # Teleport to player
            target_name = context.arguments[0]
            
            if self.server_manager:
                target_player = self.server_manager.get_player(target_name)
                if target_player:
                    target_coords = target_player.coordinates
                    self.server_manager.update_player_coordinates(context.player_uuid, target_coords)
                    
                    return {
                        "message": f"Teleported to {target_player.display_name} at {target_coords}",
                        "data": {"target": target_player.display_name, "coordinates": target_coords}
                    }
                else:
                    return {"message": f"Player {target_name} not found", "data": None}
            else:
                return {"message": "Server manager not available", "data": None}
        
        return {"message": "Usage: /tp <x> <y> <z> or /tp <player>", "data": None}
    
    def handle_home_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle home command"""
        if not context.arguments:
            # Teleport to default home
            if context.player_uuid in self.player_homes:
                home_coords = self.player_homes[context.player_uuid].get("default")
                if home_coords:
                    if self.server_manager:
                        self.server_manager.update_player_coordinates(context.player_uuid, home_coords)
                    
                    return {
                        "message": "Teleported to your home",
                        "data": {"coordinates": home_coords}
                    }
                else:
                    return {"message": "You don't have a home set. Use /home set to set one.", "data": None}
            else:
                return {"message": "You don't have a home set. Use /home set to set one.", "data": None}
        
        elif context.arguments[0] == "set":
            # Set home
            home_name = context.arguments[1] if len(context.arguments) > 1 else "default"
            
            if context.player_uuid not in self.player_homes:
                self.player_homes[context.player_uuid] = {}
            
            self.player_homes[context.player_uuid][home_name] = context.coordinates
            
            return {
                "message": f"Home '{home_name}' set at {context.coordinates}",
                "data": {"home_name": home_name, "coordinates": context.coordinates}
            }
        
        elif context.arguments[0] == "list":
            # List homes
            if context.player_uuid in self.player_homes:
                homes = list(self.player_homes[context.player_uuid].keys())
                return {
                    "message": f"Your homes: {', '.join(homes)}",
                    "data": {"homes": homes}
                }
            else:
                return {"message": "You don't have any homes set.", "data": None}
        
        else:
            # Teleport to specific home
            home_name = context.arguments[0]
            
            if context.player_uuid in self.player_homes:
                home_coords = self.player_homes[context.player_uuid].get(home_name)
                if home_coords:
                    if self.server_manager:
                        self.server_manager.update_player_coordinates(context.player_uuid, home_coords)
                    
                    return {
                        "message": f"Teleported to home '{home_name}'",
                        "data": {"home_name": home_name, "coordinates": home_coords}
                    }
                else:
                    return {"message": f"Home '{home_name}' not found", "data": None}
            else:
                return {"message": "You don't have any homes set.", "data": None}
    
    def handle_spawn_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle spawn command"""
        spawn_coords = (0, 64, 0)  # Default spawn
        
        if self.server_manager:
            self.server_manager.update_player_coordinates(context.player_uuid, spawn_coords)
        
        return {
            "message": "Teleported to spawn",
            "data": {"coordinates": spawn_coords}
        }
    
    def handle_warp_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle warp command"""
        if not context.arguments:
            return {"message": "Usage: /warp <name>", "data": None}
        
        warp_name = context.arguments[0].lower()
        
        if warp_name in self.warps:
            warp = self.warps[warp_name]
            warp_coords = warp["coordinates"]
            
            if self.server_manager:
                self.server_manager.update_player_coordinates(context.player_uuid, warp_coords)
            
            return {
                "message": f"Warped to {warp['name']}",
                "data": {"warp": warp}
            }
        else:
            return {"message": f"Warp '{warp_name}' not found", "data": None}
    
    def handle_setwarp_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle setwarp command"""
        if not context.arguments:
            return {"message": "Usage: /setwarp <name>", "data": None}
        
        warp_name = context.arguments[0].lower()
        
        # Check if warp already exists
        if warp_name in self.warps:
            return {"message": f"Warp '{warp_name}' already exists", "data": None}
        
        # Create new warp
        self.warps[warp_name] = {
            "name": warp_name.capitalize(),
            "coordinates": context.coordinates,
            "dimension": context.dimension,
            "owner": context.player_uuid,
            "description": f"Warp set by {context.player_name}",
            "public": True,
            "created_date": datetime.now().isoformat()
        }
        
        return {
            "message": f"Warp '{warp_name}' set at {context.coordinates}",
            "data": {"warp": self.warps[warp_name]}
        }
    
    def handle_balance_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle balance command"""
        if not context.arguments:
            # Show own balance
            if self.inventory_manager:
                balance = self.inventory_manager.get_balance(context.player_uuid)
                return {
                    "message": f"Your balance: {balance} coins",
                    "data": {"balance": balance, "player": context.player_name}
                }
            else:
                return {"message": "Economy system not available", "data": None}
        
        else:
            # Show other player's balance
            target_name = context.arguments[0]
            
            if self.server_manager:
                target_player = self.server_manager.get_player(target_name)
                if target_player and self.inventory_manager:
                    balance = self.inventory_manager.get_balance(target_player.uuid)
                    return {
                        "message": f"{target_player.display_name}'s balance: {balance} coins",
                        "data": {"balance": balance, "player": target_player.display_name}
                    }
                else:
                    return {"message": f"Player {target_name} not found", "data": None}
            else:
                return {"message": "Server manager not available", "data": None}
    
    def handle_pay_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle pay command"""
        if len(context.arguments) != 2:
            return {"message": "Usage: /pay <player> <amount>", "data": None}
        
        target_name = context.arguments[0]
        try:
            amount = float(context.arguments[1])
        except ValueError:
            return {"message": "Invalid amount. Use a number.", "data": None}
        
        if amount <= 0:
            return {"message": "Amount must be positive", "data": None}
        
        if self.server_manager and self.inventory_manager:
            target_player = self.server_manager.get_player(target_name)
            if target_player:
                success = self.inventory_manager.transfer_money(
                    context.player_uuid, target_player.uuid, amount, f"Payment to {target_name}"
                )
                
                if success:
                    return {
                        "message": f"Paid {amount} coins to {target_player.display_name}",
                        "data": {"amount": amount, "target": target_player.display_name}
                    }
                else:
                    return {"message": "Payment failed. Check your balance.", "data": None}
            else:
                return {"message": f"Player {target_name} not found", "data": None}
        else:
            return {"message": "Economy system not available", "data": None}
    
    def handle_kit_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle kit command"""
        kit_name = context.arguments[0] if context.arguments else "starter"
        
        if self.inventory_manager:
            # Give starter items
            items_given = []
            
            if kit_name == "starter":
                # Starter kit
                starter_items = [
                    ("stone_pickaxe", 1),
                    ("bread", 16),
                    ("torch", 32)
                ]
                
                for item_id, quantity in starter_items:
                    if self.inventory_manager.add_item_to_inventory(context.player_uuid, item_id, quantity):
                        items_given.append(f"{quantity}x {item_id}")
                
                return {
                    "message": f"Received starter kit: {', '.join(items_given)}",
                    "data": {"kit_name": kit_name, "items": items_given}
                }
            
            elif kit_name == "builder":
                # Builder kit
                builder_items = [
                    ("stone", 64),
                    ("oak_planks", 64),
                    ("glass", 32),
                    ("stone_pickaxe", 1)
                ]
                
                for item_id, quantity in builder_items:
                    if self.inventory_manager.add_item_to_inventory(context.player_uuid, item_id, quantity):
                        items_given.append(f"{quantity}x {item_id}")
                
                return {
                    "message": f"Received builder kit: {', '.join(items_given)}",
                    "data": {"kit_name": kit_name, "items": items_given}
                }
            
            else:
                return {"message": f"Kit '{kit_name}' not found", "data": None}
        else:
            return {"message": "Inventory system not available", "data": None}
    
    def handle_help_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle help command"""
        if not context.arguments:
            # Show all categories
            categories = list(self.categories.keys())
            return {
                "message": f"Available categories: {', '.join(categories)}. Use /help <category> for more info.",
                "data": {"categories": categories}
            }
        
        category = context.arguments[0].lower()
        
        if category in self.categories:
            commands_in_category = self.categories[category]
            help_text = f"Commands in {category} category:\n"
            
            for cmd_name in commands_in_category:
                if cmd_name in self.commands:
                    cmd_info = self.commands[cmd_name]
                    help_text += f"/{cmd_name}: {cmd_info['description']}\n"
                    help_text += f"  Usage: {cmd_info['usage']}\n"
            
            return {
                "message": help_text,
                "data": {"category": category, "commands": commands_in_category}
            }
        else:
            return {"message": f"Category '{category}' not found", "data": None}
    
    def handle_list_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle list command"""
        if self.server_manager:
            online_players = self.server_manager.get_online_players()
            
            if online_players:
                player_list = [f"{p['display_name']} ({p['username']})" for p in online_players]
                return {
                    "message": f"Online players ({len(online_players)}): {', '.join(player_list)}",
                    "data": {"players": online_players, "count": len(online_players)}
                }
            else:
                return {"message": "No players online", "data": {"players": [], "count": 0}}
        else:
            return {"message": "Server manager not available", "data": None}
    
    def handle_time_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle time command"""
        current_time = datetime.now()
        server_time = current_time.strftime("%H:%M:%S")
        server_date = current_time.strftime("%Y-%m-%d")
        
        return {
            "message": f"Server time: {server_time} | Date: {server_date}",
            "data": {"time": server_time, "date": server_date, "timestamp": current_time.isoformat()}
        }
    
    def handle_weather_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle weather command"""
        if not context.arguments:
            # Show current weather
            return {
                "message": "Current weather: Clear (default)",
                "data": {"weather": "clear"}
            }
        
        weather_type = context.arguments[0].lower()
        
        if weather_type in ["clear", "rain", "thunder"]:
            return {
                "message": f"Weather changed to: {weather_type}",
                "data": {"weather": weather_type}
            }
        else:
            return {"message": "Invalid weather type. Use: clear, rain, or thunder", "data": None}
    
    # Earning Commands for Survival Mode
    
    def handle_sell_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle sell command - sell items for money"""
        if len(context.arguments) < 2:
            return {"message": "Usage: /sell <item> <quantity>", "data": None}
        
        item_id = context.arguments[0].lower()
        try:
            quantity = int(context.arguments[1])
        except ValueError:
            return {"message": "Invalid quantity. Use a number.", "data": None}
        
        if quantity <= 0:
            return {"message": "Quantity must be positive", "data": None}
        
        if self.inventory_manager:
            # Check if player has the item
            if self.inventory_manager.has_item_in_inventory(context.player_uuid, item_id, quantity):
                # Get item value
                item_value = self.inventory_manager.get_item_value(item_id)
                total_value = item_value * quantity
                
                # Remove item and add money
                if self.inventory_manager.remove_item_from_inventory(context.player_uuid, item_id, quantity):
                    if self.inventory_manager.add_money(context.player_uuid, total_value, f"Sold {quantity}x {item_id}"):
                        return {
                            "message": f"Sold {quantity}x {item_id} for {total_value} dollars!",
                            "data": {"item": item_id, "quantity": quantity, "value": total_value}
                        }
                    else:
                        # Rollback item removal if money addition failed
                        self.inventory_manager.add_item_to_inventory(context.player_uuid, item_id, quantity)
                        return {"message": "Failed to process sale", "data": None}
                else:
                    return {"message": f"You don't have {quantity}x {item_id}", "data": None}
            else:
                return {"message": f"You don't have {quantity}x {item_id}", "data": None}
        else:
            return {"message": "Economy system not available", "data": None}
    
    def handle_daily_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle daily command - claim daily reward"""
        if self.inventory_manager:
            # Check if player can claim daily reward (implement cooldown logic here)
            daily_reward = 100  # Base daily reward
            bonus_multiplier = 1.0
            
            # Add bonus for consecutive days (simplified)
            if hasattr(context, 'consecutive_days'):
                bonus_multiplier = 1 + (context.consecutive_days * 0.1)
            
            total_reward = int(daily_reward * bonus_multiplier)
            
            if self.inventory_manager.add_money(context.player_uuid, total_reward, "Daily reward"):
                return {
                    "message": f"Daily reward claimed! You earned {total_reward} dollars!",
                    "data": {"reward": total_reward, "bonus_multiplier": bonus_multiplier}
                }
            else:
                return {"message": "Failed to claim daily reward", "data": None}
        else:
            return {"message": "Economy system not available", "data": None}
    
    def handle_quest_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle quest command - complete quests for money"""
        if not context.arguments:
            return {"message": "Usage: /quest <list|accept|complete> [quest_name]", "data": None}
        
        action = context.arguments[0].lower()
        
        if action == "list":
            available_quests = [
                {"name": "Mining Master", "description": "Mine 100 stone blocks", "reward": 500, "type": "mining"},
                {"name": "Farmer", "description": "Harvest 50 wheat", "reward": 300, "type": "farming"},
                {"name": "Builder", "description": "Place 200 blocks", "reward": 400, "type": "building"},
                {"name": "Explorer", "description": "Travel 1000 blocks", "reward": 200, "type": "exploration"}
            ]
            return {
                "message": "Available quests:\n" + "\n".join([f"{q['name']}: {q['description']} - Reward: {q['reward']} dollars" for q in available_quests]),
                "data": {"quests": available_quests}
            }
        
        elif action == "accept":
            if len(context.arguments) < 2:
                return {"message": "Usage: /quest accept <quest_name>", "data": None}
            quest_name = context.arguments[1]
            return {"message": f"Quest '{quest_name}' accepted! Check your progress with /quest status", "data": {"quest": quest_name, "status": "accepted"}}
        
        elif action == "complete":
            if len(context.arguments) < 2:
                return {"message": "Usage: /quest complete <quest_name>", "data": None}
            quest_name = context.arguments[1]
            
            # Simulate quest completion and reward
            quest_rewards = {
                "Mining Master": 500,
                "Farmer": 300,
                "Builder": 400,
                "Explorer": 200
            }
            
            if quest_name in quest_rewards:
                reward = quest_rewards[quest_name]
                if self.inventory_manager.add_money(context.player_uuid, reward, f"Quest completion: {quest_name}"):
                    return {
                        "message": f"Quest '{quest_name}' completed! You earned {reward} dollars!",
                        "data": {"quest": quest_name, "reward": reward}
                    }
                else:
                    return {"message": "Failed to claim quest reward", "data": None}
            else:
                return {"message": f"Quest '{quest_name}' not found", "data": None}
        
        else:
            return {"message": "Invalid action. Use: list, accept, or complete", "data": None}
    
    def handle_mine_command(self, context: CommandContext) -> Dict[str, any]:
        """Handle mine command - mine resources for money"""
        if not context.arguments:
            return {"message": "Usage: /mine <resource> [quantity]", "data": None}
        
        resource = context.arguments[0].lower()
        quantity = int(context.arguments[1]) if len(context.arguments) > 1 else 1
        
        if quantity <= 0:
            return {"message": "Quantity must be positive", "data": None}
        
        # Resource values (dollars per unit)
        resource_values = {
            "stone": 1,
            "coal": 2,
            "iron": 5,
            "gold": 10,
            "diamond": 100,
            "emerald": 80,
            "redstone": 3,
            "lapis": 15
        }
        
        if resource in resource_values:
            value_per_unit = resource_values[resource]
            total_value = value_per_unit * quantity
            
            # Simulate mining (in real implementation, this would check actual inventory)
            if self.inventory_manager:
                # Add the mined resource to inventory
                if self.inventory_manager.add_item_to_inventory(context.player_uuid, resource, quantity):
                    # Give money for mining effort
                    mining_reward = int(total_value * 0.5)  # 50% of item value as mining reward
                    if self.inventory_manager.add_money(context.player_uuid, mining_reward, f"Mining reward: {quantity}x {resource}"):
                        return {
                            "message": f"You mined {quantity}x {resource} and earned {mining_reward} dollars!",
                            "data": {"resource": resource, "quantity": quantity, "reward": mining_reward, "item_value": total_value}
                        }
                    else:
                        return {"message": f"Mined {quantity}x {resource} but failed to get reward", "data": None}
                else:
                    return {"message": "Failed to add mined resource to inventory", "data": None}
            else:
                return {"message": "Inventory system not available", "data": None}
        else:
            return {"message": f"Unknown resource: {resource}. Available: {', '.join(resource_values.keys())}", "data": None}
    
    # Utility Methods
    
    def get_command_info(self, command_name: str) -> Optional[Dict[str, any]]:
        """Get information about a specific command"""
        return self.commands.get(command_name)
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get all commands in a specific category"""
        return self.categories.get(category, [])
    
    def get_all_commands(self) -> Dict[str, any]:
        """Get all available commands"""
        return self.commands.copy()
    
    def get_command_usage_stats(self, command_name: str) -> Optional[CommandUsage]:
        """Get usage statistics for a command"""
        return self.usage_stats.get(command_name)
    
    def get_player_homes(self, player_uuid: str) -> Dict[str, Tuple[float, float, float]]:
        """Get all homes for a player"""
        return self.player_homes.get(player_uuid, {})
    
    def get_warps(self) -> Dict[str, Dict[str, any]]:
        """Get all available warps"""
        return self.warps.copy()
    
    def set_server_manager(self, server_manager):
        """Set the server manager reference"""
        self.server_manager = server_manager
    
    def set_inventory_manager(self, inventory_manager):
        """Set the inventory manager reference"""
        self.inventory_manager = inventory_manager
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Command Handler...")
        self.stop_updates.set()
        
        if self.update_thread:
            self.update_thread.join(timeout=5)
        
        self.save_config()
        logger.info("Command Handler cleanup completed")

# Example usage
if __name__ == "__main__":
    try:
        # Create command handler instance
        command_handler = CommandHandler()
        
        # Print available commands
        print("=== Available Commands ===")
        for cmd_name, cmd_info in command_handler.commands.items():
            print(f"/{cmd_name}: {cmd_info['description']}")
        
        # Print command categories
        print("\n=== Command Categories ===")
        for category, commands in command_handler.categories.items():
            print(f"{category}: {', '.join(commands)}")
        
        # Test command execution
        print("\n=== Testing Command Execution ===")
        
        # Mock player context
        test_context = CommandContext(
            player_uuid="test_player",
            player_name="TestPlayer",
            coordinates=(100, 64, 100),
            dimension="overworld",
            gamemode="survival",
            permissions=["command.tp", "command.home"],
            timestamp=datetime.now(),
            command="tp",
            arguments=["200", "64", "200"],
            raw_input="/tp 200 64 200"
        )
        
        # Test home command
        result = command_handler.handle_home_command(test_context)
        print(f"Home command result: {result}")
        
        # Keep running for a while
        print("\n=== Running for 30 seconds to demonstrate functionality ===")
        time.sleep(30)
        
        # Cleanup
        command_handler.cleanup()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        if 'command_handler' in locals():
            command_handler.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        if 'command_handler' in locals():
            command_handler.cleanup()