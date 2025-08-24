#!/usr/bin/env python3
"""
Bot Vision Commander - Real-time Bot Vision and Live Command System
This system provides a live view of what all bots can see and allows real-time command input.
Think of it as a command center dashboard for your Minecraft bot army!
"""

import json
import time
import threading
import asyncio
import curses
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import math
import random
from bot_brain import BotBrain, TaskPriority, BotState

# Terminal colors and styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class BotVision:
    bot_name: str
    position: Tuple[float, float, float]
    looking_at: Tuple[float, float, float]
    nearby_blocks: List[Dict[str, Any]]
    nearby_entities: List[Dict[str, Any]]
    inventory: Dict[str, int]
    health: float
    food: float
    state: str
    last_update: datetime
    view_distance: int = 16

@dataclass
class WorldMap:
    width: int
    height: int
    blocks: Dict[Tuple[int, int], str]
    entities: Dict[Tuple[int, int], List[str]]
    last_update: datetime

class BotVisionCommander:
    def __init__(self):
        self.brain = BotBrain()
        self.bot_visions = {}
        self.world_map = WorldMap(100, 100, {}, {}, datetime.now())
        self.command_history = []
        self.live_commands = []
        self.is_running = False
        self.update_interval = 1.0  # seconds
        self.view_distance = 16
        
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
                "food": 18.0
            },
            {
                "name": "Bot2", 
                "position": (150, 64, 250),
                "looking_at": (155, 64, 255),
                "state": "building",
                "health": 19.0,
                "food": 20.0
            },
            {
                "name": "Bot3",
                "position": (200, 64, 300),
                "looking_at": (205, 64, 305),
                "state": "exploring",
                "health": 18.0,
                "food": 17.0
            }
        ]
        
        for bot_data in sample_bots:
            self._update_bot_vision(bot_data["name"], bot_data)
    
    def _update_bot_vision(self, bot_name: str, data: Dict[str, Any]):
        """Update the vision data for a specific bot"""
        # Generate nearby blocks based on position
        nearby_blocks = self._generate_nearby_blocks(data["position"])
        nearby_entities = self._generate_nearby_entities(data["position"])
        
        vision = BotVision(
            bot_name=bot_name,
            position=data["position"],
            looking_at=data["looking_at"],
            nearby_blocks=nearby_blocks,
            nearby_entities=nearby_entities,
            inventory=self._generate_sample_inventory(),
            health=data["health"],
            food=data["food"],
            state=data["state"],
            last_update=datetime.now()
        )
        
        self.bot_visions[bot_name] = vision
        
        # Update world map
        self._update_world_map(vision)
    
    def _generate_nearby_blocks(self, position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """Generate sample nearby blocks for a bot position"""
        blocks = []
        x, y, z = position
        
        # Generate blocks in view distance
        for dx in range(-self.view_distance, self.view_distance + 1):
            for dy in range(-8, 8 + 1):
                for dz in range(-self.view_distance, self.view_distance + 1):
                    if abs(dx) + abs(dy) + abs(dz) <= self.view_distance:
                        block_x, block_y, block_z = x + dx, y + dy, z + dz
                        
                        # Generate realistic block types
                        block_type = self._get_block_type_at(block_x, block_y, block_z)
                        
                        if block_type != "air":
                            blocks.append({
                                "position": (block_x, block_y, block_z),
                                "type": block_type,
                                "distance": math.sqrt(dx*dx + dy*dy + dz*dz)
                            })
        
        return blocks[:50]  # Limit to 50 blocks for performance
    
    def _generate_nearby_entities(self, position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """Generate sample nearby entities for a bot position"""
        entities = []
        x, y, z = position
        
        # Generate some sample entities
        entity_types = ["zombie", "skeleton", "creeper", "cow", "pig", "chicken", "villager"]
        
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
                "health": random.randint(1, 20) if entity_type in ["zombie", "skeleton", "creeper"] else 10
            })
        
        return entities
    
    def _get_block_type_at(self, x: float, y: float, z: float) -> str:
        """Determine block type at given coordinates"""
        # Simple algorithm to generate realistic terrain
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
        items = ["wood", "stone", "iron_ore", "coal", "diamond", "food", "torch", "pickaxe"]
        inventory = {}
        
        for item in random.sample(items, random.randint(3, 6)):
            inventory[item] = random.randint(1, 20)
        
        return inventory
    
    def _update_world_map(self, vision: BotVision):
        """Update the world map with bot vision data"""
        x, y, z = vision.position
        
        # Update blocks around bot
        for block in vision.nearby_blocks:
            bx, by, bz = block["position"]
            map_key = (int(bx/10), int(bz/10))  # Group blocks into 10x10 chunks
            
            if map_key not in self.world_map.blocks:
                self.world_map.blocks[map_key] = []
            
            if block["type"] not in self.world_map.blocks[map_key]:
                self.world_map.blocks[map_key].append(block["type"])
        
        # Update entities
        for entity in vision.nearby_entities:
            ex, ey, ez = entity["position"]
            map_key = (int(ex/10), int(ez/10))
            
            if map_key not in self.world_map.entities:
                self.world_map.entities[map_key] = []
            
            if entity["type"] not in self.world_map.entities[map_key]:
                self.world_map.entities[map_key].append(entity["type"])
        
        self.world_map.last_update = datetime.now()
    
    def get_bot_vision_summary(self) -> Dict[str, Any]:
        """Get a summary of all bot visions"""
        summary = {
            "total_bots": len(self.bot_visions),
            "bot_status": {},
            "world_overview": {},
            "last_update": datetime.now().isoformat()
        }
        
        # Bot status summary
        for bot_name, vision in self.bot_visions.items():
            summary["bot_status"][bot_name] = {
                "position": vision.position,
                "state": vision.state,
                "health": vision.health,
                "food": vision.food,
                "nearby_blocks": len(vision.nearby_blocks),
                "nearby_entities": len(vision.nearby_entities),
                "inventory_count": len(vision.inventory)
            }
        
        # World overview
        summary["world_overview"] = {
            "total_blocks": len(self.world_map.blocks),
            "total_entities": len(self.world_map.entities),
            "block_types": list(set([block for blocks in self.world_map.blocks.values() for block in blocks])),
            "entity_types": list(set([entity for entities in self.world_map.entities.values() for entity in entities]))
        }
        
        return summary
    
    def process_live_command(self, command: str) -> Dict[str, Any]:
        """Process a live command and return the result"""
        timestamp = datetime.now()
        
        # Add to command history
        self.command_history.append({
            "timestamp": timestamp,
            "command": command,
            "status": "processing"
        })
        
        try:
            # Analyze command using bot brain
            analysis = self.brain.analyze_prompt(command)
            
            # Execute command
            result = self._execute_command(analysis, command)
            
            # Update command history
            self.command_history[-1]["status"] = "completed"
            self.command_history[-1]["result"] = result
            
            return {
                "success": True,
                "analysis": analysis,
                "result": result,
                "timestamp": timestamp.isoformat()
            }
            
        except Exception as e:
            # Update command history with error
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
                # Create mining task
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
                # Create building task
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
    
    def start_live_monitoring(self):
        """Start live monitoring of all bots"""
        self.is_running = True
        
        # Start background update thread
        update_thread = threading.Thread(target=self._background_updates, daemon=True)
        update_thread.start()
        
        print(f"{Colors.GREEN}🚀 Live Bot Vision Monitoring Started!{Colors.END}")
        print(f"{Colors.CYAN}Monitoring {len(self.bot_visions)} bots...{Colors.END}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}\n")
        
        try:
            while self.is_running:
                self._display_live_dashboard()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Stopping live monitoring...{Colors.END}")
            self.is_running = False
    
    def _background_updates(self):
        """Background thread for updating bot data"""
        while self.is_running:
            try:
                # Simulate bot movement and updates
                for bot_name in self.bot_visions.keys():
                    # Randomly move bots around
                    if random.random() < 0.3:  # 30% chance to move
                        current_pos = self.bot_visions[bot_name].position
                        new_x = current_pos[0] + random.randint(-5, 5)
                        new_z = current_pos[2] + random.randint(-5, 5)
                        new_pos = (new_x, current_pos[1], new_z)
                        
                        self._update_bot_vision(bot_name, {
                            "position": new_pos,
                            "looking_at": (new_x + 2, current_pos[1], new_z + 2),
                            "state": self.bot_visions[bot_name].state,
                            "health": self.bot_visions[bot_name].health,
                            "food": self.bot_visions[bot_name].food
                        })
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Background update error: {e}")
                time.sleep(5)
    
    def _display_live_dashboard(self):
        """Display the live dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}🤖 BOT VISION COMMANDER - LIVE DASHBOARD{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
        print(f"{Colors.CYAN}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Bots: {len(self.bot_visions)} | Updates: {len(self.command_history)}{Colors.END}\n")
        
        # Bot Status Grid
        self._display_bot_status_grid()
        
        # World Map Overview
        self._display_world_overview()
        
        # Recent Commands
        self._display_recent_commands()
        
        # Live Command Input
        self._display_command_input()
    
    def _display_bot_status_grid(self):
        """Display bot status in a grid format"""
        print(f"{Colors.BOLD}{Colors.BLUE}📊 BOT STATUS GRID{Colors.END}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.END}")
        
        # Header row
        print(f"{Colors.BOLD}{'Bot':<8} {'Position':<20} {'State':<12} {'Health':<8} {'Food':<8} {'Blocks':<8} {'Entities':<8}{Colors.END}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.END}")
        
        # Bot rows
        for bot_name, vision in self.bot_visions.items():
            pos_str = f"{vision.position[0]:.0f},{vision.position[1]:.0f},{vision.position[2]:.0f}"
            
            # Color coding for health
            health_color = Colors.GREEN if vision.health > 15 else Colors.YELLOW if vision.health > 10 else Colors.RED
            food_color = Colors.GREEN if vision.food > 15 else Colors.YELLOW if vision.food > 10 else Colors.RED
            
            print(f"{bot_name:<8} {pos_str:<20} {vision.state:<12} "
                  f"{health_color}{vision.health:<8.1f}{Colors.END} "
                  f"{food_color}{vision.food:<8.1f}{Colors.END} "
                  f"{len(vision.nearby_blocks):<8} {len(vision.nearby_entities):<8}")
        
        print()
    
    def _display_world_overview(self):
        """Display world overview"""
        print(f"{Colors.BOLD}{Colors.GREEN}🌍 WORLD OVERVIEW{Colors.END}")
        print(f"{Colors.GREEN}{'-'*40}{Colors.END}")
        
        # Block types found
        all_block_types = set()
        for blocks in self.world_map.blocks.values():
            all_block_types.update(blocks)
        
        print(f"Blocks Found: {', '.join(sorted(all_block_types))}")
        
        # Entity types found
        all_entity_types = set()
        for entities in self.world_map.entities.values():
            all_entity_types.update(entities)
        
        print(f"Entities Found: {', '.join(sorted(all_entity_types))}")
        print(f"Total Chunks: {len(self.world_map.blocks)}")
        print()
    
    def _display_recent_commands(self):
        """Display recent commands"""
        print(f"{Colors.BOLD}{Colors.YELLOW}📝 RECENT COMMANDS{Colors.END}")
        print(f"{Colors.YELLOW}{'-'*40}{Colors.END}")
        
        recent_commands = self.command_history[-5:] if self.command_history else []
        
        for cmd in recent_commands:
            timestamp = cmd["timestamp"].strftime("%H:%M:%S")
            status_color = Colors.GREEN if cmd["status"] == "completed" else Colors.RED if cmd["status"] == "error" else Colors.YELLOW
            
            print(f"{timestamp} | {status_color}{cmd['status']:<10}{Colors.END} | {cmd['command'][:50]}")
        
        print()
    
    def _display_command_input(self):
        """Display command input section"""
        print(f"{Colors.BOLD}{Colors.CYAN}💬 LIVE COMMAND INPUT{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print("Type commands here (or press Enter to continue monitoring):")
        
        try:
            command = input(f"{Colors.GREEN}🤖 Command > {Colors.END}")
            if command.strip():
                result = self.process_live_command(command)
                if result["success"]:
                    print(f"{Colors.GREEN}✅ Command executed successfully!{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Command failed: {result['error']}{Colors.END}")
                
                input("Press Enter to continue...")
        except EOFError:
            pass
    
    def export_vision_data(self, filename: str = None) -> str:
        """Export all vision data to JSON"""
        if filename is None:
            filename = f"bot_vision_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "bot_visions": {name: asdict(vision) for name, vision in self.bot_visions.items()},
            "world_map": asdict(self.world_map),
            "command_history": self.command_history,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Vision data exported to: {filename}")
        return filename

def main():
    """Main function to run the bot vision commander"""
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 Starting Bot Vision Commander...{Colors.END}")
    
    commander = BotVisionCommander()
    
    try:
        # Start live monitoring
        commander.start_live_monitoring()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Shutting down...{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
    finally:
        # Export data before shutting down
        try:
            commander.export_vision_data()
        except:
            pass
        print(f"{Colors.GREEN}✅ Bot Vision Commander stopped.{Colors.END}")

if __name__ == "__main__":
    main()