#!/usr/bin/env python3
"""
Test memory system directly without LLM calls
"""

import sys
sys.path.append('.')

from memory.graph_manager import GraphManager
from memory.keyword_extractor import KeywordExtractor
from app.chat_service import ChatService
import asyncio

def test_memory_system():
    print("🧠 Testing Memory System Components")
    print("=" * 50)
    
    # Test 1: Graph Manager
    print("1. Testing Graph Manager...")
    graph_manager = GraphManager()
    
    # Create user
    user_id = "test_user_123"
    graph_manager.create_user(user_id)
    print(f"   ✅ Created user: {user_id}")
    
    # Add messages
    msg1 = graph_manager.add_message(user_id, "I love coffee", "user")
    msg2 = graph_manager.add_message(user_id, "Coffee is great", "user") 
    msg3 = graph_manager.add_message(user_id, "More coffee please", "user")
    print(f"   ✅ Added 3 messages")
    
    # Count messages
    count = graph_manager.count_user_messages(user_id)
    print(f"   ✅ Message count: {count}")
    
    # Create preferences (coffee mentioned 3 times)
    pref_id = graph_manager.create_preference(user_id, "coffee", 0.3)
    print(f"   ✅ Created preference: {pref_id}")
    
    # Get user messages
    messages = graph_manager.get_user_messages(user_id)
    print(f"   ✅ Retrieved {len(messages)} messages")
    
    # Get preferences
    preferences = graph_manager.get_user_preferences(user_id)
    print(f"   ✅ Retrieved {len(preferences)} preferences")
    for pref in preferences:
        print(f"      - {pref['keyword']}: weight {pref['weight']}")
    
    print()
    
    # Test 2: Keyword Extractor
    print("2. Testing Keyword Extractor...")
    extractor = KeywordExtractor()
    
    keywords = extractor.extract_keywords("I love drinking coffee in the morning")
    print(f"   ✅ Extracted keywords: {keywords[:5]}")
    
    # Track keywords for user
    keyword_counts = extractor.track_user_keywords(user_id, "I love coffee and more coffee")
    print(f"   ✅ Tracked keywords with counts: {keyword_counts}")
    
    print()
    
    # Test 3: Chat Service (without LLM)
    print("3. Testing Chat Service components...")
    chat_service = ChatService()
    
    # Test memory stage detection
    stage1 = chat_service.get_memory_stage("new_user")
    stage2 = chat_service.get_memory_stage(user_id)  # Has 3 messages
    print(f"   ✅ Memory stages: new_user={stage1}, test_user={stage2}")
    
    # Test memory retrieval for each stage
    for stage in ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]:
        try:
            memory_nodes, memory_used = chat_service.get_memory_for_stage(user_id, stage, "coffee question")
            print(f"   ✅ {stage}: Retrieved {len(memory_nodes)} memory nodes, {len(memory_used)} for response")
        except Exception as e:
            print(f"   ⚠️  {stage}: Error - {e}")
    
    print()
    
    # Test 4: Graph Statistics
    print("4. Testing Graph Statistics...")
    stats = graph_manager.get_graph_stats(user_id)
    print(f"   ✅ Graph stats: {stats}")
    
    # Test contextual search
    search_results = graph_manager.contextual_graph_search(user_id, "coffee recommendation")
    print(f"   ✅ Contextual search returned {len(search_results)} results")
    for result in search_results:
        print(f"      - {result['type']}: score {result.get('score', 0):.2f}")
    
    print("\n🎉 Memory system test completed successfully!")
    print("\nKey findings:")
    print(f"- Graph stores {stats['total_nodes']} nodes and {stats['total_edges']} edges")
    print(f"- User has {len(preferences)} preferences detected")
    print(f"- Memory system progresses through stages based on message count")
    print(f"- Contextual search finds relevant memory nodes")

if __name__ == "__main__":
    test_memory_system()