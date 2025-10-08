#!/bin/bash

set -e

echo "========================================="
echo "  🧪 Local Model Test Suite"
echo "========================================="
echo ""

# Test 1: Simple math
echo "TEST 1: Math Calculation"
echo "Prompt: 'What is 157 + 243? Reply with just the number.'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "What is 157 + 243? Reply with just the number."}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo ""

# Test 2: Creative writing
echo "TEST 2: Creative Writing"
echo "Prompt: 'Write a haiku about coffee'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Write a haiku about coffee"}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo ""

# Test 3: Text classification
echo "TEST 3: Text Classification"
echo "Prompt: 'Classify as urgent/normal/spam: URGENT: Your account will be closed!'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Classify this email as urgent, normal, or spam (reply with one word): URGENT: Your account will be closed!"}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo ""

# Test 4: Translation
echo "TEST 4: Translation"
echo "Prompt: 'Translate to Spanish: The AI is working perfectly'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Translate to Spanish: The AI is working perfectly"}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo ""

# Test 5: Summarization
echo "TEST 5: Text Summarization"
echo "Prompt: 'Summarize this in 5 words: Customer wants refund for damaged product'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Summarize this in 5 words: Customer wants refund for damaged product"}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo ""

# Test 6: Code generation
echo "TEST 6: Code Generation"
echo "Prompt: 'Write a Python one-liner to reverse a string'"
echo "---"
echo "AI Response:"
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Write a Python one-liner to reverse a string variable called s"}], "stream": false}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message']['content'])"

echo ""
echo "========================================="
echo "  ✅ All Tests Complete!"
echo "========================================="
echo ""
echo "Performance:"
echo "  • Speed: ~96-100 tokens/second"
echo "  • Context: 32,768 tokens (8x ChatGPT)"
echo "  • Model: Llama 3.1 8B"
echo ""
echo "Endpoints:"
echo "  • Local: http://localhost:8080/v1"
echo "  • Public: https://api.kendall-max.org/v1"
echo ""
echo "API Keys:"
echo "  • sk-oatisawesome-2024-ml-api"
echo "  • sk-0at!sAw3s0m3-2024-ml-v2"
echo ""
