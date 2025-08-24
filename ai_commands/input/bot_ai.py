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
        self.load_memory()
        
        # Priority levels for different actions
        self.action_priorities = {
            BotState.HEALING: 1,
            BotState.ATTACKING: 2,
            BotState.DEFENDING: 2,
            BotState.SLEEPING: 3,
            BotState.FOLLOWING: 4,
            BotState.GATHERING_WOOD: 5,
            BotState.MINING: 5,
            BotState.FARMING: 5,
            BotState.CRAFTING: 6,
            BotState.BUILDING: 7,
            BotState.EXPLORING: 8,
            BotState.IDLE: 9
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
        except FileNotFoundError:
            self.save_memory()  # Create new memory file if none exists

    def save_memory(self):
        """Save bot's current state to JSON file"""
        memory = {
            'inventory': self.bot.inventory,
            'equipment': self.bot.equipment,
            'state': self.bot.state.value,
            'position': self.bot.position,
            'target_position': self.bot.target_position
        }
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=4)

    def update(self):
        """Main AI update loop"""
        # Update bot's state based on current conditions
        self.check_health()
        self.check_food()
        self.check_inventory()
        self.check_position()
        self.decide_action()
        self.save_memory()

    def check_health(self):
        """Check bot's health and decide if healing is needed"""
        if self.bot.health < 10:
            self.bot.state = BotState.HEALING
            self.chat("Health is low, need to heal!")
        elif self.bot.health < 15 and self.bot.state != BotState.ATTACKING:
            self.chat("Health is getting low, should find food or shelter")

    def check_food(self):
        """Check bot's food level and decide if eating is needed"""
        if self.bot.food < 10:
            self.chat("Very hungry, need to find food immediately!")
            self.prioritize_food()
        elif self.bot.food < 15:
            self.chat("Getting hungry, should find food soon")

    def check_inventory(self):
        """Check inventory and update memory"""
        essential_items = {
            'wood': 10,
            'stone': 5,
            'food': 5,
            'torch': 10,
            'bed': 1
        }
        
        for item, min_count in essential_items.items():
            current_count = self.bot.inventory.get(item, 0)
            if current_count < min_count:
                self.chat(f"Need to gather more {item} (have {current_count}, need {min_count})")

    def check_position(self):
        """Check bot's position and update target if needed"""
        if self.bot.target_position:
            distance = self.calculate_distance(self.bot.position, self.bot.target_position)
            if distance < 1.0:  # Reached target
                self.bot.target_position = None
                self.chat("Reached target position")

    def calculate_distance(self, pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Calculate distance between two positions"""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2) ** 0.5

    def decide_action(self):
        """Decide what action to take based on current state and priorities"""
        if self.bot.state == BotState.IDLE:
            # Choose action based on priorities and current needs
            possible_actions = self.get_possible_actions()
            if possible_actions:
                self.bot.state = min(possible_actions, key=lambda x: self.action_priorities[x])
                self.chat(f"Decided to {self.bot.state.value}")

    def get_possible_actions(self) -> List[BotState]:
        """Get list of possible actions based on current conditions"""
        actions = []
        
        # Check for immediate needs
        if self.bot.health < 15:
            actions.append(BotState.HEALING)
        if self.bot.food < 15:
            actions.append(BotState.FARMING)
        
        # Check for resource needs
        if self.bot.inventory.get('wood', 0) < 10:
            actions.append(BotState.GATHERING_WOOD)
        if self.bot.inventory.get('stone', 0) < 5:
            actions.append(BotState.MINING)
            
        # Add exploration if no immediate needs
        if not actions:
            actions.append(BotState.EXPLORING)
            
        return actions

    def prioritize_food(self):
        """Prioritize finding food when hungry"""
        self.bot.state = BotState.FARMING
        self.chat("Prioritizing food gathering")

    def chat(self, message: str):
        """Send a chat message with cooldown"""
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.bot.last_chat_time > self.bot.chat_cooldown:
            print(f"[{self.bot.name}] {message}")
            self.bot.last_chat_time = current_time

    def add_to_inventory(self, item: str, count: int = 1):
        """Add items to inventory"""
        self.bot.inventory[item] = self.bot.inventory.get(item, 0) + count
        self.chat(f"Added {count} {item} to inventory")
        self.save_memory()

    def remove_from_inventory(self, item: str, count: int = 1):
        """Remove items from inventory"""
        if item in self.bot.inventory:
            self.bot.inventory[item] = max(0, self.bot.inventory[item] - count)
            self.chat(f"Removed {count} {item} from inventory")
            self.save_memory()

    def set_target_position(self, position: Tuple[float, float, float]):
        """Set a target position for the bot to move to"""
        self.bot.target_position = position
        self.chat(f"Moving to position {position}")
        self.save_memory()

    def set_target_entity(self, entity: str):
        """Set a target entity for the bot to interact with"""
        self.bot.target_entity = entity
        self.chat(f"Targeting entity: {entity}")
        self.save_memory()

    def update_position(self, position: Tuple[float, float, float]):
        """Update bot's current position"""
        self.bot.position = position
        self.save_memory()
