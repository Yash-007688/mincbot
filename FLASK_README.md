# 🚀 Minecraft Bot Hub - Flask Application

A comprehensive Flask web application that integrates the Minecraft Bot Hub interface with the AI commands system, providing real-time bot management, vision streaming, and secure communication.

## 🏗️ **Architecture Overview**

```
Minecraft Bot Hub Flask App
├── Web Interface (HTML/CSS/JS)
│   ├── Home Page (Minecraft Style)
│   ├── Login System
│   └── Chat Interface with Bot Vision
├── Flask Backend
│   ├── REST API Endpoints
│   ├── WebSocket Support (SocketIO)
│   └── Bot Management System
├── AI Commands Integration
│   ├── Bot AI System
│   ├── IP Management
│   └── Command Processing
└── Real-time Features
    ├── Live Bot Status
    ├── Vision Streams
    └── Instant Communication
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-dev python3-pip nginx redis-server
```

### **2. Run Development Server**
```bash
# Start the Flask application
python run.py

# Or run directly
python app.py
```

### **3. Access the Application**
- **Home Page**: http://localhost:5000/
- **Login**: http://localhost:5000/login
- **Chat Interface**: http://localhost:5000/chat

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- pip package manager
- Git (for cloning the repository)

### **Step-by-Step Setup**

#### **1. Clone Repository**
```bash
git clone <repository-url>
cd minecraft-bot-hub
```

#### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Environment Configuration**
Create a `.env` file in the root directory:
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Server Configuration
HOST=0.0.0.0
PORT=5000

# AI System Configuration
AI_SYSTEM_ENABLED=True
AI_CONFIG_PATH=ai_commands/config

# Database Configuration (optional)
DATABASE_URL=sqlite:///minecraft_bot_hub.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0
```

#### **5. Initialize Directories**
```bash
python -c "from config import create_directories; create_directories()"
```

## 🎮 **Features**

### **🌐 Web Interface**
- **Minecraft-Style Homepage**: Pixelated design with animated elements
- **Secure Login System**: User authentication and session management
- **Chat Interface**: ChatGPT-like interface with bot vision integration
- **Settings Panel**: Server configuration and bot management
- **Real-Time Updates**: Live bot status and vision streams

### **🤖 Bot Management**
- **Live Status Monitoring**: Real-time bot health and performance
- **IP Rotation**: Automatic IP changes for security
- **Command Execution**: Send commands to bots via web interface
- **Vision Streaming**: Live camera feeds from all bots
- **Settings Configuration**: Manage bot parameters and network settings

### **🔒 Security Features**
- **Session Management**: Secure user sessions
- **IP Rotation**: Prevents bot tracking
- **Proxy Support**: Multiple proxy layers
- **VPN Integration**: Secure communication channels
- **Rate Limiting**: Protection against abuse

### **📡 Real-Time Communication**
- **WebSocket Support**: Instant updates and communication
- **Live Bot Status**: Real-time monitoring
- **Vision Streams**: Live camera feeds
- **Chat System**: Instant messaging with AI

## 🚀 **Running the Application**

### **Development Mode**
```bash
# Start development server
python run.py

# Or run directly
python app.py
```

### **Production Mode**
```bash
# Use production deployment script
python deploy.py

# Or use Gunicorn directly
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class eventlet app:app
```

### **Docker Deployment**
```bash
# Build Docker image
docker build -t minecraft-bot-hub .

# Run container
docker run -p 5000:5000 minecraft-bot-hub
```

## 📁 **Project Structure**

```
minecraft-bot-hub/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── run.py                # Development startup script
├── deploy.py             # Production deployment script
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   └── prompt.html      # Chat interface
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Images and icons
├── ai_commands/          # AI system integration
├── logs/                 # Application logs
├── uploads/              # File uploads
└── flask_session/        # Session storage
```

## 🔧 **Configuration**

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `True` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `AI_SYSTEM_ENABLED` | Enable AI system | `True` |
| `DATABASE_URL` | Database connection | `sqlite:///minecraft_bot_hub.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |

### **Configuration Classes**
- **DevelopmentConfig**: Development settings with debug enabled
- **ProductionConfig**: Production settings with security features
- **TestingConfig**: Testing configuration for unit tests

## 📡 **API Endpoints**

### **Bot Management**
- `GET /api/bots/status` - Get all bot statuses
- `GET /api/bots/<bot_id>/status` - Get specific bot status
- `POST /api/bots/<bot_id>/rotate` - Rotate bot IP
- `POST /api/bots/<bot_id>/command` - Execute bot command

### **Settings Management**
- `POST /api/settings/server` - Update server configuration
- `POST /api/settings/bots/<bot_id>/ping` - Ping bot
- `POST /api/settings/bots/<bot_id>/restart` - Restart bot

### **System Information**
- `GET /api/system/info` - Get system information
- `POST /api/chat/message` - Process chat message

### **WebSocket Events**
- `connect` - Client connection
- `disconnect` - Client disconnection
- `join_bot_room` - Join bot-specific room
- `leave_bot_room` - Leave bot-specific room

## 🔒 **Security Features**

### **Authentication & Authorization**
- Session-based authentication
- Secure session storage
- CSRF protection
- Rate limiting

### **Network Security**
- IP rotation for bots
- Proxy support
- VPN integration
- Connection encryption

### **Data Protection**
- Input validation
- SQL injection prevention
- XSS protection
- Secure headers

## 📊 **Monitoring & Logging**

### **Application Logs**
- **Access Logs**: HTTP request logging
- **Error Logs**: Application error tracking
- **Performance Logs**: Response time monitoring
- **Security Logs**: Authentication and security events

### **Health Checks**
- **System Health**: Overall application status
- **Bot Health**: Individual bot status
- **Database Health**: Database connectivity
- **External Services**: Redis, proxy, VPN status

### **Metrics Collection**
- **Request Counts**: API endpoint usage
- **Response Times**: Performance metrics
- **Error Rates**: Error frequency tracking
- **User Activity**: User interaction metrics

## 🚀 **Deployment**

### **Development Deployment**
```bash
# Simple development server
python run.py
```

### **Production Deployment**
```bash
# Use production script
python deploy.py

# Or manual deployment
gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class eventlet app:app
```

### **Docker Deployment**
```bash
# Build and run
docker build -t minecraft-bot-hub .
docker run -d -p 5000:5000 --name minecraft-bot-hub minecraft-bot-hub
```

### **Systemd Service**
```bash
# Enable and start service
sudo systemctl enable minecraft-bot-hub
sudo systemctl start minecraft-bot-hub

# Check status
sudo systemctl status minecraft-bot-hub
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### **2. Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

#### **3. AI System Not Available**
```bash
# Check AI system path
ls -la ai_commands/

# Install AI system dependencies
cd ai_commands && pip install -r requirements.txt
```

#### **4. WebSocket Connection Issues**
```bash
# Check SocketIO configuration
# Ensure eventlet is installed
pip install eventlet

# Check firewall settings
sudo ufw status
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run.py

# Check logs
tail -f logs/error.log
```

### **Performance Issues**
```bash
# Monitor system resources
htop
iotop

# Check application performance
python -m cProfile -o profile.stats app.py
```

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

### **Integration Tests**
```bash
# Test API endpoints
python -m pytest tests/test_api.py

# Test WebSocket functionality
python -m pytest tests/test_socketio.py
```

### **Load Testing**
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/locustfile.py
```

## 📚 **Development**

### **Code Style**
- Follow PEP 8 guidelines
- Use type hints
- Document all functions
- Write unit tests

### **Git Workflow**
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create pull request
git push origin feature/new-feature
```

### **Adding New Features**
1. Create feature branch
2. Implement functionality
3. Add tests
4. Update documentation
5. Create pull request

## 🌟 **Future Enhancements**

### **Planned Features**
- **User Management**: User roles and permissions
- **Database Integration**: Persistent data storage
- **Mobile App**: Mobile interface
- **Cloud Deployment**: AWS/Azure integration
- **Advanced Analytics**: Machine learning insights

### **Performance Improvements**
- **Caching**: Redis-based caching
- **CDN Integration**: Content delivery network
- **Load Balancing**: Multiple server instances
- **Database Optimization**: Query optimization

## 📞 **Support & Documentation**

### **Getting Help**
- **Documentation**: This README and inline code comments
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Wiki**: Check project wiki for detailed guides

### **Contributing**
- **Fork Repository**: Create your own fork
- **Submit Issues**: Report bugs and request features
- **Create Pull Requests**: Submit code improvements
- **Code Review**: Participate in code reviews

### **Community**
- **Discord**: Join our Discord server
- **Forum**: Participate in community discussions
- **Newsletter**: Subscribe to updates
- **Events**: Attend community events

---

**🚀 Minecraft Bot Hub Flask Application - Where Web Meets AI!**

For more information, see the main project README or contact the development team.