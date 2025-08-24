# 🤖 AI Commands System - Minecraft Bot Hub

The AI Commands system provides comprehensive control over Minecraft bots through natural language commands, vision system management, and advanced configuration options.

## 🏗️ **System Architecture**

```
ai_commands/
├── config/                 # Configuration files
│   └── ai_config.json     # AI behavior and vision settings
├── input/                  # Core AI logic and handlers
│   ├── bot_ai.py         # Main bot AI system
│   └── discord_handler.py # Discord bot integration
└── commands/              # Command definitions and handlers
    ├── actions/           # Action commands (mine, build, etc.)
    ├── movement/          # Movement commands
    └── team_commands.json # Team coordination
```

## 🎯 **Core Features**

### **🧠 AI Bot System**
- **Smart State Management**: 12 different bot states (IDLE, MINING, BUILDING, etc.)
- **Memory Persistence**: JSON-based memory system for each bot
- **Priority-Based Actions**: Intelligent action prioritization system
- **Vision Integration**: Real-time camera feed processing

### **👁️ Vision System**
- **Multi-Camera Support**: 4 specialized camera types
- **Real-Time Analysis**: Live environmental data processing
- **Thermal Vision**: Heat detection and temperature mapping
- **Depth Sensing**: 3D mapping and obstacle detection
- **Object Recognition**: Entity tracking and item identification

### **⚙️ Settings Management**
- **Server Configuration**: Name, port, and IP management
- **Bot Network Settings**: Individual bot IP and port configuration
- **Vision System Control**: Enable/disable and configure cameras
- **Performance Optimization**: Bot behavior and safety thresholds

## 🚀 **Available Commands**

### **🎮 Basic Actions**
- `mine <bot> <block>` - Mine specific block types
- `build <bot> <structure>` - Build structures (house, tower, farm)
- `collect <bot> <item>` - Collect resources (wood, stone, food)
- `craft <bot> <item> <quantity>` - Craft items and tools
- `farm <bot> <crop>` - Farm crops and breed animals

### **🔧 Advanced Actions**
- `vision <bot> <action>` - Manage vision systems
- `camera <bot> <setting> <value>` - Control camera settings
- `settings <bot> <category> <setting> <value>` - Configure bot settings
- `monitor <bot> <metric>` - Monitor bot performance
- `optimize <bot> <aspect>` - Optimize bot systems

### **🛠️ Management Commands**
- `backup <bot> <type>` - Create bot backups
- `restore <bot> <backup_id>` - Restore from backup
- `update <bot> <component>` - Update bot firmware
- `diagnose <bot> <test_type>` - Run diagnostic tests
- `calibrate <bot> <system>` - Calibrate bot systems

### **🚶 Movement Commands**
- `move <bot> <x> <y> <z>` - Move to coordinates
- `follow <bot> <target>` - Follow another bot
- `stop <bot>` - Stop movement

## 📱 **Discord Integration**

The system includes a full Discord bot with commands:

```
!vision <bot> status      - Check vision status
!vision <bot> toggle on   - Enable/disable vision
!settings server <name> <port> <ip> - Update server config
!bot ping <bot>          - Ping a bot
!bot restart <bot>       - Restart a bot
!system                  - Get system information
!help                    - Show all commands
```

## 🤖 **Bot Types & Capabilities**

### **Bot Alpha - Main Camera**
- **IP**: 192.168.1.101:8080
- **Features**: Environment analysis, block detection
- **Specialty**: General purpose, structural analysis

### **Bot Beta - Thermal Vision**
- **IP**: 192.168.1.102:8081
- **Features**: Temperature mapping, heat detection
- **Specialty**: Thermal analysis, fire detection

### **Bot Gamma - Depth Sensor**
- **IP**: 192.168.1.103:8082
- **Features**: 3D mapping, distance measurement
- **Specialty**: Spatial awareness, obstacle detection

### **Bot Delta - Object Detection**
- **IP**: 192.168.1.104:8083
- **Features**: Entity tracking, item recognition
- **Specialty**: Object identification, inventory management

## ⚙️ **Configuration**

### **AI Settings (`ai_config.json`)**
```json
{
  "ai_settings": {
    "command_processing": {
      "interval_ms": 1000,
      "max_queue_size": 100,
      "timeout_ms": 5000
    },
    "vision_system": {
      "camera_update_interval": 500,
      "max_vision_range": 64,
      "thermal_vision_enabled": true
    },
    "bot_management": {
      "auto_health_check": true,
      "ping_interval": 30000
    }
  }
}
```

### **Bot Behavior Settings**
- **Follow Distance**: 5 blocks (configurable)
- **Movement Speed**: 1.0 (configurable)
- **Health Threshold**: Safety threshold for actions
- **Vision Range**: Maximum camera detection range

## 🔌 **Integration Points**

### **Web Interface**
- **Chat System**: Process commands through web chat
- **Settings Panel**: Visual configuration interface
- **Vision Streams**: Live camera feed display
- **Bot Management**: Real-time bot status and control

### **Python API**
```python
from ai_commands.input.bot_ai import BotAI, BotProperties

# Create a bot
bot_props = BotProperties(
    name="MyBot",
    team_members=["Bot1", "Bot2"],
    camera_type="main_camera",
    ip_address="192.168.1.100",
    port=8080
)

# Initialize AI
bot_ai = BotAI(bot_props)

# Execute commands
result = bot_ai.execute_action("mine", {"block_type": "diamond_ore"})
vision_data = bot_ai.get_vision_data()
```

## 🚀 **Getting Started**

### **1. Setup Environment**
```bash
cd ai_commands
pip install -r requirements.txt
```

### **2. Configure Bots**
Edit `config/ai_config.json` to set your server and bot configurations.

### **3. Start Discord Bot**
```bash
export DISCORD_TOKEN="your_token_here"
python input/discord_handler.py
```

### **4. Use Web Interface**
Open the web interface and start chatting with the AI system.

## 🔧 **Customization**

### **Adding New Commands**
1. Add command definition to `commands/actions/action_commands.json`
2. Implement handler in `commands/actions/action_handler.py`
3. Update Discord handler if needed

### **Adding New Bot Types**
1. Define camera type in configuration
2. Add vision processing logic
3. Update bot initialization

### **Custom Vision Systems**
1. Extend `BotAI` class with new vision methods
2. Add camera configuration
3. Implement data processing logic

## 📊 **Monitoring & Debugging**

### **System Information**
- Real-time uptime tracking
- Active connection monitoring
- Bot status overview
- Performance metrics

### **Diagnostic Tools**
- Vision system tests
- Network connectivity checks
- Bot health monitoring
- Performance optimization

### **Logging & Debugging**
- Command execution logs
- Error tracking and reporting
- Performance analytics
- System health monitoring

## 🎮 **Minecraft Integration**

### **Block Detection**
- Automatic block type recognition
- Resource gathering optimization
- Building pattern analysis
- Structural integrity assessment

### **World Analysis**
- Environmental scanning
- Resource mapping
- Threat detection
- Pathfinding optimization

### **Multiplayer Support**
- Team coordination
- Shared resource management
- Collaborative building
- Strategic planning

## 🔒 **Security Features**

- **Command Validation**: Parameter validation and sanitization
- **Access Control**: Role-based command permissions
- **Rate Limiting**: Command execution throttling
- **Audit Logging**: Complete command history tracking

## 📈 **Performance Optimization**

- **Command Queuing**: Efficient command processing
- **Memory Management**: Optimized bot state storage
- **Vision Processing**: Real-time camera feed analysis
- **Network Optimization**: Efficient bot communication

## 🌟 **Future Enhancements**

- **Machine Learning**: Advanced AI decision making
- **Voice Commands**: Speech-to-command processing
- **Mobile App**: Mobile bot control interface
- **Cloud Integration**: Multi-server bot management
- **Advanced Vision**: AI-powered object recognition

---

**🤖 Minecraft Bot Hub - Where AI Meets the Blocky World!**

For more information, see the main project README or contact the development team.