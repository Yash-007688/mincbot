#!/usr/bin/env python3
"""
Bot Brain - Intelligent Task Analysis and Management System
This module serves as the central intelligence for the Minecraft bot system,
providing task analysis, work management, and intelligent prompt responses.
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_brain.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    IDLE = 5

class BotState(Enum):
    IDLE = "idle"
    WORKING = "working"
    GATHERING = "gathering"
    BUILDING = "building"
    EXPLORING = "exploring"
    FIGHTING = "fighting"
    HEALING = "healing"
    SLEEPING = "sleeping"
    CRAFTING = "crafting"
    FOLLOWING = "following"

@dataclass
class Task:
    id: str
    type: str
    description: str
    priority: TaskPriority
    target_bot: str
    parameters: Dict[str, Any]
    created_at: datetime
    deadline: Optional[datetime]
    status: str = "pending"
    progress: float = 0.0
    assigned_bots: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.assigned_bots is None:
            self.assigned_bots = []
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class BotInfo:
    name: str
    state: BotState
    health: float
    food: float
    inventory: Dict[str, int]
    position: Tuple[float, float, float]
    skills: List[str]
    current_task: Optional[str]
    team: List[str]
    last_activity: datetime

class BotBrain:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.bots: Dict[str, BotInfo] = {}
        self.teams: Dict[str, List[str]] = {}
        self.task_counter = 0
        self.work_patterns = {}
        self.resource_priorities = {}
        self.emergency_responses = {}
        self.conversation_context = {}
        
        # Initialize default configurations
        self._initialize_defaults()
        
    def _initialize_defaults(self):
        """Initialize default bot brain configurations"""
        self.resource_priorities = {
            "critical": ["food", "health_potion", "diamond_pickaxe"],
            "high": ["iron_ingot", "coal", "wood"],
            "medium": ["stone", "dirt", "sand"],
            "low": ["decorative_blocks", "flowers"]
        }
        
        self.emergency_responses = {
            "low_health": "Prioritize healing and retreat",
            "low_food": "Find and eat food immediately",
            "hostile_mob": "Engage or retreat based on health",
            "falling": "Use water bucket or elytra if available",
            "drowning": "Swim to surface or break blocks"
        }
        
        self.work_patterns = {
            "mining": ["find_vein", "clear_area", "extract_resources", "return_to_base"],
            "building": ["plan_structure", "gather_materials", "construct_foundation", "build_walls", "add_details"],
            "farming": ["plant_seeds", "water_crops", "harvest_mature", "replant"],
            "exploration": ["scout_area", "map_terrain", "identify_resources", "mark_landmarks"]
        }

    def analyze_prompt(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze incoming prompts and determine appropriate responses and actions
        """
        logger.info(f"Analyzing prompt: {prompt}")
        
        # Extract intent and entities
        intent = self._extract_intent(prompt)
        entities = self._extract_entities(prompt)
        urgency = self._assess_urgency(prompt)
        
        # Generate response and actions
        response = self._generate_response(intent, entities, context)
        actions = self._generate_actions(intent, entities, urgency)
        
        return {
            "intent": intent,
            "entities": entities,
            "urgency": urgency,
            "response": response,
            "actions": actions,
            "confidence": self._calculate_confidence(intent, entities)
        }

    def _extract_intent(self, prompt: str) -> str:
        """Extract the main intent from a prompt"""
        prompt_lower = prompt.lower()
        
        # Mining related intents
        if any(word in prompt_lower for word in ["mine", "dig", "extract", "ore"]):
            return "mining"
        elif any(word in prompt_lower for word in ["build", "construct", "create", "make"]):
            return "building"
        elif any(word in prompt_lower for word in ["collect", "gather", "harvest", "find"]):
            return "gathering"
        elif any(word in prompt_lower for word in ["explore", "scout", "search", "map"]):
            return "exploration"
        elif any(word in prompt_lower for word in ["fight", "attack", "defend", "protect"]):
            return "combat"
        elif any(word in prompt_lower for word in ["craft", "make", "create_item"]):
            return "crafting"
        elif any(word in prompt_lower for word in ["move", "go", "travel", "teleport"]):
            return "movement"
        elif any(word in prompt_lower for word in ["team", "group", "coordinate", "together"]):
            return "team_coordination"
        elif any(word in prompt_lower for word in ["status", "report", "info", "check"]):
            return "status_request"
        else:
            return "general_query"

    def _extract_entities(self, prompt: str) -> Dict[str, Any]:
        """Extract relevant entities from the prompt"""
        entities = {
            "bot_names": [],
            "locations": [],
            "items": [],
            "quantities": [],
            "time_constraints": []
        }
        
        # Extract bot names (Bot1, Bot2, etc.)
        bot_pattern = r'\bBot\d+\b'
        entities["bot_names"] = re.findall(bot_pattern, prompt)
        
        # Extract coordinates
        coord_pattern = r'(-?\d+)\s+(-?\d+)\s+(-?\d+)'
        coords = re.findall(coord_pattern, prompt)
        if coords:
            entities["locations"] = [{"x": int(x), "y": int(y), "z": int(z)} for x, y, z in coords]
        
        # Extract items
        item_pattern = r'\b(wood|stone|iron|diamond|coal|food|water|sword|pickaxe|axe)\b'
        entities["items"] = re.findall(item_pattern, prompt.lower())
        
        # Extract quantities
        quantity_pattern = r'\b(\d+)\s+(blocks?|items?|pieces?)\b'
        entities["quantities"] = re.findall(quantity_pattern, prompt.lower())
        
        return entities

    def _assess_urgency(self, prompt: str) -> str:
        """Assess the urgency level of a prompt"""
        urgent_words = ["emergency", "urgent", "immediately", "now", "quick", "fast", "hurry"]
        if any(word in prompt.lower() for word in urgent_words):
            return "high"
        elif any(word in prompt.lower() for word in ["soon", "later", "when possible"]):
            return "low"
        else:
            return "medium"

    def _generate_response(self, intent: str, entities: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate an appropriate response based on intent and entities"""
        responses = {
            "mining": "I'll coordinate the bots to mine the requested resources efficiently.",
            "building": "I'll analyze the building requirements and assign appropriate bots to the task.",
            "gathering": "I'll send bots to collect the specified items and materials.",
            "exploration": "I'll organize an exploration team to scout the requested area.",
            "combat": "I'll assess the threat level and coordinate defensive or offensive actions.",
            "crafting": "I'll ensure the necessary materials are gathered and crafting begins.",
            "movement": "I'll coordinate bot movement to the specified locations.",
            "team_coordination": "I'll organize the bots into effective teams for coordinated action.",
            "status_request": "I'll provide a comprehensive status report of all bots and current tasks.",
            "general_query": "I'm here to help coordinate the bot operations. What would you like me to do?"
        }
        
        base_response = responses.get(intent, responses["general_query"])
        
        # Customize response based on entities
        if entities["bot_names"]:
            bot_list = ", ".join(entities["bot_names"])
            base_response += f" I'll specifically involve {bot_list} in this task."
        
        if entities["locations"]:
            base_response += " I'll coordinate movement to the specified coordinates."
        
        return base_response

    def _generate_actions(self, intent: str, entities: Dict[str, Any], urgency: str) -> List[Dict[str, Any]]:
        """Generate specific actions based on the prompt analysis"""
        actions = []
        
        if intent == "mining":
            actions.extend(self._generate_mining_actions(entities))
        elif intent == "building":
            actions.extend(self._generate_building_actions(entities))
        elif intent == "gathering":
            actions.extend(self._generate_gathering_actions(entities))
        elif intent == "exploration":
            actions.extend(self._generate_exploration_actions(entities))
        elif intent == "movement":
            actions.extend(self._generate_movement_actions(entities))
        
        # Add urgency-based actions
        if urgency == "high":
            actions.append({
                "type": "prioritize_task",
                "description": "Mark task as high priority",
                "parameters": {"priority": "high"}
            })
        
        return actions

    def _generate_mining_actions(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mining-specific actions"""
        actions = []
        
        if entities["items"]:
            for item in entities["items"]:
                actions.append({
                    "type": "mine_resource",
                    "description": f"Mine {item}",
                    "parameters": {"resource": item, "quantity": 1}
                })
        
        actions.extend([
            {
                "type": "coordinate_bots",
                "description": "Coordinate multiple bots for efficient mining",
                "parameters": {"strategy": "grid_pattern"}
            },
            {
                "type": "return_to_base",
                "description": "Return collected resources to base",
                "parameters": {"auto_return": True}
            }
        ])
        
        return actions

    def _generate_building_actions(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate building-specific actions"""
        actions = []
        
        actions.extend([
            {
                "type": "plan_structure",
                "description": "Create building plan and material requirements",
                "parameters": {"auto_plan": True}
            },
            {
                "type": "gather_materials",
                "description": "Collect necessary building materials",
                "parameters": {"priority": "high"}
            },
            {
                "type": "assign_builders",
                "description": "Assign specialized bots to construction",
                "parameters": {"team_size": 3}
            }
        ])
        
        return actions

    def _generate_gathering_actions(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate gathering-specific actions"""
        actions = []
        
        if entities["items"]:
            for item in entities["items"]:
                actions.append({
                    "type": "collect_item",
                    "description": f"Collect {item}",
                    "parameters": {"item": item, "search_radius": 50}
                })
        
        actions.append({
            "type": "organize_inventory",
            "description": "Organize collected items efficiently",
            "parameters": {"auto_sort": True}
        })
        
        return actions

    def _generate_exploration_actions(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate exploration-specific actions"""
        actions = []
        
        actions.extend([
            {
                "type": "scout_area",
                "description": "Send scouts to explore the area",
                "parameters": {"scout_count": 2, "exploration_radius": 100}
            },
            {
                "type": "map_terrain",
                "description": "Create map of discovered areas",
                "parameters": {"auto_mapping": True}
            },
            {
                "type": "mark_landmarks",
                "description": "Mark important locations and resources",
                "parameters": {"landmark_types": ["caves", "villages", "temples"]}
            }
        ])
        
        return actions

    def _generate_movement_actions(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate movement-specific actions"""
        actions = []
        
        if entities["locations"]:
            for location in entities["locations"]:
                actions.append({
                    "type": "move_to_coordinates",
                    "description": f"Move to coordinates {location}",
                    "parameters": {"x": location["x"], "y": location["y"], "z": location["z"]}
                })
        
        if entities["bot_names"]:
            actions.append({
                "type": "coordinate_movement",
                "description": "Coordinate movement of specified bots",
                "parameters": {"formation": "line", "maintain_distance": 5}
            })
        
        return actions

    def _calculate_confidence(self, intent: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence level of the analysis"""
        base_confidence = 0.7
        
        # Boost confidence based on clear entities
        if entities["bot_names"]:
            base_confidence += 0.1
        if entities["locations"]:
            base_confidence += 0.1
        if entities["items"]:
            base_confidence += 0.1
        
        # Boost confidence for specific intents
        specific_intents = ["mining", "building", "gathering", "movement"]
        if intent in specific_intents:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)

    def create_task(self, task_type: str, description: str, target_bot: str, 
                    parameters: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Create a new task and add it to the task queue"""
        task_id = f"task_{self.task_counter:04d}"
        self.task_counter += 1
        
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            priority=priority,
            target_bot=target_bot,
            parameters=parameters,
            created_at=datetime.now(),
            deadline=None
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {description}")
        
        return task_id

    def assign_task(self, task_id: str, bot_name: str) -> bool:
        """Assign a task to a specific bot"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        if bot_name not in self.bots:
            logger.error(f"Bot {bot_name} not found")
            return False
        
        task = self.tasks[task_id]
        if bot_name not in task.assigned_bots:
            task.assigned_bots.append(bot_name)
        
        self.bots[bot_name].current_task = task_id
        logger.info(f"Assigned task {task_id} to {bot_name}")
        
        return True

    def update_bot_status(self, bot_name: str, status_data: Dict[str, Any]):
        """Update the status of a specific bot"""
        if bot_name not in self.bots:
            # Create new bot if it doesn't exist
            self.bots[bot_name] = BotInfo(
                name=bot_name,
                state=BotState.IDLE,
                health=20.0,
                food=20.0,
                inventory={},
                position=(0.0, 64.0, 0.0),
                skills=[],
                current_task=None,
                team=[],
                last_activity=datetime.now()
            )
        
        bot = self.bots[bot_name]
        
        # Update bot properties
        for key, value in status_data.items():
            if hasattr(bot, key):
                setattr(bot, key, value)
        
        bot.last_activity = datetime.now()
        logger.debug(f"Updated status for {bot_name}")

    def get_bot_recommendations(self, bot_name: str) -> List[Dict[str, Any]]:
        """Get intelligent recommendations for a specific bot"""
        if bot_name not in self.bots:
            return []
        
        bot = self.bots[bot_name]
        recommendations = []
        
        # Health-based recommendations
        if bot.health < 10:
            recommendations.append({
                "type": "health_emergency",
                "priority": "critical",
                "action": "Find healing items or retreat to safe area",
                "reason": f"Bot health is critically low: {bot.health}"
            })
        
        # Food-based recommendations
        if bot.food < 15:
            recommendations.append({
                "type": "food_priority",
                "priority": "high",
                "action": "Search for and consume food",
                "reason": f"Bot food level is low: {bot.food}"
            })
        
        # Task-based recommendations
        if not bot.current_task:
            recommendations.append({
                "type": "idle_activity",
                "priority": "medium",
                "action": "Assign resource gathering or exploration task",
                "reason": "Bot is currently idle"
            })
        
        # Inventory-based recommendations
        if len(bot.inventory) < 5:
            recommendations.append({
                "type": "inventory_management",
                "priority": "low",
                "action": "Gather basic resources for future tasks",
                "reason": "Inventory is relatively empty"
            })
        
        return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        total_bots = len(self.bots)
        active_tasks = len([t for t in self.tasks.values() if t.status == "active"])
        idle_bots = len([b for b in self.bots.values() if b.state == BotState.IDLE])
        
        # Calculate resource availability
        total_resources = {}
        for bot in self.bots.values():
            for item, count in bot.inventory.items():
                total_resources[item] = total_resources.get(item, 0) + count
        
        return {
            "total_bots": total_bots,
            "active_tasks": active_tasks,
            "idle_bots": idle_bots,
            "total_resources": total_resources,
            "system_health": "good" if total_bots > 0 and idle_bots < total_bots else "warning",
            "last_updated": datetime.now().isoformat()
        }

    def optimize_work_distribution(self) -> List[Dict[str, Any]]:
        """Optimize work distribution among available bots"""
        optimizations = []
        
        # Find idle bots
        idle_bots = [name for name, bot in self.bots.items() if bot.state == BotState.IDLE]
        
        # Find pending tasks
        pending_tasks = [task for task in self.tasks.values() if task.status == "pending"]
        
        # Assign tasks to idle bots
        for i, task in enumerate(pending_tasks):
            if i < len(idle_bots):
                bot_name = idle_bots[i]
                self.assign_task(task.id, bot_name)
                optimizations.append({
                    "type": "task_assignment",
                    "bot": bot_name,
                    "task": task.id,
                    "description": f"Assigned {task.description} to {bot_name}"
                })
        
        # Balance team workloads
        for team_name, team_members in self.teams.items():
            if len(team_members) > 1:
                workloads = [len([t for t in self.tasks.values() if bot in t.assigned_bots]) 
                           for bot in team_members]
                
                if max(workloads) - min(workloads) > 2:
                    optimizations.append({
                        "type": "team_balance",
                        "team": team_name,
                        "action": "Redistribute tasks to balance workload",
                        "current_workloads": dict(zip(team_members, workloads))
                    })
        
        return optimizations

    def handle_emergency(self, emergency_type: str, bot_name: str, details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle emergency situations"""
        emergency_responses = []
        
        if emergency_type == "low_health":
            emergency_responses.extend([
                {
                    "type": "emergency_healing",
                    "bot": bot_name,
                    "action": "Immediate retreat to safe area",
                    "priority": "critical"
                },
                {
                    "type": "resource_request",
                    "bot": bot_name,
                    "action": "Request healing items from team",
                    "priority": "high"
                }
            ])
        
        elif emergency_type == "hostile_mob":
            emergency_responses.extend([
                {
                    "type": "combat_assessment",
                    "bot": bot_name,
                    "action": "Assess threat level and determine response",
                    "priority": "high"
                },
                {
                    "type": "team_support",
                    "bot": bot_name,
                    "action": "Request backup from nearby team members",
                    "priority": "medium"
                }
            ])
        
        logger.warning(f"Emergency handled for {bot_name}: {emergency_type}")
        return emergency_responses

    def export_to_json(self, filename: str = None) -> str:
        """Export bot brain state to JSON"""
        if filename is None:
            filename = f"bot_brain_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "bots": {name: asdict(bot) for name, bot in self.bots.items()},
            "tasks": {tid: asdict(task) for tid, task in self.tasks.items()},
            "teams": self.teams,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Bot brain state exported to {filename}")
        return filename

    def load_from_json(self, filename: str) -> bool:
        """Load bot brain state from JSON"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Reconstruct bots
            for name, bot_data in data.get("bots", {}).items():
                # Convert string back to BotState enum
                if "state" in bot_data:
                    bot_data["state"] = BotState(bot_data["state"])
                self.bots[name] = BotInfo(**bot_data)
            
            # Reconstruct tasks
            for tid, task_data in data.get("tasks", {}).items():
                # Convert string back to TaskPriority enum
                if "priority" in task_data:
                    task_data["priority"] = TaskPriority(task_data["priority"])
                # Convert string back to datetime
                if "created_at" in task_data:
                    task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
                self.tasks[tid] = Task(**task_data)
            
            self.teams = data.get("teams", {})
            logger.info(f"Bot brain state loaded from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load bot brain state: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Create bot brain instance
    brain = BotBrain()
    
    # Example: Update bot status
    brain.update_bot_status("Bot1", {
        "health": 18.0,
        "food": 15.0,
        "position": (100, 64, 200),
        "state": BotState.IDLE
    })
    
    brain.update_bot_status("Bot2", {
        "health": 20.0,
        "food": 20.0,
        "position": (150, 64, 250),
        "state": BotState.WORKING
    })
    
    # Example: Analyze a prompt
    prompt = "Bot1, please mine some iron ore and collect 10 pieces"
    analysis = brain.analyze_prompt(prompt)
    
    print("Prompt Analysis:")
    print(json.dumps(analysis, indent=2, default=str))
    
    # Example: Create and assign a task
    task_id = brain.create_task(
        task_type="mining",
        description="Mine iron ore and collect 10 pieces",
        target_bot="Bot1",
        parameters={"resource": "iron_ore", "quantity": 10},
        priority=TaskPriority.HIGH
    )
    
    brain.assign_task(task_id, "Bot1")
    
    # Example: Get recommendations
    recommendations = brain.get_bot_recommendations("Bot1")
    print("\nBot1 Recommendations:")
    for rec in recommendations:
        print(f"- {rec['action']} (Priority: {rec['priority']})")
    
    # Example: Get system status
    status = brain.get_system_status()
    print("\nSystem Status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Example: Export state
    brain.export_to_json("example_bot_brain_state.json")
    
    print("\nBot brain system initialized and tested successfully!")