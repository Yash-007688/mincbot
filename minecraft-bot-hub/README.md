# 🚀 Minecraft Bot Hub - Render Deployment Package

This directory contains all the files needed to deploy your Minecraft Bot Hub to Render.

## 📁 File Structure

```
minecraft-bot-hub/
├── 🚀 app_production.py              # Production Flask application
├── 🚀 start_production.py            # Production startup script
├── 📦 requirements_production.txt    # Production dependencies
├── ⚙️ render.yaml                    # Render configuration
├── 🌐 templates/                     # HTML templates
├── 🎨 static/                        # CSS, JS, images
├── 🤖 ai_commands/                   # AI system
├── 🗄️ database.py                    # Database manager
├── 🏗️ server_manager.py              # Server management
├── 📦 inventory_manager.py           # Inventory management
└── ⌨️ command_handler.py             # Command handling
```

## 🚀 Render Deployment

### **Build Command**
```bash
pip install -r requirements_production.txt
```

### **Start Command**
```bash
python start_production.py
```

### **Environment Variables**
Set these in your Render dashboard:

```bash
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_FILE=minecraft_bot_hub.db
HOST=0.0.0.0
PORT=10000
AI_SYSTEM_ENABLED=true
MANAGEMENT_SYSTEMS_ENABLED=true
DATABASE_ENABLED=true
```

## 🌐 Access Your App

Once deployed, your app will be available at:
```
https://your-app-name.onrender.com
```

## 🔑 Default Login
```
Username: yash
Password: yash
```

## 📚 Documentation

- **`RENDER_DEPLOYMENT_GUIDE.md`** - Complete deployment guide
- **`render.yaml`** - Render configuration reference
- **`start_production.py`** - Production startup details

---

**Your Minecraft Bot Hub is ready for Render deployment! 🎉✨**