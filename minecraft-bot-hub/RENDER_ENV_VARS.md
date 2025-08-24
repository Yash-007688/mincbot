# 🔧 **Render Environment Variables Guide**

## 🚨 **Fix the Missing Environment Variables Error**

If you see this error:
```
Missing required environment variables: ['FLASK_SECRET_KEY']
```

Follow this guide to set the environment variables in Render.

## 🌐 **How to Set Environment Variables in Render**

### **Step 1: Go to Your Service Dashboard**
1. **Login to [render.com](https://render.com)**
2. **Click on your service** (minecraft-bot-hub)
3. **Go to "Environment" tab**

### **Step 2: Add Environment Variables**
Click **"Add Environment Variable"** and add these one by one:

## 📋 **Required Environment Variables**

### **1. FLASK_SECRET_KEY**
```
Key: FLASK_SECRET_KEY
Value: minecraft-bot-hub-secret-key-2024-production
```
**Purpose**: Security key for Flask sessions and cookies

### **2. PORT**
```
Key: PORT
Value: 10000
```
**Purpose**: Port for the application (Render sets this automatically)

## 🔧 **Optional Environment Variables**

### **3. FLASK_ENV**
```
Key: FLASK_ENV
Value: production
```
**Purpose**: Sets Flask to production mode

### **4. DATABASE_FILE**
```
Key: DATABASE_FILE
Value: minecraft_bot_hub.db
```
**Purpose**: SQLite database filename

### **5. HOST**
```
Key: HOST
Value: 0.0.0.0
```
**Purpose**: Host binding for the application

### **6. AI_SYSTEM_ENABLED**
```
Key: AI_SYSTEM_ENABLED
Value: true
```
**Purpose**: Enable AI commands system

### **7. MANAGEMENT_SYSTEMS_ENABLED**
```
Key: MANAGEMENT_SYSTEMS_ENABLED
Value: true
```
**Purpose**: Enable server/inventory management

### **8. DATABASE_ENABLED**
```
Key: DATABASE_ENABLED
Value: true
```
**Purpose**: Enable database functionality

## 🎯 **Quick Setup**

Copy and paste these into Render:

```bash
# Required
FLASK_SECRET_KEY=minecraft-bot-hub-secret-key-2024-production
PORT=10000

# Optional (recommended)
FLASK_ENV=production
DATABASE_FILE=minecraft_bot_hub.db
HOST=0.0.0.0
AI_SYSTEM_ENABLED=true
MANAGEMENT_SYSTEMS_ENABLED=true
DATABASE_ENABLED=true
```

## 🔄 **After Setting Variables**

1. **Save the environment variables**
2. **Go to "Manual Deploy"**
3. **Click "Deploy latest commit"**
4. **Wait for deployment to complete**
5. **Check logs for success**

## 🚨 **Common Issues**

### **Issue: Still getting missing variables error**
**Solution**: 
- Make sure you saved the environment variables
- Redeploy after setting variables
- Check that variables are exactly as shown above

### **Issue: Variables not showing up**
**Solution**:
- Refresh the page
- Check that you're in the right service
- Ensure variables are saved

### **Issue: Deployment fails after setting variables**
**Solution**:
- Check the build logs
- Verify variable names are correct
- Try a manual redeploy

## ✅ **Verification**

After setting variables, you should see in the logs:
```
✅ Environment variables check passed
✅ Production application loaded successfully
🌐 Starting production server...
```

## 🎉 **Success!**

Once environment variables are set correctly:
- ✅ **No more missing variables errors**
- ✅ **Application starts successfully**
- ✅ **Your Minecraft Bot Hub is live!**

## 🌐 **Access Your App**

Your app will be available at:
```
https://your-app-name.onrender.com
```

## 🔑 **Default Login**
```
Username: yash
Password: yash
```

---

**Set these environment variables and redeploy to fix the error! 🚀✨**