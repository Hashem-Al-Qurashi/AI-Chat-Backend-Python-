import networkx as nx
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import structlog
from collections import defaultdict
import threading

logger = structlog.get_logger()

class GraphManager:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.lock = threading.Lock()
        self.user_message_counts = defaultdict(int)
        self.preference_counts = defaultdict(lambda: defaultdict(int))
        
    def create_user(self, user_id: str) -> Dict:
        with self.lock:
            if not self.graph.has_node(user_id):
                self.graph.add_node(
                    user_id,
                    node_type="User",
                    created_at=datetime.utcnow().isoformat()
                )
                logger.info("user_created", user_id=user_id)
            return {"id": user_id, "type": "User"}
            
    def add_message(self, user_id: str, message: str, role: str) -> str:
        with self.lock:
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
            
            logger.info(
                "message_added",
                user_id=user_id,
                message_id=message_id,
                role=role
            )
            
            return message_id
            
    def create_preference(self, user_id: str, keyword: str, weight: float = 0.1) -> str:
        with self.lock:
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
                
            logger.info(
                "preference_updated",
                user_id=user_id,
                keyword=keyword,
                pref_id=pref_id
            )
            
            return pref_id
            
    def get_user_messages(self, user_id: str, limit: int = 5) -> List[Dict]:
        with self.lock:
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
        with self.lock:
            return self.user_message_counts.get(user_id, 0)
            
    def get_user_preferences(self, user_id: str) -> List[Dict]:
        with self.lock:
            preferences = []
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
            
    def graph_traverse(self, user_id: str, max_depth: int = 2, min_weight: float = 0.3) -> List[Dict]:
        with self.lock:
            nodes = []
            visited = set()
            
            def traverse(node, depth):
                if depth > max_depth or node in visited:
                    return
                visited.add(node)
                
                node_data = self.graph.nodes[node]
                if node_data.get("weight", 1.0) >= min_weight:
                    nodes.append({
                        "id": node,
                        "type": node_data.get("node_type"),
                        "data": node_data
                    })
                    
                for neighbor in self.graph.neighbors(node):
                    traverse(neighbor, depth + 1)
                    
            if self.graph.has_node(user_id):
                traverse(user_id, 0)
                
            return nodes
            
    def contextual_graph_search(self, user_id: str, query: str, max_depth: int = 3) -> List[Dict]:
        with self.lock:
            nodes = []
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            for node, data in self.graph.nodes(data=True):
                if data.get("user_id") == user_id or node == user_id:
                    score = 0.0
                    
                    if data.get("node_type") == "Preference":
                        keyword = data.get("keyword", "").lower()
                        if keyword in query_lower:
                            score += 0.5
                            data["count"] = data.get("count", 0) + 1
                            data["weight"] = min(1.0, data["count"] * 0.1)
                            data["last_seen"] = datetime.utcnow().isoformat()
                            
                        timestamp = data.get("last_seen", data.get("first_seen"))
                        if timestamp:
                            age_hours = (datetime.utcnow() - datetime.fromisoformat(timestamp)).total_seconds() / 3600
                            if age_hours < 24:
                                score += 0.3
                                
                        if data.get("weight", 0) > 0.5:
                            score += 0.2
                            
                    elif data.get("node_type") == "Message":
                        content = data.get("content", "").lower()
                        matching_words = sum(1 for word in query_words if word in content)
                        if matching_words > 0:
                            score += 0.3 * (matching_words / len(query_words))
                            
                    if score > 0:
                        nodes.append({
                            "id": node,
                            "type": data.get("node_type"),
                            "score": score,
                            "data": data
                        })
                        
            nodes.sort(key=lambda x: x["score"], reverse=True)
            return nodes[:10]
            
    def get_graph_stats(self, user_id: str) -> Dict:
        with self.lock:
            user_nodes = 0
            user_edges = 0
            
            for node, data in self.graph.nodes(data=True):
                if data.get("user_id") == user_id or node == user_id:
                    user_nodes += 1
                    
            for u, v in self.graph.edges():
                if u == user_id or self.graph.nodes[u].get("user_id") == user_id:
                    user_edges += 1
                    
            return {
                "total_nodes": user_nodes,
                "total_edges": user_edges,
                "message_count": self.user_message_counts.get(user_id, 0)
            }
            
    def track_keyword_mention(self, user_id: str, keyword: str):
        with self.lock:
            self.preference_counts[user_id][keyword.lower()] += 1
            if self.preference_counts[user_id][keyword.lower()] >= 3:
                self.create_preference(user_id, keyword)