import discord
from discord.ext import commands
import json
import os
from typing import Dict, Any
from bot_ai import BotAI, BotProperties, BotState

class DiscordBotHandler:
    def __init__(self):
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.commands = self.load_commands()
        self.bots = {}  # Store bot instances
        self.setup_commands()
        self.initialize_bots()

    def initialize_bots(self):
        """Initialize bot instances for the four main bots"""
        bot_configs = [
            {"name": "Alpha", "camera_type": "main_camera", "ip": "192.168.1.101", "port": 8080},
            {"name": "Beta", "camera_type": "thermal_vision", "ip": "192.168.1.102", "port": 8081},
            {"name": "Gamma", "camera_type": "depth_sensor", "ip": "192.168.1.103", "port": 8082},
            {"name": "Delta", "camera_type": "object_detection", "ip": "192.168.1.104", "port": 8083}
        ]
        
        for config in bot_configs:
            bot_props = BotProperties(
                name=f"Bot {config['name']}",
                team_members=[f"Bot {c['name']}" for c in bot_configs if c['name'] != config['name']],
                camera_type=config['camera_type'],
                ip_address=config['ip'],
                port=config['port']
            )
            self.bots[config['name'].lower()] = BotAI(bot_props)

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
            print('Available commands:')
            for cmd_name in self.commands.keys():
                print(f'  !{cmd_name}')

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
                    response = f"Processing {cmd_name} command for {bot_name}"
                    await ctx.send(response)
                except Exception as e:
                    await ctx.send(f"Error processing command: {str(e)}")

        # Vision system commands
        @self.bot.command(name='vision')
        async def vision_command(ctx, bot_name: str, action: str, *args):
            """Vision system management commands"""
            bot_key = bot_name.lower().replace('bot', '').strip()
            if bot_key not in self.bots:
                await ctx.send(f"Bot {bot_name} not found. Available bots: Alpha, Beta, Gamma, Delta")
                return
            
            bot_ai = self.bots[bot_key]
            
            if action == "status":
                vision_data = bot_ai.get_vision_data()
                await ctx.send(f"Vision status for {bot_name}:\n```json\n{json.dumps(vision_data, indent=2)}\n```")
            
            elif action == "toggle":
                enabled = args[0].lower() == "on" if args else not bot_ai.bot.vision_enabled
                response = bot_ai.update_vision_status(enabled)
                await ctx.send(response)
            
            elif action == "analyze":
                vision_data = bot_ai.get_vision_data()
                await ctx.send(f"Vision analysis for {bot_name}:\n```json\n{json.dumps(vision_data, indent=2)}\n```")
            
            else:
                await ctx.send(f"Unknown vision action: {action}. Use: status, toggle, analyze")

        # Settings management commands
        @self.bot.command(name='settings')
        async def settings_command(ctx, action: str, *args):
            """Settings management commands"""
            if action == "server":
                if len(args) >= 3:
                    server_name, port, ip = args[0], int(args[1]), args[2]
                    # Update server config using first available bot
                    bot_ai = list(self.bots.values())[0]
                    response = bot_ai.update_server_config(server_name, port, ip)
                    await ctx.send(response)
                else:
                    await ctx.send("Usage: !settings server <name> <port> <ip>")
            
            elif action == "show":
                bot_ai = list(self.bots.values())[0]
                server_config = bot_ai.get_server_config()
                await ctx.send(f"Current server configuration:\n```json\n{json.dumps(server_config, indent=2)}\n```")
            
            else:
                await ctx.send(f"Unknown settings action: {action}. Use: server, show")

        # Bot management commands
        @self.bot.command(name='bot')
        async def bot_command(ctx, action: str, bot_name: str):
            """Bot management commands"""
            bot_key = bot_name.lower().replace('bot', '').strip()
            if bot_key not in self.bots:
                await ctx.send(f"Bot {bot_name} not found. Available bots: Alpha, Beta, Gamma, Delta")
                return
            
            bot_ai = self.bots[bot_key]
            
            if action == "ping":
                ping_data = bot_ai.ping_bot()
                await ctx.send(f"Ping result for {bot_name}:\n```json\n{json.dumps(ping_data, indent=2)}\n```")
            
            elif action == "restart":
                restart_data = bot_ai.restart_bot()
                await ctx.send(f"Restart result for {bot_name}:\n```json\n{json.dumps(restart_data, indent=2)}\n```")
            
            elif action == "status":
                status_data = bot_ai.get_status_summary()
                await ctx.send(f"Status for {bot_name}:\n```json\n{json.dumps(status_data, indent=2)}\n```")
            
            elif action == "config":
                if len(args) >= 2:
                    ip, port = args[0], int(args[1])
                    response = bot_ai.update_network_config(ip, port)
                    await ctx.send(response)
                else:
                    await ctx.send("Usage: !bot config <bot_name> <ip> <port>")
            
            else:
                await ctx.send(f"Unknown bot action: {action}. Use: ping, restart, status, config")

        # System information command
        @self.bot.command(name='system')
        async def system_command(ctx):
            """Get system information"""
            bot_ai = list(self.bots.values())[0]
            system_info = bot_ai.get_system_info()
            await ctx.send(f"System Information:\n```json\n{json.dumps(system_info, indent=2)}\n```")

        # Help command
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Show available commands"""
            help_text = """
**🤖 Minecraft Bot Hub - Discord Commands**

**Vision System:**
`!vision <bot_name> status` - Check bot vision status
`!vision <bot_name> toggle on/off` - Enable/disable vision
`!vision <bot_name> analyze` - Analyze vision data

**Settings Management:**
`!settings server <name> <port> <ip>` - Update server config
`!settings show` - Show current server configuration

**Bot Management:**
`!bot ping <bot_name>` - Ping a bot
`!bot restart <bot_name>` - Restart a bot
`!bot status <bot_name>` - Get bot status
`!bot config <bot_name> <ip> <port>` - Update bot network config

**System:**
`!system` - Get system information
`!help` - Show this help message

**Available Bots:** Alpha, Beta, Gamma, Delta
**Example:** `!vision alpha status`
            """
            await ctx.send(help_text)

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
