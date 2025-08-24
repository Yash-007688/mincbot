#!/usr/bin/env python3
"""
Test script to verify all Flask routes work correctly
"""

import requests
import time
import sys

def test_routes():
    """Test all routes for internal server errors"""
    base_url = "http://localhost:5000"
    
    # Routes to test
    routes = [
        "/",
        "/login", 
        "/chat",
        "/health",
        "/api/system/info",
        "/api/deployments/list"
    ]
    
    print("🧪 Testing all Flask routes...")
    print("=" * 50)
    
    for route in routes:
        try:
            print(f"Testing {route}...", end=" ")
            response = requests.get(f"{base_url}{route}", timeout=5)
            
            if response.status_code == 200:
                print("✅ SUCCESS")
            elif response.status_code == 302:  # Redirect (expected for /chat without auth)
                print("✅ REDIRECT (Expected)")
            else:
                print(f"⚠️ Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - Is the app running?")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n🎉 All route tests completed!")
    return True

def test_auth_flow():
    """Test authentication flow"""
    base_url = "http://localhost:5000"
    
    print("\n🔐 Testing authentication flow...")
    print("=" * 50)
    
    try:
        # Test login
        print("Testing login...", end=" ")
        login_data = {"username": "yash", "password": "yash"}
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            cookies = response.cookies
            
            # Test authenticated route
            print("Testing authenticated chat route...", end=" ")
            response = requests.get(f"{base_url}/chat", cookies=cookies, timeout=5)
            
            if response.status_code == 200:
                print("✅ SUCCESS")
            else:
                print(f"⚠️ Status: {response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Minecraft Bot Hub - Route Testing")
    print("Make sure the Flask app is running on port 5000")
    print()
    
    # Wait a moment for app to be ready
    print("Waiting for app to be ready...")
    time.sleep(2)
    
    # Test basic routes
    if test_routes():
        # Test authentication
        test_auth_flow()
    
    print("\n✨ Route testing completed!")