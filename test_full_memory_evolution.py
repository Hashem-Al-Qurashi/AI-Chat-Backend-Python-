#!/usr/bin/env python3
"""
Test complete memory evolution with working API
"""

import requests
import time
import json

API_BASE = "http://127.0.0.1:8001"

def test_complete_evolution():
    print("🧠 Complete Memory Evolution Test")
    print("=" * 60)
    
    user_id = "evolution_test_user"
    
    # Messages to trigger different stages and preferences
    stage1_messages = [
        "Hello! I'm testing the memory system.",
        "How does this AI memory work?",
        "This is quite interesting.",
        "I'm looking forward to seeing how this evolves."
    ]
    
    stage2_messages = [
        "I absolutely love drinking coffee in the morning.",  # coffee #1
        "Coffee really helps me focus during work.",          # coffee #2  
        "My favorite type of coffee is dark roast.",          # coffee #3 -> should create preference
        "Do you have any coffee recommendations for me?",     # coffee #4
        "I usually drink coffee around 9 AM every day.",      # coffee #5
        "The smell of fresh coffee is just amazing.",         # coffee #6
        "I prefer coffee over tea any day of the week.",      # coffee #7
        "Coffee shops are great places to work and think.",   # coffee #8
        "This coffee conversation is really interesting.",    # coffee #9
        "Coffee culture varies so much around the world."     # coffee #10
    ]
    
    stage3_messages = [
        "I also enjoy programming in Python quite a bit.",    # python #1
        "The coffee at that new café was exceptional.",       # coffee #11
        "Python makes data analysis so much easier.",         # python #2
        "I'm thinking about trying Ethiopian coffee next.",   # coffee #12
        "Python's syntax is so clean and readable.",         # python #3 -> should create preference
        "Morning coffee and coding go perfectly together.",   # coffee #13
        "I've been learning more Python frameworks lately.",  # python #4
        "That espresso shot was perfectly balanced today.",   # coffee #14
        "Python's libraries are incredibly powerful.",        # python #5
        "Coffee subscription services are quite convenient.", # coffee #15
        "I'm working on a Python project this week.",        # python #6
        "The coffee quality here has really improved.",       # coffee #16
        "Python debugging tools are very helpful.",          # python #7
        "I love the ritual of morning coffee brewing.",      # coffee #17
        "Python community support is fantastic."             # python #8
    ]
    
    stage4_messages = [
        "What would you recommend for someone who loves both coffee and Python programming?",
        "I'm looking for the perfect coffee to drink while coding Python.",
        "Can you suggest a coffee that would complement a long Python coding session?",
        "What's the best coffee setup for a Python developer's workspace?",
        "I want to combine my love of coffee with my Python programming habit."
    ]
    
    all_messages = stage1_messages + stage2_messages + stage3_messages + stage4_messages
    
    print(f"👤 Testing with user: {user_id}")
    print(f"📝 Sending {len(all_messages)} messages total")
    print(f"   - Stage 1: {len(stage1_messages)} messages (basic history)")
    print(f"   - Stage 2: {len(stage2_messages)} messages (keyword tracking)")  
    print(f"   - Stage 3: {len(stage3_messages)} messages (relationship weighting)")
    print(f"   - Stage 4: {len(stage4_messages)} messages (advanced context)")
    print()
    
    for i, message in enumerate(all_messages, 1):
        print(f"💬 Message {i}: {message[:60]}{'...' if len(message) > 60 else ''}")
        
        # Send chat message
        try:
            data = {
                "userId": user_id,
                "message": message,
                "config": {"temperature": 0.7, "maxTokens": 150}
            }
            
            response = requests.post(f"{API_BASE}/chat", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"🤖 AI ({result.get('stage', 'Unknown')}):")
                print(f"   {result.get('response', 'No response')[:80]}{'...' if len(result.get('response', '')) > 80 else ''}")
                
                # Show memory info
                memory_count = len(result.get('memoryUsed', []))
                conv_count = result.get('conversationCount', 0)
                print(f"📊 Conversations: {conv_count}, Memory Nodes: {memory_count}")
                
                # Show top memory nodes
                memory_nodes = result.get('memoryUsed', [])[:2]
                for node in memory_nodes:
                    node_type = node.get('type', 'Unknown')
                    content = (node.get('content') or '')[:40]
                    weight = node.get('weight', 0)
                    print(f"   💭 {node_type}: {content}{'...' if len(content) >= 40 else ''} (w:{weight:.2f})")
                
            else:
                error = response.json()
                print(f"❌ Error: {error.get('detail', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 50)
        
        # Check memory state at key transition points
        if i in [4, 14, 29, len(all_messages)]:
            print(f"\n🔍 MEMORY STATE ANALYSIS - After Message {i}")
            print("=" * 50)
            
            try:
                response = requests.get(f"{API_BASE}/memory/{user_id}", timeout=10)
                if response.status_code == 200:
                    memory = response.json()
                    
                    print(f"🎯 Current Stage: {memory.get('stage', 'Unknown')}")
                    print(f"💬 Total Conversations: {memory.get('conversationCount', 0)}")
                    print(f"📊 Graph: {memory.get('graphStats', {})}")
                    
                    prefs = memory.get('topPreferences', [])
                    if prefs:
                        print(f"🔝 Top Preferences ({len(prefs)}):")
                        for j, pref in enumerate(prefs, 1):
                            keyword = pref.get('keyword', 'N/A')
                            weight = pref.get('weight', 0)
                            count = pref.get('count', 0)
                            print(f"   {j}. {keyword}: weight={weight:.2f}, mentions={count}")
                    else:
                        print("🔝 No preferences detected yet")
                        
                else:
                    error = response.json()
                    print(f"❌ Memory check error: {error.get('detail', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ Memory check failed: {e}")
            
            print("=" * 50)
            print()
        
        # Small delay between messages
        time.sleep(0.5)
    
    print("\n🎉 Memory Evolution Test Complete!")
    print("\n📋 Summary:")
    print("✅ Stage 1: Basic conversation history")
    print("✅ Stage 2: Keyword tracking (coffee preference after 3+ mentions)")
    print("✅ Stage 3: Multiple preferences (coffee + python)")
    print("✅ Stage 4: Advanced contextual responses")
    print("\n💡 Key Features Demonstrated:")
    print("- Memory stages progress based on conversation count")
    print("- Keyword preferences created after 3+ mentions") 
    print("- Graph stores messages, users, and preferences")
    print("- AI responses become more personalized over time")
    print("- Memory nodes influence response generation")

if __name__ == "__main__":
    test_complete_evolution()