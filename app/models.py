from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    userId: str
    message: str
    config: Optional[Dict[str, Any]] = {}

class MemoryNode(BaseModel):
    nodeId: str
    type: str
    content: Optional[str] = None
    weight: Optional[float] = None
    
class ChatResponse(BaseModel):
    response: str
    requestId: str
    stage: str
    memoryUsed: List[MemoryNode]
    conversationCount: int
    
class MemoryResponse(BaseModel):
    userId: str
    stage: str
    conversationCount: int
    graphStats: Dict[str, int]
    topPreferences: List[Dict[str, Any]]
    
class ConfigRequest(BaseModel):
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = 500
    model: Optional[str] = None
    systemPrompt: Optional[str] = None