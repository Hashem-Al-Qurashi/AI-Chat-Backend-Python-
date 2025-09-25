#!/usr/bin/env python3
"""
Easy test script - just run this!
"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_system():
    print("🧪 Testing AI Memory Backend")
    print("=" * 40)
    
    user_id = "easy_test_user"
    
    # Test messages that will create coffee preference
    messages = [
        "Hello! I'm testing this system.",
        "I really love drinking coffee in the morning.",
        "Coffee helps me stay focused at work.", 
        "My favorite coffee is dark roast.",
        "Do you have any coffee recommendations?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Message {i}: {message}")
        
        try:
            data = {
                "userId": user_id,
                "message": message,
                "config": {"temperature": 0.7, "maxTokens": 150}
            }
            
            response = requests.post(f"{API_BASE}/chat", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 AI ({result.get('stage')}):")
                print(f"   {result.get('response', '')[:100]}...")
                print(f"📊 Conversations: {result.get('conversationCount')}")
                
                # Show memory nodes
                memory_nodes = result.get('memoryUsed', [])
                if memory_nodes:
                    print(f"🧠 Memory nodes used:")
                    for node in memory_nodes[:2]:
                        node_type = node.get('type')
                        content = node.get('content', '')[:30]
                        weight = node.get('weight', 0)
                        print(f"   - {node_type}: {content}... (weight: {weight:.2f})")
                
            elif response.status_code == 429:
                print("⚠️  Rate limit hit - waiting...")
                import time
                time.sleep(5)
                continue
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            
    # Check final memory state
    print("\n🧠 Final Memory State:")
    print("=" * 40)
    try:
        response = requests.get(f"{API_BASE}/memory/{user_id}")
        if response.status_code == 200:
            memory = response.json()
            print(f"🎯 Stage: {memory.get('stage')}")
            print(f"📊 Graph Stats: {memory.get('graphStats')}")
            
            prefs = memory.get('topPreferences', [])
            if prefs:
                print(f"🔝 Preferences detected:")
                for pref in prefs:
                    print(f"   - {pref.get('keyword')}: weight {pref.get('weight'):.2f}, mentions {pref.get('count')}")
            else:
                print("🔝 No preferences yet")
        else:
            print(f"❌ Memory check failed: {response.text}")
    except Exception as e:
        print(f"❌ Memory check error: {e}")
        
    print(f"\n✨ Test complete!")
    print(f"💡 Try opening frontend.html in your browser for visual interface!")

if __name__ == "__main__":
    test_system()