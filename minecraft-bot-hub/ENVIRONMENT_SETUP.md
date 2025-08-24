# 🌐 Environment Variables Setup Guide

## 🚀 **Minecraft Bot Hub - Complete Environment Configuration**

This guide explains how to set up environment variables for both **local development** and **Render deployment**.

---

## 📁 **File Structure**

```
minecraft-bot-hub/
├── .env                    # 🚫 Local development (DO NOT COMMIT)
├── .env.example           # ✅ Reference template (safe to commit)
├── .gitignore             # 🛡️ Protects sensitive files
└── ENVIRONMENT_SETUP.md   # 📖 This guide
```

---

## 🔐 **Local Development Setup**

### **Step 1: Copy Environment Template**
```bash
# Copy the example file to create your local .env
cp .env.example .env
```

### **Step 2: Edit Local Variables**
```bash
# Edit .env file with your local settings
nano .env
# or
code .env
```

### **Step 3: Customize for Local Use**
```env
# Local development settings
FLASK_ENV=development
FLASK_SECRET_KEY=local-dev-secret-key-2024
DATABASE_FILE=local_minecraft_bot_hub.db
HOST=127.0.0.1
PORT=5000
```

---

## ☁️ **Render Deployment Setup**

### **Step 1: Access Render Dashboard**
1. **Go to [render.com](https://render.com)**
2. **Login to your account**
3. **Select your service** (`minecraft-bot-hub`)

### **Step 2: Navigate to Environment**
1. **Click "Environment"** tab
2. **Click "Add Environment Variable"**

### **Step 3: Add Required Variables**

#### **🔑 Essential Variables (Must Set)**
```
Key: FLASK_SECRET_KEY
Value: minecraft-bot-hub-super-secret-2024-yash-007688
```

#### **🌍 Core Configuration**
```
Key: FLASK_ENV
Value: production

Key: DATABASE_FILE
Value: minecraft_bot_hub.db

Key: HOST
Value: 0.0.0.0

Key: PORT
Value: 10000
```

#### **⚙️ Feature Toggles**
```
Key: AI_SYSTEM_ENABLED
Value: true

Key: MANAGEMENT_SYSTEMS_ENABLED
Value: true

Key: DATABASE_ENABLED
Value: true
```

#### **🎮 Server Configuration**
```
Key: SERVER_NAME
Value: mcfleet

Key: SERVER_IP
Value: play.mcfleet.net

Key: SERVER_PORT
Value: 25565
```

---

## 📊 **Complete Variables Reference**

### **🔑 Security & Core**
| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `FLASK_SECRET_KEY` | Auto-gen | ✅ Yes | Session encryption |
| `FLASK_ENV` | `production` | ❌ No | Environment mode |
| `DATABASE_FILE` | `minecraft_bot_hub.db` | ❌ No | Database filename |
| `HOST` | `0.0.0.0` | ❌ No | Server host |
| `PORT` | `10000` | ❌ No | Server port |

### **⚙️ Features**
| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `AI_SYSTEM_ENABLED` | `true` | ❌ No | Enable AI features |
| `MANAGEMENT_SYSTEMS_ENABLED` | `true` | ❌ No | Enable management |
| `DATABASE_ENABLED` | `true` | ❌ No | Enable database |

### **🎮 Minecraft Server**
| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `SERVER_NAME` | `mcfleet` | ❌ No | Default server name |
| `SERVER_IP` | `play.mcfleet.net` | ❌ No | Default server IP |
| `SERVER_PORT` | `25565` | ❌ No | Default server port |

### **🔧 Advanced Settings**
| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `SESSION_COOKIE_SECURE` | `false` | ❌ No | HTTPS cookies |
| `SESSION_COOKIE_HTTPONLY` | `true` | ❌ No | HTTP-only cookies |
| `LOG_LEVEL` | `INFO` | ❌ No | Logging detail |
| `SOCKETIO_ASYNC_MODE` | `eventlet` | ❌ No | Async mode |

---

## 🚨 **Security Warnings**

### **❌ Never Do This:**
- **Commit `.env` files** to Git
- **Share secret keys** publicly
- **Use weak passwords** as secret keys
- **Store secrets** in code comments

### **✅ Always Do This:**
- **Use strong secret keys** (32+ characters)
- **Keep `.env` in `.gitignore`**
- **Use different keys** for dev/prod
- **Rotate keys** periodically

---

## 🔄 **Automatic Fallbacks**

### **What Happens If Variables Are Missing:**

#### **✅ Auto-Generated:**
- `FLASK_SECRET_KEY` → Random 64-character hex
- `FLASK_ENV` → `production`
- `DATABASE_FILE` → `minecraft_bot_hub.db`
- `HOST` → `0.0.0.0`

#### **⚠️ Uses Render Defaults:**
- `PORT` → Render's assigned port
- `HOST` → `0.0.0.0` (all interfaces)

#### **🚫 Must Be Set:**
- No critical variables are required!

---

## 🚀 **Quick Start (Minimal Setup)**

### **For Render Deployment:**
1. **Set just one variable:**
   ```
   FLASK_SECRET_KEY = minecraft-bot-hub-super-secret-2024-yash-007688
   ```

2. **Everything else auto-configures!**

### **For Local Development:**
1. **Copy `.env.example` to `.env`**
2. **Edit with your local settings**
3. **Run the app locally**

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **"Missing Environment Variables" Error**
- **Solution**: Variables are auto-generated, check logs for details

#### **"Port Already in Use" Error**
- **Solution**: Render handles port assignment automatically

#### **"Database Connection Failed" Error**
- **Solution**: Database file is auto-created in production

#### **"Secret Key Not Set" Error**
- **Solution**: Key is auto-generated if not provided

---

## 📞 **Support**

### **If You Need Help:**
1. **Check Render logs** for error messages
2. **Verify environment variables** are set correctly
3. **Check GitHub repository** for latest updates
4. **Review this guide** for configuration details

---

## 🎉 **Success Indicators**

### **✅ Your App is Working When:**
- **Render logs show**: "✅ Environment variables configured successfully"
- **No error messages** about missing variables
- **App starts** without crashes
- **Website loads** at your Render URL

---

**🚀 Happy Deploying! Your Minecraft Bot Hub is ready for production! 🎮✨**