#!/usr/bin/env python3
"""
🧪 Minecraft Bot Hub - System Test Suite
Tests all new features: authentication, database, bot deployment, and management systems
"""

import sys
import os
import time
import requests
import sqlite3
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_database():
    """Test database functionality"""
    print_header("Testing Database System")
    
    try:
        from database import DatabaseManager
        
        # Initialize database
        db = DatabaseManager()
        print_success("Database manager initialized")
        
        # Test user authentication
        user = db.authenticate_user("yash", "yash")
        if user:
            print_success(f"User authentication successful: {user.username} (Role: {user.role})")
        else:
            print_error("User authentication failed")
            return False
        
        # Test session creation
        session = db.create_session(user.id, user.username)
        if session:
            print_success(f"Session created: {session.session_id}")
        else:
            print_error("Session creation failed")
            return False
        
        # Test deployment creation
        deployment = db.create_deployment(
            user_id=user.id,
            deployment_name="Test Deployment",
            bot_count=5,
            server_ip="test.server.com",
            server_name="testserver",
            server_port=25565
        )
        if deployment:
            print_success(f"Deployment created: {deployment.deployment_name}")
        else:
            print_error("Deployment creation failed")
            return False
        
        # Cleanup
        db.delete_session(session.session_id)
        db.delete_deployment(deployment.id)
        print_success("Database cleanup completed")
        
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def test_management_systems():
    """Test management systems"""
    print_header("Testing Management Systems")
    
    try:
        from server_manager import ServerManager
        from inventory_manager import InventoryManager
        from command_handler import CommandHandler
        
        # Test Server Manager
        server_mgr = ServerManager()
        print_success("Server Manager initialized")
        
        # Test adding a player
        player_uuid = "test-player-123"
        server_mgr.add_player(
            uuid=player_uuid,
            username="TestPlayer",
            display_name="Test Player",
            coordinates=(100, 64, 200),
            dimension="overworld"
        )
        print_success("Test player added to server")
        
        # Test adding a bot
        bot_uuid = "test-bot-456"
        server_mgr.add_bot(
            uuid=bot_uuid,
            username="TestBot",
            bot_type="miner",
            coordinates=(150, 64, 250),
            dimension="overworld"
        )
        print_success("Test bot added to server")
        
        # Test Inventory Manager
        inv_mgr = InventoryManager()
        print_success("Inventory Manager initialized")
        
        # Test adding items
        inv_mgr.add_item_to_inventory(
            player_uuid=player_uuid,
            item_id="diamond_sword",
            quantity=1,
            slot=0
        )
        print_success("Item added to player inventory")
        
        # Test Command Handler
        cmd_handler = CommandHandler()
        print_success("Command Handler initialized")
        
        # Test command execution
        result = cmd_handler.execute_command(
            command="tp",
            arguments=["TestPlayer", "100", "64", "200"],
            player_uuid=player_uuid,
            player_name="TestPlayer"
        )
        print_success(f"Command executed: {result.success}")
        
        # Cleanup
        server_mgr.remove_player(player_uuid)
        server_mgr.remove_player(bot_uuid)
        print_success("Management systems cleanup completed")
        
        return True
        
    except Exception as e:
        print_error(f"Management systems test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application endpoints"""
    print_header("Testing Flask Application")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test home page
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print_success("Home page accessible")
        else:
            print_error(f"Home page failed: {response.status_code}")
            return False
        
        # Test login page
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print_success("Login page accessible")
        else:
            print_error(f"Login page failed: {response.status_code}")
            return False
        
        # Test chat page (should redirect to login)
        response = requests.get(f"{base_url}/chat")
        if response.status_code in [302, 401]:
            print_success("Chat page properly protected")
        else:
            print_error(f"Chat page protection failed: {response.status_code}")
            return False
        
        # Test system info endpoint
        response = requests.get(f"{base_url}/api/system/info")
        if response.status_code == 200:
            data = response.json()
            print_success(f"System info endpoint working: {data.get('status', 'unknown')}")
        else:
            print_error(f"System info endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Flask application not running. Start with: python run.py")
        return False
    except Exception as e:
        print_error(f"Flask test failed: {e}")
        return False

def test_authentication_flow():
    """Test complete authentication flow"""
    print_header("Testing Authentication Flow")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test login endpoint
        login_data = {
            "username": "yash",
            "password": "yash"
        }
        
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("Login endpoint working")
                
                # Get session cookie
                cookies = response.cookies
                session_cookie = cookies.get("session_id")
                
                if session_cookie:
                    print_success(f"Session cookie received: {session_cookie[:20]}...")
                    
                    # Test authenticated access to chat
                    response = requests.get(
                        f"{base_url}/chat",
                        cookies={"session_id": session_cookie}
                    )
                    
                    if response.status_code == 200:
                        print_success("Authenticated chat access working")
                    else:
                        print_error(f"Authenticated chat access failed: {response.status_code}")
                        return False
                    
                    # Test logout
                    response = requests.post(
                        f"{base_url}/auth/logout",
                        cookies={"session_id": session_cookie}
                    )
                    
                    if response.status_code == 200:
                        print_success("Logout endpoint working")
                    else:
                        print_error(f"Logout endpoint failed: {response.status_code}")
                        return False
                    
                else:
                    print_error("No session cookie received")
                    return False
                    
            else:
                print_error(f"Login failed: {data.get('error', 'unknown error')}")
                return False
        else:
            print_error(f"Login endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Flask application not running. Start with: python run.py")
        return False
    except Exception as e:
        print_error(f"Authentication flow test failed: {e}")
        return False

def test_bot_deployment():
    """Test bot deployment functionality"""
    print_header("Testing Bot Deployment")
    
    base_url = "http://localhost:5000"
    
    try:
        # First login to get session
        login_data = {"username": "yash", "password": "yash"}
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if not response.status_code == 200:
            print_error("Login failed for deployment test")
            return False
        
        cookies = {"session_id": response.cookies.get("session_id")}
        
        # Test deployment creation
        deployment_data = {
            "deployment_name": "Test Deployment",
            "bot_count": 3,
            "server_ip": "test.mcfleet.net",
            "server_name": "testserver",
            "server_port": 25565
        }
        
        response = requests.post(
            f"{base_url}/api/deployments/create",
            json=deployment_data,
            cookies=cookies
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                deployment_id = data.get("deployment_id")
                print_success(f"Deployment created: ID {deployment_id}")
                
                # Test deployment list
                response = requests.get(
                    f"{base_url}/api/deployments/list",
                    cookies=cookies
                )
                
                if response.status_code == 200:
                    data = response.json()
                    deployments = data.get("deployments", [])
                    print_success(f"Deployment list working: {len(deployments)} deployments")
                    
                    # Test deployment execution
                    response = requests.post(
                        f"{base_url}/api/deployments/{deployment_id}/deploy",
                        cookies=cookies
                    )
                    
                    if response.status_code == 200:
                        print_success("Deployment execution working")
                    else:
                        print_error(f"Deployment execution failed: {response.status_code}")
                        return False
                    
                else:
                    print_error(f"Deployment list failed: {response.status_code}")
                    return False
                    
            else:
                print_error(f"Deployment creation failed: {data.get('error', 'unknown error')}")
                return False
        else:
            print_error(f"Deployment creation endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Flask application not running. Start with: python run.py")
        return False
    except Exception as e:
        print_error(f"Bot deployment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Minecraft Bot Hub - Complete System Test")
    print_info("This script tests all new features and systems")
    
    tests = [
        ("Database System", test_database),
        ("Management Systems", test_management_systems),
        ("Flask Application", test_flask_app),
        ("Authentication Flow", test_authentication_flow),
        ("Bot Deployment", test_bot_deployment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print_error(f"⚠️  {total - passed} tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)