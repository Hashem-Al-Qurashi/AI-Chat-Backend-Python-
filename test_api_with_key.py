#!/usr/bin/env python3
"""
Test the API with OpenAI key to demonstrate memory evolution
"""

import asyncio
import aiohttp
import json
import time

API_BASE = "http://localhost:8001"

async def test_with_openai_key():
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing AI Memory Backend with OpenAI API")
        print("=" * 60)
        
        user_id = "coffee_test_user"
        
        # Test messages to show memory evolution
        test_messages = [
            # Stage 1 messages (1-4)
            "Hello! I'm testing the AI memory system.",
            "How are you doing today?",
            "I'm working on a project about memory.",
            "This is my fourth message.",
            
            # Stage 2 messages (5-14) - mention coffee 3+ times
            "I really love drinking coffee in the morning.",
            "Coffee helps me stay focused during work.",
            "My favorite type of coffee is dark roast.",
            "Do you have any coffee recommendations?",
            "I usually drink coffee around 9 AM.",
            "Coffee shops are great places to work.",
            "The smell of fresh coffee is amazing.",
            "I prefer coffee over tea any day.",
            "This coffee conversation is interesting.",
            "Coffee culture varies around the world."
        ]
        
        print(f"👤 Testing with user: {user_id}")
        print(f"📝 Sending {len(test_messages)} messages to demonstrate memory evolution")
        print()
        
        for i, message in enumerate(test_messages, 1):
            print(f"💬 Message {i}: {message}")
            
            try:
                # Send chat message
                data = {
                    "userId": user_id,
                    "message": message,
                    "config": {
                        "temperature": 0.7,
                        "maxTokens": 150
                    }
                }
                
                async with session.post(f"{API_BASE}/chat", json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"🤖 AI Response ({result.get('stage', 'Unknown')}):")
                        print(f"   {result.get('response', 'No response')[:100]}...")
                        
                        print(f"📊 Memory Stats:")
                        print(f"   - Conversation Count: {result.get('conversationCount', 0)}")
                        print(f"   - Memory Nodes Used: {len(result.get('memoryUsed', []))}")
                        
                        # Show memory nodes if any
                        memory_nodes = result.get('memoryUsed', [])
                        if memory_nodes:
                            print(f"   - Top Memory Nodes:")
                            for node in memory_nodes[:3]:
                                print(f"     * {node.get('type')}: {(node.get('content', '') or '')[:30]}... (weight: {node.get('weight', 0):.2f})")
                        
                    else:
                        error = await response.json()
                        print(f"❌ Error: {error.get('detail', 'Unknown error')}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
            
            print("-" * 50)
            
            # Wait between messages to see evolution
            if i % 5 == 0:
                print(f"\n🧠 Checking memory state after {i} messages...")
                try:
                    async with session.get(f"{API_BASE}/memory/{user_id}") as response:
                        if response.status == 200:
                            memory = await response.json()
                            print(f"   Stage: {memory.get('stage', 'Unknown')}")
                            print(f"   Graph Stats: {memory.get('graphStats', {})}")
                            prefs = memory.get('topPreferences', [])
                            if prefs:
                                print(f"   Top Preferences:")
                                for pref in prefs[:3]:
                                    print(f"     - {pref.get('keyword', 'N/A')}: {pref.get('weight', 0):.2f} (count: {pref.get('count', 0)})")
                        else:
                            error = await response.json()
                            print(f"   Memory Error: {error.get('detail', 'Unknown')}")
                except Exception as e:
                    print(f"   Memory check failed: {e}")
                print()
            
            # Short delay between messages
            await asyncio.sleep(1)
        
        print("\n🎉 Test complete!")
        print("\n💡 Next steps:")
        print("1. Open frontend.html in your browser")
        print("2. Try the interactive interface")
        print("3. Check the /docs endpoint for API documentation")

if __name__ == "__main__":
    asyncio.run(test_with_openai_key())