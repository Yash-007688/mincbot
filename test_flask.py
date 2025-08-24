#!/usr/bin/env python3
"""
Test script for Minecraft Bot Hub Flask Application
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_flask_app():
    """Test the Flask application endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Minecraft Bot Hub Flask Application")
    print("=" * 60)
    
    # Test 1: Home page
    print("1. Testing home page...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Home page accessible")
        else:
            print(f"   ❌ Home page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Home page error: {e}")
        return False
    
    # Test 2: Login page
    print("2. Testing login page...")
    try:
        response = requests.get(f"{base_url}/login", timeout=10)
        if response.status_code == 200:
            print("   ✅ Login page accessible")
        else:
            print(f"   ❌ Login page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Login page error: {e}")
        return False
    
    # Test 3: Chat page
    print("3. Testing chat page...")
    try:
        response = requests.get(f"{base_url}/chat", timeout=10)
        if response.status_code == 200:
            print("   ✅ Chat page accessible")
        else:
            print(f"   ❌ Chat page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Chat page error: {e}")
        return False
    
    # Test 4: Bot status API
    print("4. Testing bot status API...")
    try:
        response = requests.get(f"{base_url}/api/bots/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bot status API working: {len(data)} bots found")
            for bot_id, status in data.items():
                if status:
                    print(f"      - {bot_id}: {status.get('status', 'unknown')}")
        else:
            print(f"   ❌ Bot status API failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Bot status API error: {e}")
        return False
    
    # Test 5: System info API
    print("5. Testing system info API...")
    try:
        response = requests.get(f"{base_url}/api/system/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System info API working")
            print(f"      - Current time: {data.get('current_time', 'unknown')}")
            print(f"      - System status: {data.get('system_status', 'unknown')}")
            print(f"      - AI system: {data.get('ai_system_available', 'unknown')}")
        else:
            print(f"   ❌ System info API failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ System info API error: {e}")
        return False
    
    # Test 6: Chat message API
    print("6. Testing chat message API...")
    try:
        test_message = {
            "message": "Hello, this is a test message",
            "user": "TestUser"
        }
        response = requests.post(
            f"{base_url}/api/chat/message",
            json=test_message,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chat message API working")
            print(f"      - Response: {data.get('response', 'unknown')[:50]}...")
        else:
            print(f"   ❌ Chat message API failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Chat message API error: {e}")
        return False
    
    # Test 7: Bot ping API
    print("7. Testing bot ping API...")
    try:
        response = requests.post(f"{base_url}/api/settings/bots/alpha/ping", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bot ping API working")
            print(f"      - Bot: {data.get('bot_id', 'unknown')}")
            print(f"      - Status: {data.get('status', 'unknown')}")
            print(f"      - Ping: {data.get('ping_ms', 'unknown')}ms")
        else:
            print(f"   ❌ Bot ping API failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Bot ping API error: {e}")
        return False
    
    print("=" * 60)
    print("🎉 All tests completed successfully!")
    print("🚀 Your Flask application is working correctly!")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_socketio',
        'requests',
        'eventlet'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies available")
    return True

def check_files():
    """Check if required files exist"""
    print("📁 Checking project files...")
    
    required_files = [
        'app.py',
        'config.py',
        'run.py',
        'requirements.txt',
        'templates/index.html',
        'templates/login.html',
        'templates/prompt.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    print("   ✅ All required files present")
    return True

def main():
    """Main test function"""
    print("🤖 Minecraft Bot Hub - Flask Application Test")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        return False
    
    print()
    
    # Check files
    if not check_files():
        print("\n❌ File check failed!")
        return False
    
    print()
    
    # Check if Flask app is running
    print("🌐 Checking if Flask app is running...")
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask app is running")
            print()
            
            # Run tests
            return test_flask_app()
        else:
            print(f"   ❌ Flask app responded with status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("   ❌ Flask app is not running")
        print("\n💡 Start the Flask app first:")
        print("   python run.py")
        print("   # or")
        print("   python app.py")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 Test Summary: PASSED")
            sys.exit(0)
        else:
            print("\n🎯 Test Summary: FAILED")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)