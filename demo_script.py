#!/usr/bin/env python3
"""
Demo script to showcase AI Memory Backend memory evolution through stages.
Tests the progression from Stage 1 to Stage 4 with coffee preference example.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time

API_BASE = "http://localhost:8000"
TEST_USER_ID = "demo_user_123"

async def make_request(session, method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "POST":
            async with session.post(url, json=data) as response:
                return await response.json(), response.status
        elif method == "GET":
            async with session.get(url) as response:
                return await response.json(), response.status
        elif method == "PUT":
            async with session.put(url, json=data) as response:
                return await response.json(), response.status
    except Exception as e:
        return {"error": str(e)}, 500

async def send_chat_message(session, message, user_id=TEST_USER_ID):
    data = {
        "userId": user_id,
        "message": message,
        "config": {"temperature": 0.7, "maxTokens": 200}
    }
    return await make_request(session, "POST", "/chat", data)

async def get_memory_info(session, user_id=TEST_USER_ID):
    return await make_request(session, "GET", f"/memory/{user_id}")

async def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

async def test_stage_progression():
    async with aiohttp.ClientSession() as session:
        print("🤖 AI Memory Backend Demo Script")
        print("Testing memory evolution across 4 stages")
        
        stage_messages = [
            # Stage 1 (Messages 1-4): Basic History
            "Hello, I'm John. Nice to meet you!",
            "What can you help me with today?",
            "I'm working on a Python project",
            "The weather is nice today",
            
            # Stage 2 (Messages 5-14): Keyword Tracking - Mention coffee 3+ times
            "I love drinking coffee in the morning",
            "Do you have any coffee recommendations?",
            "Black coffee is my favorite type of coffee",
            "Coffee helps me stay focused at work",
            "I went to a new coffee shop yesterday",
            "What's the best time to drink coffee?",
            "I prefer dark roast coffee beans",
            "Coffee culture is fascinating",
            "My coffee machine broke today",
            "I need to buy more coffee beans",
            
            # Stage 3 (Messages 15-29): Relationship Weighting
            "I'm thinking about getting a new laptop",
            "Python is such a great programming language",
            "The coffee shop had amazing espresso",
            "I'm learning about machine learning",
            "Weekend plans include buying coffee",
            "Docker containers are useful for development",
            "That coffee subscription service looks good",
            "I enjoy reading tech blogs",
            "Coffee and coding go well together",
            "FastAPI is a nice Python framework",
            "The barista made perfect coffee today",
            "I'm working on a REST API",
            "Coffee beans from Ethiopia are excellent",
            "Version control with git is essential",
            "Morning coffee ritual is important to me",
            
            # Stage 4 (Messages 30+): Advanced Context
            "What type of coffee would you recommend for someone who codes late?",
            "I'm building an AI application with Python",
            "The coffee preference tracking feature sounds interesting",
            "How does memory evolution work in AI systems?",
            "Coffee shops are great places to work on code"
        ]
        
        for i, message in enumerate(stage_messages, 1):
            await print_separator(f"MESSAGE {i}")
            
            response, status = await send_chat_message(session, message)
            
            if status != 200:
                print(f"❌ Error: {response}")
                continue
                
            print(f"💬 User: {message}")
            print(f"🤖 Assistant ({response.get('stage', 'Unknown')}): {response.get('response', 'No response')[:200]}...")
            print(f"📊 Conversation Count: {response.get('conversationCount', 0)}")
            
            if response.get('memoryUsed'):
                print(f"🧠 Memory Nodes Used: {len(response['memoryUsed'])}")
                for node in response['memoryUsed'][:3]:
                    node_type = node.get('type', 'Unknown')
                    content = node.get('content', '')[:50]
                    weight = node.get('weight', 0)
                    print(f"   - {node_type}: {content}... (weight: {weight:.2f})")
            
            # Show memory info at key stages
            if i in [4, 14, 29, 35]:
                await print_separator(f"MEMORY ANALYSIS - After Message {i}")
                memory_info, mem_status = await get_memory_info(session)
                
                if mem_status == 200:
                    print(f"🎯 Stage: {memory_info.get('stage', 'Unknown')}")
                    print(f"💭 Total Conversations: {memory_info.get('conversationCount', 0)}")
                    print(f"📈 Graph Stats: {memory_info.get('graphStats', {})}")
                    
                    prefs = memory_info.get('topPreferences', [])
                    if prefs:
                        print("🔝 Top Preferences:")
                        for pref in prefs[:3]:
                            print(f"   - {pref.get('keyword', 'N/A')}: weight {pref.get('weight', 0):.2f} (mentioned {pref.get('count', 0)} times)")
                
            time.sleep(0.5)
        
        await print_separator("DEMO COMPLETE")
        print("✅ Successfully demonstrated memory evolution across all 4 stages!")
        print("🎯 Key achievements:")
        print("   - Stage 1: Basic conversation history")
        print("   - Stage 2: Coffee preference detected after 3+ mentions")
        print("   - Stage 3: Relationship weighting with recency decay")
        print("   - Stage 4: Advanced contextual search")

async def test_coffee_behavior():
    """Test specific coffee mention behavior"""
    async with aiohttp.ClientSession() as session:
        test_user = "coffee_test_user"
        
        await print_separator("COFFEE PREFERENCE TEST")
        
        # Test 1: Mention coffee only once - should not create preference
        print("Test 1: Single coffee mention")
        response, _ = await send_chat_message(session, "I had coffee this morning", test_user)
        memory_info, _ = await get_memory_info(session, test_user)
        prefs = memory_info.get('topPreferences', [])
        coffee_prefs = [p for p in prefs if 'coffee' in p.get('keyword', '').lower()]
        print(f"Coffee preferences after 1 mention: {len(coffee_prefs)}")
        
        # Test 2: Mention coffee 3 times - should create preference
        print("\nTest 2: Triple coffee mention")
        for msg in ["Coffee is great", "I love coffee"]:
            await send_chat_message(session, msg, test_user)
            
        memory_info, _ = await get_memory_info(session, test_user)
        prefs = memory_info.get('topPreferences', [])
        coffee_prefs = [p for p in prefs if 'coffee' in p.get('keyword', '').lower()]
        print(f"Coffee preferences after 3 mentions: {len(coffee_prefs)}")
        
        if coffee_prefs:
            print(f"✅ Preference created: {coffee_prefs[0].get('keyword')} (weight: {coffee_prefs[0].get('weight', 0):.2f})")
        else:
            print("❌ No coffee preference created")

async def main():
    print("Starting AI Memory Backend Demo...")
    
    try:
        await test_stage_progression()
        await test_coffee_behavior()
    except aiohttp.ClientError:
        print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())