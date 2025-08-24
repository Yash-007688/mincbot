import json
from typing import Dict, Any

class MovementHandler:
    def __init__(self):
        self.commands = self._load_commands()

    def _load_commands(self) -> Dict[str, Any]:
        with open('ai_commands/commands/movement/movement_commands.json', 'r') as f:
            return json.load(f)

    def handle_move_command(self, bot_name: str, x: float, y: float, z: float) -> str:
        """Handle move command and return formatted command string"""
        return f"{bot_name}:tp {x} {y} {z}"

    def handle_follow_command(self, bot_name: str, target_bot: str) -> str:
        """Handle follow command and return formatted command string"""
        return f"{bot_name}:follow {target_bot}"

    def handle_stop_command(self, bot_name: str) -> str:
        """Handle stop command and return formatted command string"""
        return f"{bot_name}:unfollow"

    def process_command(self, command_type: str, *args) -> str:
        """Process movement command and return formatted command string"""
        if command_type not in self.commands["commands"]:
            raise ValueError(f"Unknown command type: {command_type}")
        
        handler_name = f"handle_{command_type}_command"
        handler = getattr(self, handler_name)
        return handler(*args) 