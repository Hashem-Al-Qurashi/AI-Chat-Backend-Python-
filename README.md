# AI Memory Backend with Evolving Memory

A FastAPI backend service that provides AI chat capabilities with graph-based memory that evolves through 4 distinct stages based on user interaction history.

## 🚀 Features

- **4-Stage Memory Evolution**: Memory complexity increases as users interact more
- **Graph-based Storage**: Uses NetworkX for efficient memory graph management
- **Multi-LLM Support**: OpenAI and Anthropic integration with fallback mechanisms
- **User Isolation**: Complete separation between user memories and configurations
- **Rate Limiting**: Built-in protection against abuse
- **Structured Logging**: JSON logs with memory usage tracking
- **Docker Ready**: Complete containerization setup

## 📊 Memory Stage Progression

| Stage | Conversation Count | Memory Behavior |
|-------|-------------------|-----------------|
| **Stage 1** | 1-4 messages | Basic conversation history (last 5 messages) |
| **Stage 2** | 5-14 messages | Keyword tracking + preference detection (3+ mentions) |
| **Stage 3** | 15-29 messages | Relationship weighting + recency decay |
| **Stage 4** | 30+ messages | Advanced contextual search + dynamic weight updates |

## 🏗️ Architecture

```
ai_memory_backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── chat_service.py      # Core chat processing logic
│   ├── models.py           # Pydantic models
│   ├── config.py           # Configuration management
│   ├── rate_limiter.py     # Request rate limiting
│   └── cache_manager.py    # LRU caching
├── memory/
│   ├── graph_manager.py    # NetworkX graph operations
│   ├── keyword_extractor.py # Simple keyword extraction
│   └── recency_manager.py  # Time-based weight decay
├── llm/
│   ├── base.py            # Abstract LLM client
│   ├── openai_client.py   # OpenAI integration
│   ├── anthropic_client.py # Anthropic integration
│   └── factory.py         # LLM client factory
└── Docker files, tests, demos...
```

## 🚦 Quick Start

### Option 1: Local Development

1. **Clone and setup**:
```bash
cd ai_memory_backend
python3 -m venv venv
source venv/bin/activate  # or `venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
```

3. **Run the server**:
```bash
uvicorn app.main:app --reload
```

### Option 2: Docker

1. **Using Docker Compose** (recommended):
```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Start services
docker-compose up --build
```

2. **Direct Docker**:
```bash
docker build -t ai-memory-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY="your-key" ai-memory-backend
```

## 📡 API Endpoints

### Chat Endpoint
```bash
POST /chat
{
  "userId": "user123",
  "message": "I love black coffee",
  "config": {
    "temperature": 0.7,
    "maxTokens": 500
  }
}
```

Response:
```json
{
  "response": "I'll remember that you enjoy black coffee!",
  "requestId": "req-uuid",
  "stage": "Stage 2",
  "memoryUsed": [
    {
      "nodeId": "pref-1",
      "type": "Preference", 
      "content": "black coffee",
      "weight": 0.6
    }
  ],
  "conversationCount": 8
}
```

### Memory Inspection
```bash
GET /memory/{userId}
```

### User Configuration
```bash
GET /config/{userId}
PUT /config/{userId}
{
  "temperature": 0.5,
  "maxTokens": 300,
  "systemPrompt": "Custom system prompt"
}
```

## 🧪 Testing & Demo

### Run Demo Script
```bash
# Make sure server is running on localhost:8000
python demo_script.py
```

The demo script will:
- Send 35+ messages showing progression through all 4 stages
- Demonstrate coffee preference detection (3+ mentions)
- Show memory node usage at each stage
- Display graph statistics and top preferences

### Basic Functionality Tests
```bash
python test_basic_functionality.py
```

## 🔍 Memory Evolution Examples

### Stage 1 → Stage 2 Transition
```
Messages 1-4: "Hello", "How are you?", "What's the weather?", "Goodbye"
→ Stage 1: Returns last 5 messages

Message 5: "I love coffee"
→ Stage 2: Now tracks keywords, but coffee mentioned only once

Messages 6-7: "Coffee is great", "More coffee please" 
→ Stage 2: Coffee mentioned 3+ times → Creates preference node with weight 0.3
```

### Stage 2 → Stage 3 Transition
```
Messages 15+: Relationship weighting kicks in
→ Recent mentions of "coffee" get higher weights
→ Old preferences decay over time
→ Graph traversal includes 2-hop neighbors
```

### Stage 4 Advanced Features
```
Messages 30+: "What coffee would you recommend?"
→ Contextual search matches "coffee" with existing preferences
→ Recent coffee mentions boost relevance score (+0.3)
→ High-weight preferences add bonus (+0.2)
→ Dynamic weight updates on each interaction
```

## 🛠️ Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key  
- `LLM_PROVIDER`: "openai" or "anthropic" (default: openai)
- `LOG_LEVEL`: "DEBUG", "INFO", "WARNING", "ERROR" (default: INFO)
- `MAX_CONCURRENT_USERS`: Rate limit per user (default: 10)

### Memory Tuning
Edit these parameters in the respective files:
- **Keyword threshold**: 3+ mentions in `keyword_extractor.py`
- **Preference weights**: `count * 0.1` in `graph_manager.py`
- **Recency decay**: Age-based multipliers in `recency_manager.py`
- **Cache TTL**: 300 seconds in `cache_manager.py`

## 📈 Monitoring & Observability

### Structured Logging
All operations emit JSON logs with:
```json
{
  "requestId": "uuid",
  "userId": "123", 
  "stage": "Stage 2",
  "memoryNodesUsed": [{"nodeId": "n1", "type": "Preference", "weight": 0.8}],
  "retrievalMs": 45,
  "llmMs": 1200,
  "timestamp": "2025-09-25T10:30:00Z"
}
```

### Key Metrics
- Memory retrieval time (target: <200ms)
- Total response time (target: <3s)
- Memory nodes per stage
- Preference creation rate
- Cache hit ratios

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'app'"**
   ```bash
   # Make sure you're in the project root directory
   cd ai_memory_backend
   python -m app.main  # Not just python app/main.py
   ```

2. **LLM API Errors**
   ```bash
   # Check your API keys are set
   echo $OPENAI_API_KEY
   
   # Check the logs for specific errors
   tail -f logs/app.log
   ```

3. **Memory not evolving**
   ```bash
   # Check user message count
   curl http://localhost:8000/memory/your-user-id
   
   # Verify stage transitions in logs
   grep "stage" logs/app.log
   ```

4. **Docker issues**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache
   
   # Check container logs
   docker-compose logs ai-memory-backend
   ```

## 🚀 Production Considerations

### Performance
- Add Redis for persistent caching
- Implement database persistence (PostgreSQL + graph extension)
- Use connection pooling for LLM APIs
- Add request queuing for high load

### Security  
- Add authentication/authorization
- Implement API key management
- Add request signing for webhooks
- Validate and sanitize all inputs

### Scaling
- Horizontal scaling with load balancers
- Separate read/write graph operations
- Implement graph sharding by user_id
- Add metrics collection (Prometheus)

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🤝 Contributing

This is a hackathon proof-of-concept. Key areas for improvement:
- Replace simple keyword extraction with NLP
- Add proper vector embeddings for semantic search
- Implement graph persistence beyond memory
- Add comprehensive test coverage
- Optimize graph traversal algorithms

## 📄 License

MIT License - see LICENSE file for details.

---

Built for the AI Memory Hackathon 🧠✨