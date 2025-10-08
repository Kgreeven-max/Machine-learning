# API Usage Guide

Complete reference for using the Ollama API Gateway. This API is 100% OpenAI-compatible, so any tool that works with ChatGPT will work with this API.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Format](#requestresponse-format)
5. [Code Examples](#code-examples)
6. [Streaming](#streaming)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)
9. [Best Practices](#best-practices)

## Quick Start

### Base URL

```
https://api.kendall-max.org/v1
```

### Simple Example

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Authentication

All API requests require an API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

### Available API Keys

Configured in your `.env` file:

- **Primary**: `sk-oatisawesome-2024-ml-api`
- **Alternative**: `sk-0at!sAw3s0m3-2024-ml-v2`

### Authentication Errors

**401 Unauthorized** - Invalid or missing API key
```json
{
  "error": "Unauthorized"
}
```

## Endpoints

### 1. Chat Completions

**The main endpoint for conversational AI**

`POST /v1/chat/completions`

**Features:**
- Multi-turn conversations with message history
- Streaming support
- System prompts for behavior control
- Temperature and other parameters

**Request:**
```json
{
  "model": "llama3.1:8b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1696789012,
  "model": "llama3.1:8b",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The capital of France is Paris."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 8,
    "total_tokens": 23
  }
}
```

### 2. Text Completions

**For simple text completion (no conversation context)**

`POST /v1/completions`

**Request:**
```json
{
  "model": "llama3.1:8b",
  "prompt": "Once upon a time in a land far away",
  "max_tokens": 100,
  "temperature": 0.8
}
```

**Response:**
```json
{
  "id": "cmpl-abc123",
  "object": "text_completion",
  "created": 1696789012,
  "model": "llama3.1:8b",
  "choices": [{
    "text": " there lived a brave knight who...",
    "index": 0,
    "finish_reason": "length"
  }],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 100,
    "total_tokens": 109
  }
}
```

### 3. Embeddings

**Generate vector embeddings for text**

`POST /v1/embeddings`

**Request:**
```json
{
  "model": "llama3.1:8b",
  "input": "The quick brown fox jumps over the lazy dog"
}
```

**Response:**
```json
{
  "object": "list",
  "data": [{
    "object": "embedding",
    "embedding": [0.0123, -0.0234, 0.0345, ...],
    "index": 0
  }],
  "model": "llama3.1:8b",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### 4. List Models

**Get available models**

`GET /v1/models`

**Request:**
```bash
curl https://api.kendall-max.org/v1/models \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api"
```

**Response:**
```json
{
  "object": "list",
  "data": [{
    "id": "llama3.1:8b",
    "object": "model",
    "created": 1696789012,
    "owned_by": "ollama"
  }]
}
```

## Request/Response Format

### Message Roles

**system** - Sets the behavior/personality of the assistant
```json
{"role": "system", "content": "You are a helpful coding assistant."}
```

**user** - The user's message
```json
{"role": "user", "content": "Write a Python function to calculate fibonacci"}
```

**assistant** - The AI's response (used for conversation history)
```json
{"role": "assistant", "content": "Here's a fibonacci function..."}
```

### Parameters

**model** (required) - Which model to use
- `llama3.1:8b` (default, recommended)

**messages** (required for chat) - Array of message objects

**temperature** (optional, 0-2, default: 0.7)
- Lower = more focused/deterministic
- Higher = more creative/random

**max_tokens** (optional, default: unlimited)
- Maximum tokens in response
- Note: Context window is 32,768 tokens total

**stream** (optional, boolean, default: true)
- `true` = Stream tokens as they're generated
- `false` = Wait for complete response

**top_p** (optional, 0-1, default: 0.9)
- Nucleus sampling parameter
- Alternative to temperature

**frequency_penalty** (optional, -2 to 2, default: 0)
- Reduce repetition of token sequences

**presence_penalty** (optional, -2 to 2, default: 0)
- Encourage new topics

## Code Examples

### Python

```python
import requests

url = "https://api.kendall-max.org/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-oatisawesome-2024-ml-api",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3.1:8b",
    "messages": [
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(result["choices"][0]["message"]["content"])
```

### Python with Streaming

```python
import requests

url = "https://api.kendall-max.org/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-oatisawesome-2024-ml-api",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Write a story"}],
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)

for line in response.iter_lines():
    if line:
        chunk = line.decode('utf-8')
        if chunk.startswith('data: '):
            import json
            data = json.loads(chunk[6:])
            if data["choices"][0]["delta"].get("content"):
                print(data["choices"][0]["delta"]["content"], end='', flush=True)
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function chat(prompt) {
  const response = await fetch('https://api.kendall-max.org/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer sk-oatisawesome-2024-ml-api',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama3.1:8b',
      messages: [
        { role: 'user', content: prompt }
      ]
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}

// Usage
chat('What is machine learning?').then(console.log);
```

### cURL - Multi-turn Conversation

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [
      {"role": "system", "content": "You are a math tutor."},
      {"role": "user", "content": "What is 15 * 24?"},
      {"role": "assistant", "content": "15 * 24 = 360"},
      {"role": "user", "content": "How did you calculate that?"}
    ]
  }'
```

### OpenAI Python Library

```python
from openai import OpenAI

# Point to your API
client = OpenAI(
    api_key="sk-oatisawesome-2024-ml-api",
    base_url="https://api.kendall-max.org/v1"
}

# Use exactly like OpenAI API
response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

## Streaming

### Why Stream?

- Better user experience (see tokens as they're generated)
- Lower perceived latency
- Essential for long responses

### Streaming Format

When `stream: true`, responses come as Server-Sent Events (SSE):

```
data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"Hello"}}]}

data: {"id":"chatcmpl-123","choices":[{"delta":{"content":" there"}}]}

data: {"id":"chatcmpl-123","choices":[{"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### Python Streaming Example

```python
import requests
import json

url = "https://api.kendall-max.org/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-oatisawesome-2024-ml-api",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Count to 10"}],
    "stream": True
}

with requests.post(url, headers=headers, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: ') and line != 'data: [DONE]':
                chunk_data = json.loads(line[6:])
                content = chunk_data["choices"][0]["delta"].get("content", "")
                if content:
                    print(content, end='', flush=True)
    print()  # New line at end
```

## Error Handling

### HTTP Status Codes

- **200 OK** - Success
- **401 Unauthorized** - Invalid/missing API key
- **404 Not Found** - Invalid endpoint
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error
- **503 Service Unavailable** - Model loading or temporarily unavailable

### Error Response Format

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Handling Errors in Python

```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raises exception for 4xx/5xx
    result = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded, retry after delay")
    else:
        print(f"HTTP Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## Rate Limits

### Current Limits

- **No hard rate limits** currently enforced
- Recommended: 4 concurrent requests max for best performance
- Large batch operations: Add delays between requests

### Best Practices

```python
import time

# For batch processing
for item in items:
    response = make_api_call(item)
    time.sleep(0.5)  # 500ms delay between requests
```

### Future Rate Limits

May be added in future versions:
- Per API key limits
- Per IP limits
- Request queuing

## Best Practices

### 1. Use Streaming for Long Responses

```json
{
  "stream": true,  // Always use for stories, articles, code generation
  "max_tokens": 2000
}
```

### 2. Set Appropriate Temperature

```json
{
  "temperature": 0.1,  // For factual, deterministic responses
  "temperature": 0.7,  // Balanced (default)
  "temperature": 1.5   // For creative writing
}
```

### 3. Provide Context with System Messages

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a senior Python developer. Provide clean, well-documented code."
    },
    {
      "role": "user",
      "content": "Write a function to sort a list"
    }
  ]
}
```

### 4. Handle Long Conversations

Keep track of token count to stay within 32k context window:

```python
def count_tokens(text):
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4

# Truncate old messages if needed
if total_tokens > 30000:
    messages = messages[-10:]  # Keep last 10 messages
```

### 5. Retry Logic

```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

### 6. Cache Responses

For identical requests, cache the response:

```python
import hashlib
import json

cache = {}

def get_cached_response(messages):
    # Create cache key from messages
    key = hashlib.md5(
        json.dumps(messages).encode()
    ).hexdigest()

    if key in cache:
        return cache[key]

    response = make_api_call(messages)
    cache[key] = response
    return response
```

## Advanced Usage

### Function Calling (Coming Soon)

Support for OpenAI-style function calling is planned:

```json
{
  "model": "llama3.1:8b",
  "messages": [...],
  "functions": [{
    "name": "get_weather",
    "description": "Get current weather",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      }
    }
  }]
}
```

### Vision (Future)

Multi-modal support for image analysis:

```json
{
  "model": "llama3.2-vision:11b",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What's in this image?"},
      {"type": "image_url", "image_url": {"url": "..."}}
    ]
  }]
}
```

## Monitoring Your Usage

### Via Dashboard

Access `http://localhost:3000` to see:
- Total requests and tokens
- Costs (electricity)
- Request history
- Search through prompts/responses

### Via Database

```sql
-- Total requests today
SELECT COUNT(*) FROM request_logs
WHERE DATE(timestamp AT TIME ZONE 'America/Los_Angeles') = CURRENT_DATE
AND http_status = 200;

-- Top prompts by token count
SELECT prompt, total_tokens, cost_dollars
FROM request_logs
WHERE http_status = 200
ORDER BY total_tokens DESC
LIMIT 10;

-- Hourly usage
SELECT
  DATE_TRUNC('hour', timestamp) as hour,
  COUNT(*) as requests,
  SUM(total_tokens) as tokens,
  SUM(cost_dollars) as cost
FROM request_logs
WHERE http_status = 200
GROUP BY hour
ORDER BY hour DESC;
```

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review dashboard logs at `http://localhost:3000`
3. Check service logs: `docker-compose logs -f logger`
4. Open an issue on GitHub

---

**Happy coding!** 🚀

For more examples, see the [examples/](examples/) directory in the repository.
