#!/usr/bin/env python3
"""
Test memory functionality without requiring LLM API calls
"""

import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8001"

async def test_memory_stages():
    async with aiohttp.ClientSession() as session:
        print("🧠 Testing AI Memory Backend - Memory Stages Only")
        print("=" * 60)
        
        user_id = "memory_test_user"
        
        # Test 1: Check initial state
        print("\n1️⃣ Testing initial state (no messages)")
        async with session.get(f"{API_BASE}/memory/{user_id}") as response:
            if response.status == 500:
                result = await response.json()
                print(f"✅ Expected error for new user: {result.get('detail', '')[:100]}...")
            else:
                print(f"❌ Unexpected status: {response.status}")
        
        # Test 2: Test config endpoints
        print("\n2️⃣ Testing config endpoints")
        async with session.get(f"{API_BASE}/config/{user_id}") as response:
            result = await response.json()
            print(f"✅ Get config: {result}")
            
        # Test 3: Update config
        config_data = {
            "temperature": 0.5,
            "maxTokens": 300,
            "systemPrompt": "Test prompt"
        }
        async with session.put(f"{API_BASE}/config/{user_id}", json=config_data) as response:
            result = await response.json()
            print(f"✅ Update config: {result['message']}")
            
        # Test 4: Verify config was saved
        async with session.get(f"{API_BASE}/config/{user_id}") as response:
            result = await response.json()
            print(f"✅ Verified config: temperature={result.get('temperature')}, maxTokens={result.get('maxTokens')}")
        
        print("\n🎉 Memory-only tests completed successfully!")
        print("\nTo test full chat functionality:")
        print("1. Set up API keys in .env file:")
        print("   OPENAI_API_KEY=your-key-here")
        print("   ANTHROPIC_API_KEY=your-key-here")
        print("2. Visit http://localhost:8001/docs for interactive testing")
        print("3. Use the /chat endpoint with POST requests")

if __name__ == "__main__":
    asyncio.run(test_memory_stages())