import requests
import json

API_BASE = "http://127.0.0.1:8001"

print("🧪 Simple API Test")
print("=" * 40)

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Chat endpoint
print("2. Testing chat endpoint...")
try:
    data = {
        "userId": "simple_test_user",
        "message": "Hello! This is a test message.",
        "config": {
            "temperature": 0.7,
            "maxTokens": 100
        }
    }
    
    response = requests.post(f"{API_BASE}/chat", json=data, timeout=30)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Stage: {result.get('stage', 'Unknown')}")
        print(f"   Response: {result.get('response', 'No response')[:100]}...")
        print(f"   Conversation Count: {result.get('conversationCount', 0)}")
    else:
        print(f"   Error Response: {response.text}")
        
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 3: Memory endpoint
print("3. Testing memory endpoint...")
try:
    response = requests.get(f"{API_BASE}/memory/simple_test_user", timeout=5)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   User: {result.get('userId')}")
        print(f"   Stage: {result.get('stage')}")
        print(f"   Graph Stats: {result.get('graphStats')}")
    else:
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   Error: {e}")

print("\n✅ Test complete!")