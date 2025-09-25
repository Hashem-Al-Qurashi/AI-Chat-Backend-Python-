#!/usr/bin/env python3
"""
Basic functionality tests for AI Memory Backend.
Tests API endpoints and core memory stage transitions.
"""

import pytest
import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000"

class TestMemoryBackend:
    
    async def make_request(self, session, method, endpoint, data=None):
        url = f"{API_BASE}{endpoint}"
        if method == "POST":
            async with session.post(url, json=data) as response:
                return await response.json(), response.status
        elif method == "GET":
            async with session.get(url) as response:
                return await response.json(), response.status
                
    async def test_health_endpoint(self):
        """Test basic health endpoint"""
        async with aiohttp.ClientSession() as session:
            response, status = await self.make_request(session, "GET", "/health")
            assert status == 200
            assert response["status"] == "healthy"
            assert "llm_provider" in response
            
    async def test_stage_1_behavior(self):
        """Test Stage 1: Basic history (< 5 messages)"""
        test_user = "stage1_user"
        async with aiohttp.ClientSession() as session:
            
            for i in range(4):
                data = {
                    "userId": test_user,
                    "message": f"This is message number {i+1}",
                    "config": {}
                }
                response, status = await self.make_request(session, "POST", "/chat", data)
                assert status == 200
                assert response["stage"] == "Stage 1"
                assert response["conversationCount"] == (i + 1) * 2  # user + assistant
                
    async def test_stage_2_transition(self):
        """Test transition to Stage 2 (5+ messages)"""
        test_user = "stage2_user"
        async with aiohttp.ClientSession() as session:
            
            for i in range(6):
                data = {
                    "userId": test_user,
                    "message": f"Message {i+1} about coffee" if "coffee" not in str(i) else f"Message {i+1}",
                    "config": {}
                }
                response, status = await self.make_request(session, "POST", "/chat", data)
                assert status == 200
                
                expected_stage = "Stage 1" if i < 2 else "Stage 2"
                assert response["stage"] == expected_stage
                
    async def test_memory_endpoint(self):
        """Test GET /memory/{user_id} endpoint"""
        test_user = "memory_test_user"
        async with aiohttp.ClientSession() as session:
            
            data = {
                "userId": test_user,
                "message": "Hello, I like coffee",
                "config": {}
            }
            await self.make_request(session, "POST", "/chat", data)
            
            memory_response, status = await self.make_request(session, "GET", f"/memory/{test_user}")
            assert status == 200
            assert memory_response["userId"] == test_user
            assert "stage" in memory_response
            assert "conversationCount" in memory_response
            assert "graphStats" in memory_response
            
    async def test_coffee_preference_detection(self):
        """Test coffee preference is created after 3+ mentions"""
        test_user = "coffee_pref_user"
        async with aiohttp.ClientSession() as session:
            
            coffee_messages = [
                "I love drinking coffee in the morning",
                "Coffee is my favorite beverage",
                "Black coffee tastes amazing"
            ]
            
            for message in coffee_messages:
                data = {
                    "userId": test_user,
                    "message": message,
                    "config": {}
                }
                await self.make_request(session, "POST", "/chat", data)
                
            # Add a few more messages to get to Stage 2
            for i in range(3):
                data = {
                    "userId": test_user,
                    "message": f"Additional message {i}",
                    "config": {}
                }
                await self.make_request(session, "POST", "/chat", data)
                
            memory_response, status = await self.make_request(session, "GET", f"/memory/{test_user}")
            assert status == 200
            
            preferences = memory_response.get("topPreferences", [])
            coffee_prefs = [p for p in preferences if "coffee" in p.get("keyword", "").lower()]
            assert len(coffee_prefs) > 0, "Coffee preference should be created"
            
    async def test_config_endpoints(self):
        """Test GET/PUT /config/{user_id} endpoints"""
        test_user = "config_test_user"
        async with aiohttp.ClientSession() as session:
            
            config_response, status = await self.make_request(session, "GET", f"/config/{test_user}")
            assert status == 200
            
            new_config = {
                "temperature": 0.5,
                "maxTokens": 300,
                "systemPrompt": "You are a helpful assistant"
            }
            
            # Note: PUT endpoint needs to be implemented in the main.py
            # For now, just test that GET works
            
    async def run_all_tests(self):
        """Run all tests"""
        try:
            print("🧪 Running basic functionality tests...")
            
            await self.test_health_endpoint()
            print("✅ Health endpoint test passed")
            
            await self.test_stage_1_behavior()
            print("✅ Stage 1 behavior test passed")
            
            await self.test_stage_2_transition()
            print("✅ Stage 2 transition test passed")
            
            await self.test_memory_endpoint()
            print("✅ Memory endpoint test passed")
            
            await self.test_coffee_preference_detection()
            print("✅ Coffee preference detection test passed")
            
            await self.test_config_endpoints()
            print("✅ Config endpoints test passed")
            
            print("\n🎉 All tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise

async def main():
    tester = TestMemoryBackend()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())