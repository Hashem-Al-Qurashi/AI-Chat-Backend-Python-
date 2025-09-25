#!/bin/bash

echo "🧪 Manual API Testing Commands"
echo "================================"

API_BASE="http://localhost:8001"

echo ""
echo "1. Test Health:"
echo "curl '$API_BASE/health'"
echo ""

echo "2. Test Memory (empty user):"
echo "curl '$API_BASE/memory/test_user'"
echo ""

echo "3. Test Config GET:"
echo "curl '$API_BASE/config/test_user'"
echo ""

echo "4. Test Config PUT:"
echo "curl -X PUT '$API_BASE/config/test_user' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"temperature\": 0.8, \"maxTokens\": 400}'"
echo ""

echo "5. Test Chat (requires API keys):"
echo "curl -X POST '$API_BASE/chat' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"userId\": \"demo_user\","
echo "    \"message\": \"Hello, I love coffee!\","
echo "    \"config\": {\"temperature\": 0.7}"
echo "  }'"
echo ""

echo "6. Check memory after chat:"
echo "curl '$API_BASE/memory/demo_user'"

echo ""
echo "💡 TIP: Visit http://localhost:8001/docs for interactive testing!"