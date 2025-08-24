#!/bin/bash

# 🚀 Minecraft Bot Hub - Render Deployment Script
# This script helps prepare your application for Render deployment

echo "🚀 Preparing Minecraft Bot Hub for Render Deployment..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "database.py" ]; then
    echo "❌ Error: Please run this script from the minecraft-bot-hub directory"
    exit 1
fi

# Check if all required files exist
echo "🔍 Checking required files..."
required_files=(
    "render.yaml"
    "app_production.py"
    "requirements_production.txt"
    "start_production.py"
    "templates/index.html"
    "templates/login.html"
    "templates/prompt.html"
    "database.py"
    "server_manager.py"
    "inventory_manager.py"
    "command_handler.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing required files for Render deployment:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Please ensure all files are present before deploying."
    exit 1
fi

echo "✅ All required files present"

# Check if git repository is clean
echo "🔍 Checking git status..."
if [ -d ".git" ]; then
    git_status=$(git status --porcelain)
    if [ -n "$git_status" ]; then
        echo "⚠️  Warning: You have uncommitted changes:"
        echo "$git_status"
        echo ""
        read -p "Do you want to commit these changes before deploying? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "📝 Committing changes..."
            git add .
            git commit -m "🚀 Prepare for Render deployment"
            echo "✅ Changes committed"
        fi
    else
        echo "✅ Git repository is clean"
    fi
else
    echo "❌ Error: Not a git repository. Please initialize git first."
    exit 1
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Error: No remote origin configured. Please add your GitHub repository:"
    echo "   git remote add origin https://github.com/username/repository.git"
    exit 1
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
if git push origin main; then
    echo "✅ Successfully pushed to GitHub"
else
    echo "❌ Failed to push to GitHub. Please check your credentials and try again."
    exit 1
fi

# Display deployment instructions
echo ""
echo "🎉 Repository is ready for Render deployment!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login with your GitHub account"
echo "3. Click 'New +' and select 'Blueprint'"
echo "4. Connect your GitHub repository"
echo "5. Render will automatically detect render.yaml"
echo "6. Click 'Connect' to start deployment"
echo ""
echo "🔧 Environment Variables to Set:"
echo "   FLASK_SECRET_KEY=your-secret-key-here"
echo "   FLASK_ENV=production"
echo "   DATABASE_FILE=minecraft_bot_hub.db"
echo "   HOST=0.0.0.0"
echo "   PORT=10000"
echo ""
echo "🌐 Your app will be available at:"
echo "   https://your-app-name.onrender.com"
echo ""
echo "📚 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 Happy deploying! ✨"