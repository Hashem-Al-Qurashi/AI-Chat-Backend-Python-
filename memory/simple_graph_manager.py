import networkx as nx
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
import structlog

logger = structlog.get_logger()

class SimpleGraphManager:
    """Simplified graph manager without threading locks for testing"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.user_message_counts = defaultdict(int)
        self.preference_counts = defaultdict(lambda: defaultdict(int))
        
    def create_user(self, user_id: str) -> Dict:
        if not self.graph.has_node(user_id):
            self.graph.add_node(
                user_id,
                node_type="User",
                created_at=datetime.utcnow().isoformat()
            )
            logger.info("user_created", user_id=user_id)
        return {"id": user_id, "type": "User"}
            
    def add_message(self, user_id: str, message: str, role: str) -> str:
        self.create_user(user_id)
        
        message_id = f"msg-{user_id}-{self.user_message_counts[user_id]}"
        self.user_message_counts[user_id] += 1
        
        self.graph.add_node(
            message_id,
            node_type="Message",
            content=message,
            role=role,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id
        )
        
        self.graph.add_edge(user_id, message_id, edge_type="HAS_MESSAGE")
        
        logger.info("message_added", user_id=user_id, message_id=message_id, role=role)
        return message_id
            
    def create_preference(self, user_id: str, keyword: str, weight: float = 0.1) -> str:
        pref_id = f"pref-{user_id}-{keyword.replace(' ', '_')}"
        
        if self.graph.has_node(pref_id):
            node_data = self.graph.nodes[pref_id]
            node_data["count"] += 1
            node_data["weight"] = min(1.0, node_data["count"] * 0.1)
            node_data["last_seen"] = datetime.utcnow().isoformat()
        else:
            self.graph.add_node(
                pref_id,
                node_type="Preference",
                keyword=keyword,
                count=1,
                weight=weight,
                first_seen=datetime.utcnow().isoformat(),
                last_seen=datetime.utcnow().isoformat(),
                user_id=user_id
            )
            self.graph.add_edge(user_id, pref_id, edge_type="HAS_PREFERENCE")
            
        logger.info("preference_updated", user_id=user_id, keyword=keyword, pref_id=pref_id)
        return pref_id
            
    def get_user_messages(self, user_id: str, limit: int = 5) -> List[Dict]:
        messages = []
        for node, data in self.graph.nodes(data=True):
            if data.get("node_type") == "Message" and data.get("user_id") == user_id:
                messages.append({
                    "id": node,
                    "content": data.get("content"),
                    "role": data.get("role"),
                    "timestamp": data.get("timestamp")
                })
                
        messages.sort(key=lambda x: x["timestamp"], reverse=True)
        return messages[:limit]
            
    def count_user_messages(self, user_id: str) -> int:
        return self.user_message_counts.get(user_id, 0)
            
    def get_user_preferences(self, user_id: str) -> List[Dict]:
        preferences = []
        if self.graph.has_node(user_id):
            for neighbor in self.graph.neighbors(user_id):
                node_data = self.graph.nodes[neighbor]
                if node_data.get("node_type") == "Preference":
                    preferences.append({
                        "id": neighbor,
                        "keyword": node_data.get("keyword"),
                        "weight": node_data.get("weight"),
                        "count": node_data.get("count"),
                        "last_seen": node_data.get("last_seen")
                    })
                    
        preferences.sort(key=lambda x: x["weight"], reverse=True)
        return preferences
            
    def get_graph_stats(self, user_id: str) -> Dict:
        user_nodes = 0
        user_edges = 0
        
        for node, data in self.graph.nodes(data=True):
            if data.get("user_id") == user_id or node == user_id:
                user_nodes += 1
                
        for u, v in self.graph.edges():
            if u == user_id or (self.graph.has_node(u) and self.graph.nodes[u].get("user_id") == user_id):
                user_edges += 1
                
        return {
            "total_nodes": user_nodes,
            "total_edges": user_edges,
            "message_count": self.user_message_counts.get(user_id, 0)
        }