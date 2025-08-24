import discord
from discord.ext import commands
import json
import os
from typing import Dict, Any

class DiscordBotHandler:
    def __init__(self):
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.commands = self.load_commands()
        self.setup_commands()

    def load_commands(self) -> Dict[str, Any]:
        """Load commands from action_commands.json"""
        try:
            with open('ai_commands/commands/actions/action_commands.json', 'r') as f:
                return json.load(f)['commands']
        except FileNotFoundError:
            print("Error: action_commands.json not found")
            return {}

    def setup_commands(self):
        """Set up Discord commands based on action_commands.json"""
        @self.bot.event
        async def on_ready():
            print(f'Bot is ready! Logged in as {self.bot.user}')

        # Create commands dynamically from action_commands.json
        for cmd_name, cmd_data in self.commands.items():
            @self.bot.command(name=cmd_name)
            async def command(ctx, bot_name: str, *args):
                # Get the actual command name from the context
                cmd_name = ctx.command.name
                cmd_data = self.commands[cmd_name]
                
                # Validate parameters
                if not self.validate_parameters(cmd_name, args):
                    await ctx.send(f"Invalid parameters. Format: {cmd_data['format']}")
                    return

                # Process the command
                try:
                    # Call the appropriate Python handler
                    handler_name = cmd_data['python_handler']
                    # Here you would call your actual handler function
                    response = f"Processing {cmd_name} command for {bot_name}"
                    await ctx.send(response)
                except Exception as e:
                    await ctx.send(f"Error processing command: {str(e)}")

    def validate_parameters(self, cmd_name: str, args: tuple) -> bool:
        """Validate command parameters against defined parameters in action_commands.json"""
        cmd_data = self.commands[cmd_name]
        required_params = len(cmd_data['parameters'])
        
        if len(args) < required_params:
            return False

        # Check if parameters are valid according to the defined values
        for i, (param_name, param_values) in enumerate(cmd_data['parameters'].items()):
            if param_values != "number" and args[i] not in param_values:
                return False
            elif param_values == "number" and not args[i].isdigit():
                return False

        return True

    def run(self, token: str):
        """Run the Discord bot"""
        self.bot.run(token)

# Example usage
if __name__ == "__main__":
    # Get Discord token from environment variable
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables")
        exit(1)

    # Create and run the bot
    handler = DiscordBotHandler()
    handler.run(DISCORD_TOKEN)
