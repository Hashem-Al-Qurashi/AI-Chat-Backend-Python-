from datetime import datetime, timedelta
from typing import Dict, Any
import math
import structlog

logger = structlog.get_logger()

class RecencyManager:
    def __init__(self):
        self.decay_factor = 0.95
        self.max_age_days = 30
        
    def calculate_recency_multiplier(self, timestamp_str: str) -> float:
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.utcnow()
            age_hours = (now - timestamp).total_seconds() / 3600
            
            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.95
            elif age_hours < 72:
                return 0.85
            elif age_hours < 168:
                return 0.7
            elif age_hours < 720:
                return 0.5
            else:
                return 0.3
                
        except Exception as e:
            logger.error("recency_calculation_error", error=str(e))
            return 0.5
            
    def apply_recency_decay(self, nodes: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        for node in nodes:
            if isinstance(node, dict):
                data = node.get("data", node)
                
                if "last_seen" in data:
                    timestamp = data["last_seen"]
                elif "timestamp" in data:
                    timestamp = data["timestamp"]
                else:
                    continue
                    
                recency_multiplier = self.calculate_recency_multiplier(timestamp)
                
                if "weight" in data:
                    original_weight = data["weight"]
                    data["adjusted_weight"] = original_weight * recency_multiplier
                    data["recency_multiplier"] = recency_multiplier
                    
                    logger.debug(
                        "recency_applied",
                        original_weight=original_weight,
                        adjusted_weight=data["adjusted_weight"],
                        recency_multiplier=recency_multiplier
                    )
                    
        return nodes
        
    def update_preference_weights_with_decay(self, preferences: list[Dict]) -> list[Dict]:
        updated_preferences = []
        
        for pref in preferences:
            if "last_seen" in pref:
                recency_multiplier = self.calculate_recency_multiplier(pref["last_seen"])
                base_weight = pref.get("count", 1) * 0.1
                adjusted_weight = base_weight * recency_multiplier
                
                pref["weight"] = adjusted_weight
                pref["base_weight"] = base_weight
                pref["recency_multiplier"] = recency_multiplier
                
            updated_preferences.append(pref)
            
        updated_preferences.sort(key=lambda x: x.get("weight", 0), reverse=True)
        return updated_preferences