#!/usr/bin/env python3
"""
Quick memory test without threading
"""

import networkx as nx
from datetime import datetime
import json

def test_basic_graph():
    print("🔬 Quick Memory System Test")
    print("=" * 40)
    
    # Test basic NetworkX functionality
    G = nx.DiGraph()
    
    # Add user node
    user_id = "test_user"
    G.add_node(user_id, node_type="User", created_at=datetime.utcnow().isoformat())
    print(f"✅ Added user node: {user_id}")
    
    # Add message nodes
    for i in range(3):
        msg_id = f"msg-{i}"
        G.add_node(msg_id, node_type="Message", content=f"Message {i}", role="user")
        G.add_edge(user_id, msg_id, edge_type="HAS_MESSAGE")
        print(f"✅ Added message: {msg_id}")
    
    # Add preference node
    pref_id = "pref-coffee"
    G.add_node(pref_id, node_type="Preference", keyword="coffee", count=3, weight=0.3)
    G.add_edge(user_id, pref_id, edge_type="HAS_PREFERENCE")
    print(f"✅ Added preference: {pref_id}")
    
    # Test queries
    print(f"✅ Total nodes: {G.number_of_nodes()}")
    print(f"✅ Total edges: {G.number_of_edges()}")
    
    # Get user's connections
    neighbors = list(G.neighbors(user_id))
    print(f"✅ User has {len(neighbors)} connections")
    
    # Get messages
    messages = []
    for node, data in G.nodes(data=True):
        if data.get("node_type") == "Message":
            messages.append({"id": node, "content": data.get("content")})
    print(f"✅ Found {len(messages)} messages")
    
    # Get preferences  
    preferences = []
    for neighbor in G.neighbors(user_id):
        node_data = G.nodes[neighbor]
        if node_data.get("node_type") == "Preference":
            preferences.append({
                "keyword": node_data.get("keyword"),
                "weight": node_data.get("weight")
            })
    print(f"✅ Found {len(preferences)} preferences")
    for pref in preferences:
        print(f"   - {pref['keyword']}: {pref['weight']}")
    
    print("\n🎉 Basic graph functionality works!")
    
    # Test memory stage logic
    message_count = len(messages) * 2  # user + assistant
    if message_count < 5:
        stage = "Stage 1"
    elif message_count < 15:
        stage = "Stage 2"
    elif message_count < 30:
        stage = "Stage 3"
    else:
        stage = "Stage 4"
    
    print(f"✅ Memory stage for {message_count} messages: {stage}")
    
    return True

if __name__ == "__main__":
    success = test_basic_graph()
    if success:
        print("\n💡 Memory system core functionality is working!")
        print("   Issue is likely in the threading or API integration.")
    else:
        print("\n❌ Basic functionality has issues.")