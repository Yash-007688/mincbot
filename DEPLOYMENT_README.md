# 🚀 Minecraft Bot Hub - Bot Deployment & Authentication System

## ✨ New Features Added

### 🔐 **User Authentication System**
- **Database-driven user management** with SQLite
- **Session management** with secure cookies
- **Default user account**: `yash` / `yash` (admin role)
- **Role-based permissions** (admin, moderator, user)
- **Secure password hashing** using SHA-256

### 🎮 **Bot Deployment Management**
- **Configurable bot deployment** with slider (1-20 bots)
- **Server configuration**: IP, name, port
- **Deployment status tracking** (pending, deploying, active, stopped, error)
- **Real-time deployment monitoring**
- **Default MCFleet configuration**: `play.mcfleet.net:25565`

### 🎯 **Go Live Button**
- **One-click bot deployment** from chat interface
- **Real-time deployment status** with visual feedback
- **Live mode indicator** with pulsing animation
- **Instant bot activation** across all systems

## 🏗️ **System Architecture**

```
Minecraft Bot Hub
├── Web Interface (HTML/CSS/JS)
├── Flask Backend (REST API + WebSocket)
├── Database System (SQLite)
│   ├── User Management
│   ├── Session Management
│   └── Bot Deployments
├── AI Commands System
├── Server Manager (Players, Bots, Coordinates)
├── Inventory Manager (Items, Economy, Trading)
└── Command Handler (Commands, Permissions, Cooldowns)
```

## 🚀 **Quick Start Guide**

### **1. Installation & Setup**

```bash
# Clone the repository
git clone <repository-url>
cd minecraft-bot-hub

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### **2. Access the System**

- **Home Page**: http://localhost:5000/
- **Login Page**: http://localhost:5000/login
- **Chat Interface**: http://localhost:5000/chat (requires login)

### **3. Default Login Credentials**

```
Username: yash
Password: yash
Role: Admin
Permissions: admin.all, user.basic, bot.deploy, bot.manage
```

## 🔧 **Configuration**

### **Default Bot Deployment Settings**

```json
{
  "deployment_name": "MCFleet Main",
  "bot_count": 4,
  "server_ip": "play.mcfleet.net",
  "server_name": "mcfleet",
  "server_port": 25565,
  "configuration": {
    "auto_restart": true,
    "max_bots": 10,
    "deployment_zone": "main",
    "priority": "high"
  }
}
```

### **Environment Variables**

```bash
# Database Configuration
DATABASE_FILE=minecraft_bot_hub.db

# Server Configuration
HOST=0.0.0.0
PORT=5000
SECRET_KEY=your-secret-key-here

# AI System
AI_SYSTEM_ENABLED=true
MANAGEMENT_SYSTEMS_ENABLED=true
DATABASE_ENABLED=true
```

## 📱 **User Interface Features**

### **🔐 Login Page**
- **Modern glassmorphism design**
- **Default credentials display**
- **Secure authentication flow**
- **Session management**

### **💬 Chat Interface**
- **AI-powered chat assistant**
- **Real-time bot vision streams**
- **Go Live button** for instant deployment
- **Settings panel** with deployment configuration

### **⚙️ Settings Panel**
- **Server Configuration**
  - Server name, IP, port
  - Save/load configurations
  
- **Bot Management**
  - Bot status monitoring
  - Ping and restart controls
  
- **🚀 Bot Deployment**
  - Deployment name
  - **Bot count slider (1-20)**
  - Server configuration
  - Deploy button
  
- **Network Tools**
  - Connection testing
  - Ping diagnostics
  
- **System Information**
  - Real-time status
  - Connection monitoring

## 🎮 **Bot Deployment Process**

### **1. Configuration**
1. **Open Settings** (⚙️ button)
2. **Navigate to Bot Deployment** section
3. **Set deployment name** (e.g., "MCFleet Main")
4. **Adjust bot count** using the slider (1-20 bots)
5. **Configure server details**:
   - IP: `play.mcfleet.net`
   - Name: `mcfleet`
   - Port: `25565`

### **2. Deployment**
1. **Click "🚀 Deploy Bots"** button
2. **Monitor deployment progress**
3. **View real-time status updates**
4. **Check deployment completion**

### **3. Go Live**
1. **Click "🚀 Go Live"** button in chat header
2. **Watch bots deploy sequentially**
3. **Monitor live status indicators**
4. **Bots become active on server**

## 🔌 **API Endpoints**

### **Authentication**
```http
POST /auth/login          # User login
POST /auth/logout         # User logout
GET  /auth/check          # Check authentication status
```

### **Bot Deployment**
```http
GET    /api/deployments/list                    # List deployments
POST   /api/deployments/create                  # Create deployment
POST   /api/deployments/{id}/deploy            # Deploy bots
POST   /api/deployments/{id}/stop              # Stop deployment
```

### **Management Systems**
```http
GET /api/players/list                          # List all players
GET /api/inventory/{id}                        # Get player inventory
GET /api/economy/{id}/balance                  # Get player balance
GET /api/commands/list                         # List available commands
GET /api/system/info                           # System information
```

## 🗄️ **Database Schema**

### **Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    permissions TEXT DEFAULT '[]'
);
```

### **Bot Deployments Table**
```sql
CREATE TABLE bot_deployments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    deployment_name TEXT NOT NULL,
    bot_count INTEGER NOT NULL,
    server_ip TEXT NOT NULL,
    server_name TEXT NOT NULL,
    server_port INTEGER NOT NULL,
    deployment_status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    configuration TEXT DEFAULT '{}',
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### **User Sessions Table**
```sql
CREATE TABLE user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🎯 **Usage Examples**

### **Deploy 10 Bots to MCFleet**

1. **Login** with `yash` / `yash`
2. **Open Settings** panel
3. **Configure deployment**:
   - Name: "MCFleet Large"
   - Bot Count: 10 (use slider)
   - Server: `play.mcfleet.net:25565`
4. **Click "🚀 Deploy Bots"**
5. **Monitor deployment progress**

### **Go Live with Current Configuration**

1. **Ensure deployment is configured**
2. **Click "🚀 Go Live"** button
3. **Watch bots deploy sequentially**:
   - Bot Alpha ✅
   - Bot Beta ✅
   - Bot Gamma ✅
   - Bot Delta ✅
4. **All bots are now LIVE!**

### **Monitor Bot Status**

1. **Open Settings** panel
2. **View Bot Management** section
3. **Check individual bot status**
4. **Use Ping/Restart controls**

## 🔒 **Security Features**

### **Authentication**
- **Secure password hashing** (SHA-256)
- **Session-based authentication**
- **24-hour session expiry**
- **IP address tracking**

### **Authorization**
- **Role-based access control**
- **Permission-based command execution**
- **User isolation** (users can only access their own deployments)

### **Data Protection**
- **SQL injection prevention**
- **XSS protection**
- **CSRF protection**
- **Secure cookie handling**

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Login Fails**
```bash
# Check database file exists
ls -la minecraft_bot_hub.db

# Verify database tables
python -c "import sqlite3; conn = sqlite3.connect('minecraft_bot_hub.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

#### **Deployment Fails**
```bash
# Check system logs
tail -f logs/app.log

# Verify all systems are running
curl http://localhost:5000/api/system/info
```

#### **Bots Not Connecting**
```bash
# Test server connectivity
ping play.mcfleet.net
telnet play.mcfleet.net 25565

# Check bot status
curl http://localhost:5000/api/bots/status
```

### **Debug Mode**

```bash
# Enable debug logging
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose output
python run.py
```

## 📊 **Monitoring & Logs**

### **System Health**
- **Real-time status monitoring**
- **Connection tracking**
- **Performance metrics**
- **Error logging**

### **Log Files**
```bash
# Application logs
tail -f logs/app.log

# Database logs
tail -f logs/database.log

# System logs
tail -f logs/system.log
```

## 🔄 **Updates & Maintenance**

### **Database Maintenance**
```bash
# Backup database
cp minecraft_bot_hub.db backup_$(date +%Y%m%d).db

# Clean expired sessions
python -c "from database import DatabaseManager; db = DatabaseManager(); db.cleanup_expired_sessions()"
```

### **System Updates**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
pkill -f "python run.py"
python run.py
```

## 🎉 **What's New**

### **Version 2.0 Features**
- ✅ **User Authentication System**
- ✅ **Bot Deployment Management**
- ✅ **Go Live Button**
- ✅ **Database Integration**
- ✅ **Session Management**
- ✅ **Role-based Permissions**
- ✅ **Real-time Deployment Monitoring**
- ✅ **MCFleet Server Integration**

### **Coming Soon**
- 🔄 **Advanced Bot AI**
- 🔄 **Multi-server Support**
- 🔄 **Bot Performance Analytics**
- 🔄 **Automated Scaling**
- 🔄 **Webhook Integration**

## 🤝 **Support & Community**

### **Documentation**
- **API Reference**: `/api/docs`
- **System Status**: `/api/system/info`
- **Health Check**: `/health`

### **Getting Help**
1. **Check troubleshooting section**
2. **Review system logs**
3. **Test with default credentials**
4. **Verify all systems are running**

---

## 🎯 **Quick Commands**

```bash
# Start the system
python run.py

# Test database
python database.py

# Check system status
curl http://localhost:5000/api/system/info

# Login (default)
Username: yash
Password: yash

# Go Live
Click 🚀 Go Live button in chat header
```

**Your Minecraft Bot Hub is now ready with full authentication and bot deployment capabilities! 🚀✨**