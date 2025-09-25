from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
from datetime import datetime
from app.config import settings
from app.models import ChatRequest, ChatResponse, MemoryResponse, ConfigRequest
from app.chat_service import ChatService
from app.rate_limiter import RateLimiter

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="AI Memory Backend",
    description="Chat backend with evolving memory using Graphiti",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()
rate_limiter = RateLimiter(max_requests_per_minute=settings.max_concurrent_users)

@app.get("/")
async def root():
    return {"message": "AI Memory Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "llm_provider": settings.llm_provider
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not rate_limiter.is_allowed(request.userId):
        wait_time = rate_limiter.get_wait_time(request.userId)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please wait {wait_time:.1f} seconds."
        )
    
    try:
        response = await chat_service.process_chat(request)
        return response
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{user_id}", response_model=MemoryResponse)
async def get_user_memory(user_id: str):
    try:
        stage = chat_service.get_memory_stage(user_id)
        conversation_count = chat_service.graph_manager.count_user_messages(user_id)
        graph_stats = chat_service.graph_manager.get_graph_stats(user_id)
        top_preferences = chat_service.graph_manager.get_user_preferences(user_id)[:5]
        
        return MemoryResponse(
            userId=user_id,
            stage=stage,
            conversationCount=conversation_count,
            graphStats=graph_stats,
            topPreferences=top_preferences
        )
    except Exception as e:
        logger.error("get_memory_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/{user_id}")
async def get_user_config(user_id: str):
    try:
        config = chat_service.get_user_config(user_id)
        return config or {"message": "No custom configuration for this user"}
    except Exception as e:
        logger.error("get_config_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/config/{user_id}")
async def update_user_config(user_id: str, config: ConfigRequest):
    try:
        config_dict = config.dict(exclude_unset=True)
        chat_service.update_user_config(user_id, config_dict)
        return {"message": "Configuration updated successfully", "config": config_dict}
    except Exception as e:
        logger.error("update_config_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)