#!/bin/bash

echo "🤖 AI Memory Backend Demo Runner"
echo "================================"

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Server not running on localhost:8000"
    echo "Please start the server first:"
    echo "  uvicorn app.main:app --reload"
    exit 1
fi

echo "✅ Server is running"

# Check if required packages are installed
if ! python -c "import aiohttp" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install aiohttp
fi

echo "🚀 Starting demo script..."
echo ""

# Run the demo
python demo_script.py

echo ""
echo "🧪 Running basic tests..."
python test_basic_functionality.py

echo ""
echo "✨ Demo complete!"
echo ""
echo "💡 Next steps:"
echo "  - Check the logs for detailed memory usage"
echo "  - Visit http://localhost:8000/docs for API documentation"
echo "  - Test different user IDs to see memory isolation"
echo "  - Try the /memory/{userId} endpoint to inspect graph state"