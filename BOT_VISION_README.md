# 👁️ Bot Vision Commander - See What Your Bots See!

## 🎯 What This System Does

The **Bot Vision Commander** gives you a **real-time view** of what ALL your Minecraft bots can see, plus the ability to give **live commands** to your bot army! It's like having a command center dashboard where you can:

- **See through your bots' eyes** - View what each bot sees in real-time
- **Monitor all bot status** - Health, food, position, inventory, nearby blocks/entities
- **Give live commands** - Type commands and see them executed immediately
- **Track world exploration** - See what resources and areas your bots have discovered
- **Coordinate bot teams** - Manage multiple bots simultaneously

## 🚀 Quick Start

### Option 1: Terminal Interface (Recommended for testing)
```bash
# Run the terminal-based vision commander
python bot_vision_commander.py
```

### Option 2: Web Dashboard (Best for visual monitoring)
```bash
# Start the web-based dashboard
python bot_vision_web.py
```
Then open your browser to: `http://localhost:8080`

## 🖥️ What You'll See

### Terminal Dashboard
```
🤖 BOT VISION COMMANDER - LIVE DASHBOARD
================================================================================
Time: 2024-01-15 14:30:25 | Bots: 3 | Updates: 12

📊 BOT STATUS GRID
--------------------------------------------------------------------------------
Bot     Position            State        Health   Food     Blocks  Entities
--------------------------------------------------------------------------------
Bot1    100,64,200         mining       18.0     18.0     45      3
Bot2    150,64,250         building     19.0     20.0     38      1
Bot3    200,64,300         exploring    18.0     17.0     52      2

🌍 WORLD OVERVIEW
----------------------------------------
Blocks Found: dirt, grass, stone, tree
Entities Found: cow, pig, zombie, villager
Total Chunks: 15

📝 RECENT COMMANDS
----------------------------------------
14:29:15 | completed    | Bot1, mine some iron ore
14:28:30 | completed    | All bots, collect wood
14:27:45 | completed    | Bot2, build a house

💬 LIVE COMMAND INPUT
----------------------------------------
Type commands here (or press Enter to continue monitoring):
🤖 Command > 
```

### Web Dashboard
- **Beautiful visual interface** with real-time updates
- **Interactive bot cards** showing health bars and status
- **World map visualization** of discovered areas
- **Live command input** with instant feedback
- **Command history** with status tracking
- **Mobile-responsive** design

## 🎮 Live Commands You Can Use

### Basic Commands
```
"Bot1, mine some iron ore"           # Mine specific resources
"All bots, collect wood"              # All bots gather wood
"Bot2, go to 100 64 200"             # Move bot to coordinates
"Show me the status of all bots"      # Get system overview
```

### Advanced Commands
```
"Bot1 and Bot2, build a house at 150 64 250"    # Team building
"Bot3, explore the area around 200 64 300"       # Exploration
"All bots, form a defensive line"                # Team formation
"Bot1, emergency retreat - low health"          # Emergency response
```

### Command Examples
```
# Mining operations
"Bot1, mine diamond ore"
"All bots, mine iron and coal"
"Bot2, clear area around 100 64 200"

# Building projects
"Bot3, build a 5x5 house"
"Bot1 and Bot2, construct a bridge"
"All bots, build a wall from 100 64 200 to 200 64 200"

# Movement and exploration
"Bot1, scout north for 100 blocks"
"Bot2, follow Bot1 at distance 5"
"Bot3, return to base immediately"

# Resource management
"All bots, deposit items in chest"
"Bot1, craft stone pickaxes"
"Bot2, plant wheat seeds"
```

## 🔍 What Each Bot Can See

### Bot Vision Data
Each bot provides real-time information about:

- **Position & Movement**: Current coordinates and where they're looking
- **Nearby Blocks**: All blocks within 16-block view distance
- **Nearby Entities**: Mobs, animals, and other entities nearby
- **Inventory Status**: What items they're carrying
- **Health & Food**: Current survival status
- **Activity State**: What they're currently doing

### World Discovery
The system automatically builds a world map showing:
- **Block Types Found**: stone, dirt, grass, trees, ores, etc.
- **Entity Types Found**: hostile mobs, passive animals, villagers
- **Explored Areas**: Chunks that bots have visited
- **Resource Locations**: Where valuable materials were found

## 🛠️ How It Works

### 1. Bot Vision Collection
- Each bot continuously reports what they see
- System processes and organizes the data
- Real-time updates every 1-2 seconds

### 2. Command Processing
- Your commands are analyzed by the bot brain
- System determines intent and generates actions
- Commands are executed and results tracked

### 3. Live Monitoring
- Dashboard updates automatically
- Bot movements and discoveries shown in real-time
- Health and status changes highlighted

### 4. Data Export
- All vision data can be exported to JSON
- Command history preserved
- World map data saved for analysis

## 📱 Interface Options

### Terminal Interface (`bot_vision_commander.py`)
- **Pros**: Lightweight, works anywhere, real-time updates
- **Best for**: Server environments, quick monitoring, automation

### Web Interface (`bot_vision_web.py`)
- **Pros**: Beautiful visuals, mobile-friendly, easy to use
- **Best for**: Desktop monitoring, team collaboration, presentations

## 🔧 Configuration

### Customizing Bot Vision
```python
# In bot_vision_commander.py
self.view_distance = 16        # How far bots can see
self.update_interval = 1.0     # Update frequency in seconds
```

### Adding New Bot Types
```python
# Add new bot capabilities
sample_bots = [
    {
        "name": "Bot4",
        "position": (250, 64, 350),
        "state": "farming",
        "health": 20.0,
        "food": 20.0
    }
]
```

### Custom Commands
```python
# Add new command types in _execute_command method
elif intent == "farming":
    return self._execute_farming_command(entities)
```

## 🚨 Emergency Features

### Automatic Health Monitoring
- **Low Health Alerts**: Bots automatically flagged when health < 10
- **Food Warnings**: Warnings when food levels are low
- **Critical Status**: Visual indicators for dangerous situations

### Emergency Commands
```
"Bot1, emergency retreat"           # Immediate safety response
"All bots, defensive formation"      # Group protection
"Bot2, heal immediately"            # Priority healing
```

## 📊 Data Export & Analysis

### Export Options
```bash
# Export all vision data
python bot_vision_commander.py
# Press 'export' command to save data

# Data includes:
- Bot positions and status
- World map discoveries
- Command history
- Resource locations
```

### JSON Output Format
```json
{
  "bot_visions": {
    "Bot1": {
      "position": [100, 64, 200],
      "nearby_blocks": [...],
      "health": 18.0,
      "state": "mining"
    }
  },
  "world_map": {
    "blocks": {...},
    "entities": {...}
  },
  "command_history": [...]
}
```

## 🔌 Integration with Your Bot System

### Node.js Bot Connection
The vision system integrates with your existing Node.js bots:
1. **Status Monitoring**: Tracks bot health and position
2. **Command Execution**: Sends commands to your bot system
3. **Data Synchronization**: Keeps vision data current
4. **Task Coordination**: Manages complex bot operations

### Real Bot Integration
To connect with real Minecraft bots:
1. Modify the `_update_bot_vision` method
2. Connect to your bot's data stream
3. Replace sample data with real bot information
4. Add communication protocols (MQTT, WebSocket, etc.)

## 🎯 Use Cases

### Resource Management
- **Monitor mining operations** across multiple bots
- **Track resource discovery** in real-time
- **Coordinate resource gathering** efficiently

### Construction Projects
- **Oversee building progress** from command center
- **Coordinate multiple builders** on large projects
- **Monitor material requirements** and supply

### Exploration & Mapping
- **Track exploration progress** across the world
- **Discover new areas** through bot vision
- **Map resource locations** automatically

### Team Coordination
- **Manage bot formations** and movements
- **Coordinate complex operations** between bots
- **Monitor team health** and status

## 🐛 Troubleshooting

### Common Issues
1. **No bot data showing**: Check if sample bots are initialized
2. **Commands not working**: Ensure bot brain is properly loaded
3. **Web interface not loading**: Check if port 8080 is available
4. **Performance issues**: Reduce update frequency or bot count

### Debug Mode
```python
# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Check bot vision data
print(commander.get_bot_vision_summary())
```

### Performance Tips
- Reduce `view_distance` for better performance
- Increase `update_interval` for less frequent updates
- Limit the number of bots being monitored
- Use terminal interface for high-performance needs

## 🚀 Advanced Features

### Custom Bot Behaviors
```python
# Add specialized bot types
class MiningBot(BotVision):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.mining_efficiency = 1.5
        self.ore_detection_range = 20

class BuildingBot(BotVision):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.building_speed = 2.0
        self.blueprint_memory = []
```

### AI-Powered Decisions
```python
# Integrate with AI models for intelligent decisions
def analyze_bot_behavior(self, bot_data):
    # Use AI to predict optimal bot actions
    # Analyze patterns in bot behavior
    # Generate intelligent recommendations
    pass
```

### Multi-Server Support
```python
# Monitor bots across multiple Minecraft servers
servers = {
    "survival": "localhost:25565",
    "creative": "localhost:25566",
    "minigames": "localhost:25567"
}
```

## 🤝 Contributing

### Adding New Features
1. **New Command Types**: Extend the command execution system
2. **Enhanced Visualization**: Improve the dashboard displays
3. **Bot Intelligence**: Add smarter bot decision-making
4. **Integration Protocols**: Support new communication methods

### Code Structure
```
bot_vision_commander.py      # Main terminal interface
bot_vision_web.py           # Web dashboard interface
bot_brain.py                # Intelligent command processing
BOT_VISION_README.md        # This documentation
```

## 📄 License

This bot vision system is designed to enhance your Minecraft bot operations. Feel free to modify and extend it for your specific needs.

## 🆘 Support

### Getting Help
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with simple commands first
4. Ensure Python 3.7+ compatibility

### Example Workflow
1. **Start the system**: `python bot_vision_commander.py`
2. **Monitor bots**: Watch the live dashboard
3. **Give commands**: Type natural language commands
4. **Track progress**: Monitor command execution
5. **Export data**: Save vision data for analysis

---

**Now you can see what your bots see and command them like a true bot general! 🤖👁️⚡**