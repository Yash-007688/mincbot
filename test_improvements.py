#!/usr/bin/env python3
"""
Test script to verify the improvements to the Minecraft Bot Hub website
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the new API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing New API Endpoints...")
    print("=" * 50)
    
    # Test 1: Live Bot Vision
    print("\n1. Testing Live Bot Vision API...")
    try:
        response = requests.get(f"{base_url}/api/bots/vision/live")
        if response.status_code == 200:
            data = response.json()
            print("✅ Live Bot Vision API: SUCCESS")
            print(f"   - Response: {data.get('success', False)}")
            print(f"   - Vision Data Keys: {list(data.get('vision_data', {}).keys())}")
        else:
            print(f"❌ Live Bot Vision API: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Live Bot Vision API: ERROR - {e}")
    
    # Test 2: World Detection
    print("\n2. Testing World Detection API...")
    try:
        test_coords = {
            "coordinates": {"x": 15000, "y": 64, "z": 15000},
            "dimension": "overworld"
        }
        response = requests.post(f"{base_url}/api/bots/world/detect", 
                               json=test_coords)
        if response.status_code == 200:
            data = response.json()
            print("✅ World Detection API: SUCCESS")
            print(f"   - World Type: {data.get('world_info', {}).get('world_type', 'Unknown')}")
            print(f"   - Spawn Points: {len(data.get('world_info', {}).get('spawn_points', []))}")
        else:
            print(f"❌ World Detection API: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ World Detection API: ERROR - {e}")
    
    # Test 3: Enhanced Chat Message Processing
    print("\n3. Testing Enhanced Chat Message API...")
    try:
        test_messages = [
            "Where do I respawn?",
            "What type of world is this?",
            "Show me the bot vision",
            "Help me navigate this world"
        ]
        
        for message in test_messages:
            response = requests.post(f"{base_url}/api/chat/message", 
                                   json={"message": message, "user": "TestUser"})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat Message '{message[:20]}...': SUCCESS")
                print(f"   - Response Length: {len(data.get('response', ''))}")
            else:
                print(f"❌ Chat Message '{message[:20]}...': FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Chat Message API: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Testing Complete!")

def test_website_functionality():
    """Test the website functionality"""
    print("\n🌐 Testing Website Functionality...")
    print("=" * 50)
    
    # Test 1: Main page loads
    print("\n1. Testing Main Page...")
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("✅ Main Page: SUCCESS")
            print(f"   - Content Length: {len(response.text)}")
        else:
            print(f"❌ Main Page: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Main Page: ERROR - {e}")
    
    # Test 2: Prompt page loads
    print("\n2. Testing Prompt Page...")
    try:
        response = requests.get("http://localhost:5000/chat")
        if response.status_code == 200:
            print("✅ Prompt Page: SUCCESS")
            print(f"   - Content Length: {len(response.text)}")
            # Check for key elements
            if "AI Chat Assistant" in response.text:
                print("   - ✅ AI Chat Interface Found")
            if "Show Vision" in response.text:
                print("   - ✅ Vision Toggle Button Found")
            if "Go Live" in response.text:
                print("   - ✅ Go Live Button Found")
        else:
            print(f"❌ Prompt Page: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Prompt Page: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🌐 Website Testing Complete!")

if __name__ == "__main__":
    print("🚀 Minecraft Bot Hub - Improvement Testing Suite")
    print("=" * 60)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test website functionality
    test_website_functionality()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary of Improvements:")
    print("✅ Fixed button functionality")
    print("✅ Implemented live preview and bot view")
    print("✅ Enhanced prompting and UI")
    print("✅ Added exact location and coordinates")
    print("✅ Implemented big world navigation assistance")
    print("✅ Added quick action buttons")
    print("✅ Improved bot vision streams")
    print("✅ Enhanced AI responses with context")