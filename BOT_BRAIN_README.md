# 🤖 Bot Brain System - Intelligent Minecraft Bot Management

## Overview

The **Bot Brain System** is a Python-based intelligent management layer that acts as the central nervous system for your Minecraft bot army. It provides:

- **Intelligent Task Analysis**: Understands natural language commands and converts them to bot actions
- **Smart Work Distribution**: Optimizes task assignment across multiple bots
- **Health Monitoring**: Tracks bot status and provides recommendations
- **Emergency Response**: Handles critical situations automatically
- **Team Coordination**: Manages bot teams and formations

## 🚀 Quick Start

### 1. Test the Bot Brain
```bash
# Run the bot brain in test mode
python bot_brain.py
```

### 2. Run Interactive Mode
```bash
# Start the interactive bot brain interface
python bot_brain_integration.py
```

### 3. Use Natural Language Commands
```
🤖 Bot Brain > Bot1, mine some iron ore
🤖 Bot Brain > Bot2 and Bot3, build a house at 100 64 200
🤖 Bot Brain > All bots, collect wood
🤖 Bot Brain > Show me the status of all bots
```

## 🏗️ Architecture

```
User Input → Bot Brain → Task Analysis → Command Generation → Node.js Bots
                ↓
         Intelligent Decision Making
                ↓
         Task Management & Optimization
                ↓
         Health Monitoring & Recommendations
```

## 🔧 Core Components

### BotBrain Class
The main intelligence engine that:
- Analyzes user prompts and extracts intent
- Manages tasks and bot assignments
- Provides health monitoring and recommendations
- Handles emergency situations

### Task Management
- **Task Creation**: Generate structured tasks from natural language
- **Priority System**: CRITICAL, HIGH, MEDIUM, LOW, IDLE
- **Dependencies**: Chain tasks together for complex operations
- **Progress Tracking**: Monitor task completion status

### Bot Intelligence
- **State Management**: Track bot status (IDLE, WORKING, MINING, etc.)
- **Health Monitoring**: Monitor health, food, and inventory
- **Skill Assessment**: Track bot capabilities and specializations
- **Team Coordination**: Manage bot teams and formations

## 📋 Available Commands

### Natural Language Examples
```
"Bot1, mine some iron ore"
"Bot2 and Bot3, build a house at 100 64 200"
"All bots, collect wood"
"Bot1, go to coordinates 150 64 250"
"Show me the status of all bots"
"Emergency: Bot1 has low health"
```

### System Commands
```
help          - Show available commands
status        - Display bot system status
export        - Export bot brain state to JSON
optimize      - Optimize work distribution
quit          - Exit the system
```

## 🎯 Task Types

### Mining Tasks
- **Resource Mining**: Extract specific ores and materials
- **Area Clearing**: Clear large areas efficiently
- **Strategic Mining**: Focus on high-value resources

### Building Tasks
- **Structure Planning**: Create building plans automatically
- **Material Gathering**: Collect required building materials
- **Construction**: Coordinate multiple bots for building

### Exploration Tasks
- **Area Scouting**: Explore new territories
- **Resource Mapping**: Identify and mark valuable resources
- **Landmark Discovery**: Find villages, temples, and caves

### Movement Tasks
- **Coordinate Navigation**: Move bots to specific locations
- **Formation Management**: Maintain bot formations
- **Pathfinding**: Navigate around obstacles

## 🚨 Emergency Handling

The bot brain automatically handles:
- **Low Health**: Prioritize healing and retreat
- **Low Food**: Find and consume food immediately
- **Hostile Mobs**: Assess threat and coordinate response
- **Environmental Hazards**: Handle falling, drowning, etc.

## 📊 Monitoring & Analytics

### System Status
- Total bot count and active tasks
- Resource availability across all bots
- System health indicators
- Performance metrics

### Bot Recommendations
- Health-based suggestions
- Task optimization tips
- Resource management advice
- Team coordination recommendations

## 🔌 Integration with Node.js Bots

The bot brain integrates with your existing Node.js system through:

1. **Command Translation**: Converts Python decisions to Node.js commands
2. **Status Synchronization**: Keeps bot states synchronized
3. **Task Coordination**: Manages task execution across both systems
4. **Health Monitoring**: Tracks bot status from Node.js

## 📁 File Structure

```
├── bot_brain.py              # Core bot brain intelligence
├── bot_brain_integration.py  # Integration with Node.js system
├── requirements.txt          # Python dependencies
├── BOT_BRAIN_README.md      # This documentation
└── bots/                    # Your existing Node.js bot system
    ├── all_bots.js
    ├── botProperties.js
    └── ...
```

## 🧪 Testing & Development

### Run Tests
```bash
# Test the core bot brain
python bot_brain.py

# Test integration
python bot_brain_integration.py
```

### Example Output
```
🤖 Bot Brain > Bot1, mine some iron ore

Processing user request: Bot1, mine some iron ore
Intent: mining
Confidence: 0.90
Response: I'll coordinate the bots to mine the requested resources efficiently. I'll specifically involve Bot1 in this task.

Sending command to bots: {
  "type": "action",
  "action": "mine",
  "target": "Bot1",
  "params": {
    "task_id": "task_0001",
    "auto": true
  }
}
```

## 🚀 Advanced Features

### Custom Task Patterns
Define custom work patterns for different activities:
```python
work_patterns = {
    "custom_mining": ["scout_area", "identify_veins", "extract_resources", "return_base"],
    "custom_building": ["plan_design", "gather_materials", "construct", "decorate"]
}
```

### Resource Priority Management
Set custom resource priorities:
```python
resource_priorities = {
    "critical": ["diamond_pickaxe", "health_potion"],
    "high": ["iron_ingot", "coal"],
    "medium": ["stone", "wood"]
}
```

### Team Formation Strategies
Manage bot teams with different strategies:
```python
team_strategies = {
    "mining_team": ["Bot1", "Bot2", "Bot3"],
    "building_team": ["Bot4", "Bot5"],
    "exploration_team": ["Bot6", "Bot7"]
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Bot system configuration
BOT_COUNT=19
SERVER_HOST=localhost
SERVER_PORT=25565
```

### Custom Settings
Modify the bot brain configuration in `bot_brain.py`:
- Resource priorities
- Emergency response strategies
- Work patterns
- Team configurations

## 🐛 Troubleshooting

### Common Issues
1. **Python not found**: Ensure Python 3.7+ is installed
2. **Import errors**: Check that all files are in the same directory
3. **Node.js integration**: Ensure your Node.js bot system is running
4. **Permission errors**: Check file permissions and Python path

### Debug Mode
Enable detailed logging by modifying the logging level in `bot_brain.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

To extend the bot brain system:

1. **Add New Task Types**: Extend the task generation methods
2. **Enhance Intelligence**: Improve prompt analysis and response generation
3. **New Integrations**: Add support for additional communication protocols
4. **Custom Behaviors**: Implement specialized bot behaviors

## 📄 License

This bot brain system is designed to work with your existing Minecraft bot setup. Feel free to modify and extend it for your specific needs.

## 🆘 Support

For issues or questions:
1. Check the logs in `bot_brain.log`
2. Review the example outputs
3. Test with simple commands first
4. Ensure Python 3.7+ compatibility

---

**Happy Botting! 🤖⚡**