from typing import List, Dict, Any, Optional
import uuid
import time
import structlog
from app.models import ChatRequest, ChatResponse, MemoryNode
from app.cache_manager import CacheManager
from memory import GraphManager
from memory.keyword_extractor import KeywordExtractor
from memory.recency_manager import RecencyManager
from llm.factory import get_llm_client
from llm.base import LLMConfig

logger = structlog.get_logger()

class ChatService:
    def __init__(self):
        self.graph_manager = GraphManager()
        self.keyword_extractor = KeywordExtractor()
        self.recency_manager = RecencyManager()
        self.cache_manager = CacheManager()
        self.user_configs = {}
        
    def get_memory_stage(self, user_id: str) -> str:
        message_count = self.graph_manager.count_user_messages(user_id)
        if message_count < 5:
            return "Stage 1"
        elif message_count < 15:
            return "Stage 2"
        elif message_count < 30:
            return "Stage 3"
        else:
            return "Stage 4"
            
    def get_memory_for_stage(self, user_id: str, stage: str, current_message: str) -> tuple[List[Dict], List[MemoryNode]]:
        start_time = time.time()
        memory_nodes = []
        memory_used = []
        
        if stage == "Stage 1":
            recent_messages = self.graph_manager.get_user_messages(user_id, limit=5)
            memory_nodes = recent_messages
            memory_used = [
                MemoryNode(
                    nodeId=msg["id"],
                    type="Message",
                    content=msg["content"][:100]
                )
                for msg in recent_messages
            ]
            
        elif stage == "Stage 2":
            recent_messages = self.graph_manager.get_user_messages(user_id, limit=8)
            preferences = self.graph_manager.get_user_preferences(user_id)
            memory_nodes = recent_messages + preferences
            memory_used = [
                MemoryNode(
                    nodeId=msg["id"],
                    type="Message",
                    content=msg["content"][:100]
                )
                for msg in recent_messages[:3]
            ] + [
                MemoryNode(
                    nodeId=pref["id"],
                    type="Preference",
                    content=pref["keyword"],
                    weight=pref["weight"]
                )
                for pref in preferences[:3]
            ]
            
        elif stage == "Stage 3":
            nodes = self.graph_manager.graph_traverse(user_id, max_depth=2, min_weight=0.3)
            nodes_with_decay = self.recency_manager.apply_recency_decay(nodes)
            memory_nodes = nodes_with_decay
            memory_used = [
                MemoryNode(
                    nodeId=node["id"],
                    type=node["type"],
                    content=str(node["data"].get("content", node["data"].get("keyword", "")))[:100],
                    weight=node["data"].get("adjusted_weight", node["data"].get("weight"))
                )
                for node in nodes_with_decay[:5]
            ]
            
        elif stage == "Stage 4":
            nodes = self.graph_manager.contextual_graph_search(user_id, current_message, max_depth=3)
            memory_nodes = nodes
            memory_used = [
                MemoryNode(
                    nodeId=node["id"],
                    type=node["type"],
                    content=str(node["data"].get("content", node["data"].get("keyword", "")))[:100],
                    weight=node.get("score")
                )
                for node in nodes[:5]
            ]
            
        retrieval_time_ms = (time.time() - start_time) * 1000
        logger.info(
            "memory_retrieval",
            user_id=user_id,
            stage=stage,
            nodes_retrieved=len(memory_nodes),
            retrieval_ms=retrieval_time_ms
        )
        
        return memory_nodes, memory_used
        
    def build_prompt_with_memory(self, message: str, memory_nodes: List[Dict], stage: str) -> str:
        prompt_parts = []
        
        if memory_nodes:
            prompt_parts.append("Previous context:")
            for node in memory_nodes[:5]:
                if isinstance(node, dict):
                    if node.get("content"):
                        prompt_parts.append(f"- {node['content']}")
                    elif node.get("keyword"):
                        prompt_parts.append(f"- User likes: {node['keyword']}")
                        
        prompt_parts.append(f"\nCurrent message: {message}")
        prompt_parts.append(f"\n[You are in {stage} of memory evolution]")
        
        return "\n".join(prompt_parts)
        
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.graph_manager.create_user(request.userId)
            
            self.graph_manager.add_message(request.userId, request.message, "user")
            
            keywords_with_counts = self.keyword_extractor.track_user_keywords(
                request.userId, 
                request.message
            )
            for keyword, count in keywords_with_counts.items():
                self.graph_manager.create_preference(
                    request.userId,
                    keyword,
                    weight=count * 0.1
                )
            
            stage = self.get_memory_stage(request.userId)
            memory_nodes, memory_used = self.get_memory_for_stage(
                request.userId, 
                stage, 
                request.message
            )
            
            prompt = self.build_prompt_with_memory(request.message, memory_nodes, stage)
            
            user_config = self.user_configs.get(request.userId, {})
            config_dict = {**user_config, **request.config}
            llm_config = LLMConfig(
                temperature=config_dict.get("temperature", 0.7),
                max_tokens=config_dict.get("maxTokens", 500),
                model=config_dict.get("model"),
                system_prompt=config_dict.get("systemPrompt", "You are a helpful AI assistant with evolving memory capabilities.")
            )
            
            llm_client = get_llm_client()
            llm_response = llm_client.generate(prompt, llm_config)
            
            self.graph_manager.add_message(request.userId, llm_response.content, "assistant")
            
            conversation_count = self.graph_manager.count_user_messages(request.userId)
            
            total_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "chat_completed",
                request_id=request_id,
                user_id=request.userId,
                stage=stage,
                memory_nodes_used=len(memory_used),
                conversation_count=conversation_count,
                total_time_ms=total_time_ms
            )
            
            return ChatResponse(
                response=llm_response.content,
                requestId=request_id,
                stage=stage,
                memoryUsed=memory_used,
                conversationCount=conversation_count
            )
            
        except Exception as e:
            logger.error("chat_error", error=str(e), request_id=request_id)
            raise
            
    def update_user_config(self, user_id: str, config: Dict[str, Any]):
        self.user_configs[user_id] = config
        logger.info("user_config_updated", user_id=user_id)
        
    def get_user_config(self, user_id: str) -> Dict[str, Any]:
        return self.user_configs.get(user_id, {})