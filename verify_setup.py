#!/usr/bin/env python3
"""
🔍 Minecraft Bot Hub - Setup Verification Script
Quick verification that all components are properly configured
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and print status"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - MISSING")
        return False

def main():
    """Verify all components are properly set up"""
    print("🔍 Minecraft Bot Hub - Setup Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check core Python files
    print("\n📁 Core Python Files:")
    core_files = [
        ("app.py", "Main Flask Application"),
        ("database.py", "Database Manager"),
        ("server_manager.py", "Server Manager"),
        ("inventory_manager.py", "Inventory Manager"),
        ("command_handler.py", "Command Handler"),
        ("run.py", "Development Server"),
        ("config.py", "Configuration"),
        ("requirements.txt", "Dependencies")
    ]
    
    for filename, description in core_files:
        if check_file_exists(filename, description):
            checks_passed += 1
        total_checks += 1
    
    # Check HTML templates
    print("\n🌐 HTML Templates:")
    template_files = [
        ("templates/index.html", "Home Page"),
        ("templates/login.html", "Login Page"),
        ("templates/prompt.html", "Chat Interface")
    ]
    
    for filepath, description in template_files:
        if check_file_exists(filepath, description):
            checks_passed += 1
        total_checks += 1
    
    # Check directories
    print("\n📁 Required Directories:")
    directories = [
        ("templates", "Templates Directory"),
        ("static", "Static Assets Directory"),
        ("ai_commands", "AI Commands System"),
        (".git", "Git Repository")
    ]
    
    for dirname, description in directories:
        if check_directory_exists(dirname, description):
            checks_passed += 1
        total_checks += 1
    
    # Check static subdirectories
    print("\n🎨 Static Assets:")
    static_dirs = [
        ("static/css", "CSS Stylesheets"),
        ("static/js", "JavaScript Files"),
        ("static/images", "Image Assets")
    ]
    
    for dirpath, description in static_dirs:
        if check_directory_exists(dirpath, description):
            checks_passed += 1
        total_checks += 1
    
    # Check utility files
    print("\n🛠️ Utility Files:")
    utility_files = [
        ("start.sh", "Startup Script"),
        ("test_system.py", "System Test Suite"),
        ("DEPLOYMENT_README.md", "Deployment Documentation"),
        ("FINAL_SUMMARY.md", "Final Summary")
    ]
    
    for filename, description in utility_files:
        if check_file_exists(filename, description):
            checks_passed += 1
        total_checks += 1
    
    # Check AI commands system
    print("\n🤖 AI Commands System:")
    ai_files = [
        ("ai_commands/bot_ip_manager.py", "Bot IP Manager"),
        ("ai_commands/input/bot_ai.py", "Bot AI Core"),
        ("ai_commands/commands/actions/action_handler.py", "Action Handler")
    ]
    
    for filepath, description in ai_files:
        if check_file_exists(filepath, description):
            checks_passed += 1
        total_checks += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All components are properly set up!")
        print("\n🚀 Ready to start:")
        print("   ./start.sh")
        print("\n🧪 Ready to test:")
        print("   python test_system.py")
        print("\n🌐 Ready to access:")
        print("   http://localhost:5000")
        print("   Login: yash / yash")
        return True
    else:
        print(f"⚠️  {total_checks - checks_passed} components are missing or misconfigured")
        print("Please check the errors above and fix them before starting")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Verification failed: {e}")
        sys.exit(1)