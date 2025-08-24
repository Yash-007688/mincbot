import json
from typing import Dict, Any

class ActionHandler:
    def __init__(self):
        self.commands = self._load_commands()

    def _load_commands(self) -> Dict[str, Any]:
        with open('ai_commands/commands/actions/action_commands.json', 'r') as f:
            return json.load(f)

    def handle_mine_command(self, bot_name: str, block_type: str) -> str:
        """Handle mine command and return formatted command string"""
        return f"{bot_name}:mine {block_type}"

    def handle_build_command(self, bot_name: str, structure_type: str) -> str:
        """Handle build command and return formatted command string"""
        return f"{bot_name}:build {structure_type}"

    def handle_collect_command(self, bot_name: str, item_type: str) -> str:
        """Handle collect command and return formatted command string"""
        return f"{bot_name}:collect {item_type}"

    def process_command(self, command_type: str, *args) -> str:
        """Process action command and return formatted command string"""
        if command_type not in self.commands["commands"]:
            raise ValueError(f"Unknown command type: {command_type}")
        
        handler_name = f"handle_{command_type}_command"
        handler = getattr(self, handler_name)
        return handler(*args) 