# Architecture Documentation

Technical deep-dive into the Ollama API Gateway architecture, design decisions, and implementation details.

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Details](#component-details)
3. [Data Flow](#data-flow)
4. [Database Schema](#database-schema)
5. [Format Transformation](#format-transformation)
6. [Performance Optimizations](#performance-optimizations)
7. [Security](#security)
8. [Scaling Considerations](#scaling-considerations)

## System Overview

###

 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Internet                              │
└────────────────────────────┬─────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Cloudflare CDN  │
                    │   & DDoS Protection
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Cloudflare Tunnel│  (cloudflared)
                    │  Secure WebSocket│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Nginx Proxy    │  Port 80
                    │  - API Key Auth  │
                    │  - CORS          │
                    │  - Rate Limiting │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Logger Middleware│  Port 8000
                    │  - FastAPI       │
                    │  - Ollama→OpenAI │
                    │  - Logging       │
                    └────┬───────┬─────┘
                         │       │
              ┌──────────▼─┐   ┌▼──────────────┐
              │  Ollama    │   │  PostgreSQL   │
              │  llama3.1  │   │  Request Logs │
              │  Port 11434│   │  Port 5432    │
              └────────────┘   └───────┬───────┘
                                       │
                              ┌────────▼─────────┐
                              │ Dashboard API    │  Port 3000
                              │  - FastAPI       │
                              │  - Chart.js UI   │
                              │  - Analytics     │
                              └──────────────────┘
```

### Technology Stack

**Frontend:**
- HTML5 + Vanilla JavaScript
- Chart.js for visualizations
- Server-Sent Events for real-time updates

**Backend:**
- **FastAPI** (Python 3.11) - Logger & Dashboard APIs
- **Nginx** - Reverse proxy and authentication
- **PostgreSQL 16** - Request logging database
- **Ollama** - LLM runtime (llama3.1:8b)

**Infrastructure:**
- **Docker Compose** - Container orchestration
- **Cloudflare Tunnel** - Secure public access
- **pgAdmin** - Database management UI

## Component Details

### 1. Cloudflare Tunnel (cloudflared)

**Purpose:** Securely expose local API to the internet without port forwarding

**How it works:**
1. Creates outbound-only connection to Cloudflare
2. Cloudflare routes `api.kendall-max.org` to tunnel
3. No firewall changes or inbound ports needed

**Configuration:**
```yaml
# cloudflared-config.yml
tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/creds.json

ingress:
  - hostname: api.kendall-max.org
    service: http://nginx:80  # Routes to Nginx inside Docker network
  - service: http_status:404
```

**Docker networking fix for macOS:**
```yaml
# docker-compose.yml
cloudflared:
  extra_hosts:
    - "host.docker.internal:host-gateway"  # Required for Docker Desktop on Mac
```

### 2. Nginx Reverse Proxy

**Purpose:** API gateway, authentication, and request routing

**File:** `nginx/nginx.conf`

**Key Features:**

**A. API Key Validation**
```nginx
# Extract and validate API key
set $api_key "";
if ($http_authorization ~* "Bearer (.+)") {
    set $api_key $1;
}

# Check against allowed keys
set $valid_key 0;
if ($api_key = "sk-oatisawesome-2024-ml-api") {
    set $valid_key 1;
}
if ($api_key = "sk-0at!sAw3s0m3-2024-ml-v2") {
    set $valid_key 1;
}

# Reject invalid keys
if ($valid_key = 0) {
    return 401 '{"error": "Unauthorized"}';
}
```

**B. Endpoint Routing (OpenAI → Ollama)**
```nginx
# Map OpenAI endpoints to Ollama
location /v1/chat/completions {
    rewrite ^/v1/chat/completions$ /api/chat break;
    proxy_pass http://logger:8000;
}

location /v1/completions {
    rewrite ^/v1/completions$ /api/generate break;
    proxy_pass http://logger:8000;
}

location /v1/models {
    rewrite ^/v1/models$ /api/tags break;
    proxy_pass http://logger:8000;
}
```

**C. CORS Headers**
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
```

### 3. Logger Middleware

**Purpose:** Transform Ollama responses to OpenAI format and log all requests

**File:** `logger/app.py`

**Key Components:**

**A. Persistent HTTP Client**
```python
# Module-level client (prevents "client closed" errors during streaming)
http_client = None

@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout

@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()
```

**B. Ollama → OpenAI Transformation**

Streaming responses:
```python
def transform_ollama_to_openai_streaming(ollama_chunk: dict, model: str) -> dict:
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # Extract content from Ollama format
    content = ""
    if "message" in ollama_chunk:
        content = ollama_chunk["message"].get("content", "")
    elif "response" in ollama_chunk:
        content = ollama_chunk.get("response", "")

    finish_reason = "stop" if ollama_chunk.get("done") else None

    # Build OpenAI streaming format
    return {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {"content": content} if content else {},
            "finish_reason": finish_reason
        }]
    }
```

Non-streaming responses:
```python
def transform_ollama_to_openai_complete(ollama_response: dict, model: str,
                                        prompt_tokens: int, completion_tokens: int) -> dict:
    # Extract content
    content = ollama_response.get("message", {}).get("content", "")

    # Build OpenAI completion format
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    }
```

**C. Request Logging**
```python
async def log_request(
    timestamp: datetime,
    ip_address: str,
    api_key: str,
    model: str,
    prompt: str,
    response_text: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    duration_seconds: float,
    power_wh: float,
    cost_dollars: float,
    http_status: int,
    error_message: Optional[str] = None
):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO request_logs (
                timestamp, ip_address, api_key, model, prompt, response,
                prompt_tokens, completion_tokens, total_tokens,
                duration_seconds, power_wh, cost_dollars,
                http_status, error_message
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        ''', ...)
```

**D. Cost Calculation**
```python
def calculate_cost(duration_seconds: float) -> tuple[float, float]:
    """
    Calculate power consumption (Wh) and cost ($) based on duration

    San Diego SDG&E: $0.383/kWh
    M4 Max: 80W during inference
    """
    power_wh = (M4_MAX_POWER_WATTS * duration_seconds) / 3600  # Wh
    power_kwh = power_wh / 1000  # kWh
    cost_dollars = power_kwh * ELECTRICITY_RATE
    return power_wh, cost_dollars
```

### 4. Ollama Runtime

**Purpose:** Run llama3.1:8b model for inference

**Configuration:**
```yaml
# docker-compose.yml
ollama:
  image: ollama/ollama:latest
  platform: linux/arm64  # Important for Apple Silicon
  environment:
    - OLLAMA_HOST=0.0.0.0
    - OLLAMA_ORIGINS=*
    - OLLAMA_NUM_CTX=32768        # 32k context window
    - OLLAMA_NUM_PARALLEL=4        # 4 concurrent requests
    - OLLAMA_MAX_LOADED_MODELS=1   # Keep 1 model in memory
    - OLLAMA_DEBUG=2               # Verbose logging
```

**Performance on M4 Max:**
- 96-100 tokens/second
- First token latency: ~50ms
- Context window: 32,768 tokens
- Memory usage: ~6-8GB for 8B model

### 5. PostgreSQL Database

**Purpose:** Store all request logs for analytics

**File:** `init.sql`

```sql
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    api_key TEXT,
    model VARCHAR(100),
    prompt TEXT,
    response TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    duration_seconds REAL,
    power_wh REAL,
    cost_dollars REAL,
    http_status INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast queries
CREATE INDEX idx_timestamp ON request_logs(timestamp DESC);
CREATE INDEX idx_http_status ON request_logs(http_status);
CREATE INDEX idx_model ON request_logs(model);
```

**Storage estimates:**
- ~1KB per request log
- 10,000 requests ≈ 10MB
- 1 million requests ≈ 1GB

### 6. Dashboard API

**Purpose:** Provide analytics and usage visualization

**File:** `dashboard/api.py`

**Key Features:**

**A. Pacific Timezone Conversion**
```python
from zoneinfo import ZoneInfo

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

def format_timestamp(dt: datetime) -> str:
    """Convert UTC to Pacific Time"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    pacific_dt = dt.astimezone(PACIFIC_TZ)
    return pacific_dt.isoformat()  # Returns: "2024-10-07T22:57:42-07:00"
```

**B. 404 Filtering**
```sql
-- Only show successful requests (hide health checks, errors)
SELECT ... FROM request_logs
WHERE http_status = 200
ORDER BY timestamp DESC
LIMIT 20 OFFSET 0;
```

**C. Pagination**
```python
@app.get("/api/logs/recent")
async def get_recent_logs(limit: int = 50, offset: int = 0):
    # Calculate total pages
    total_count = await conn.fetchval(
        'SELECT COUNT(*) FROM request_logs WHERE http_status = 200'
    )

    # Fetch page
    rows = await conn.fetch('''
        SELECT ... FROM request_logs
        WHERE http_status = 200
        ORDER BY timestamp DESC
        LIMIT $1 OFFSET $2
    ''', limit, offset)

    return {"total": total_count, "logs": [...]}
```

## Data Flow

### Request Flow (Chat Completion)

```
1. Client sends POST request:
   POST https://api.kendall-max.org/v1/chat/completions
   Authorization: Bearer sk-oatisawesome-2024-ml-api
   {
     "model": "llama3.1:8b",
     "messages": [{"role": "user", "content": "Hello"}],
     "stream": true
   }

2. Cloudflare Tunnel forwards to Nginx (http://nginx:80)

3. Nginx validates API key:
   - Extracts Bearer token
   - Checks against allowed keys
   - Returns 401 if invalid

4. Nginx rewrites endpoint:
   /v1/chat/completions → /api/chat

5. Nginx proxies to Logger:
   http://logger:8000/api/chat

6. Logger (FastAPI):
   - Starts timer
   - Extracts prompt from messages
   - Forwards to Ollama: http://ollama:11434/api/chat

7. Ollama generates response (streaming):
   {"message": {"content": "Hello"}, "done": false}
   {"message": {"content": " there"}, "done": false}
   {"message": {"content": "!"}, "done": true}

8. Logger transforms each chunk:
   Ollama: {"message": {"content": "Hello"}}
   ↓
   OpenAI: {
     "id": "chatcmpl-abc123",
     "object": "chat.completion.chunk",
     "choices": [{"delta": {"content": "Hello"}}]
   }

9. Logger streams to client + collects full response

10. When complete, Logger:
    - Calculates duration, tokens, cost
    - Logs to PostgreSQL (asyncio.create_task - non-blocking)
    - Returns final chunk

11. Client receives OpenAI-formatted stream
```

### Dashboard Data Flow

```
1. Browser loads http://localhost:3000/

2. JavaScript makes API calls:
   - GET /api/stats/overview?period=today
   - GET /api/stats/hourly?hours=24
   - GET /api/logs/recent?limit=20&offset=0

3. Dashboard API queries PostgreSQL:
   - Filters WHERE http_status = 200
   - Converts timestamps to Pacific Time
   - Aggregates stats

4. Returns JSON to browser

5. Chart.js renders visualizations

6. Auto-refresh every 30 seconds
```

## Database Schema

### request_logs Table

| Column             | Type      | Description                          |
|--------------------|-----------|--------------------------------------|
| id                 | SERIAL    | Primary key                          |
| timestamp          | TIMESTAMP | Request time (UTC)                   |
| ip_address         | VARCHAR   | Client IP                            |
| api_key            | TEXT      | API key used                         |
| model              | VARCHAR   | Model name (llama3.1:8b)             |
| prompt             | TEXT      | User prompt                          |
| response           | TEXT      | Full AI response                     |
| prompt_tokens      | INTEGER   | Estimated prompt tokens              |
| completion_tokens  | INTEGER   | Estimated completion tokens          |
| total_tokens       | INTEGER   | Total tokens                         |
| duration_seconds   | REAL      | Request duration                     |
| power_wh           | REAL      | Energy consumed (Wh)                 |
| cost_dollars       | REAL      | Cost in USD                          |
| http_status        | INTEGER   | Response status (200, 404, 500, etc) |
| error_message      | TEXT      | Error if failed                      |
| created_at         | TIMESTAMP | Row insert time                      |

## Format Transformation

### Why Transform?

Ollama and OpenAI use different response formats. N8N and other tools expect OpenAI format.

### Format Comparison

**Ollama Chat Response:**
```json
{
  "model": "llama3.1:8b",
  "created_at": "2024-10-07T...",
  "message": {
    "role": "assistant",
    "content": "Hello! How can I help?"
  },
  "done": true
}
```

**OpenAI Chat Response:**
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
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 8,
    "total_tokens": 13
  }
}
```

### Transformation Points

1. **Wrap in `choices` array** - OpenAI uses array, Ollama doesn't
2. **Add `usage` object** - Token counts
3. **Add `id` field** - Unique completion ID
4. **Rename `done` → `finish_reason`** - Different field names
5. **Add `object` type** - "chat.completion" or "chat.completion.chunk"

## Performance Optimizations

### 1. Persistent HTTP Client

**Problem:** Creating new httpx client for each request caused "client closed" errors during streaming.

**Solution:**
```python
# Module-level client lives for entire application
http_client = httpx.AsyncClient(timeout=300.0)
```

### 2. Async Database Logging

**Problem:** Waiting for database writes slows responses.

**Solution:**
```python
# Non-blocking logging
asyncio.create_task(log_request(...))  # Fire and forget
```

### 3. Connection Pooling

**PostgreSQL:**
```python
db_pool = await asyncpg.create_pool(
    min_size=2,
    max_size=10
)
```

### 4. Nginx Buffering

```nginx
# Disable for streaming
proxy_buffering off;
proxy_request_buffering off;
```

### 5. Docker Resource Limits

```yaml
ollama:
  deploy:
    resources:
      limits:
        memory: 16G
      reservations:
        memory: 8G
```

## Security

### Authentication

**API Key Validation (Nginx):**
- Keys never reach Ollama
- Validated at edge
- Failed auth = no processing

**Environment Variables:**
- API keys in `.env` (not committed)
- `.env` in `.gitignore`

### Network Isolation

**Docker Networks:**
- All services on private `ollama_network`
- Only Nginx and Cloudflared exposed
- Ollama not directly accessible

**Cloudflare Tunnel:**
- No inbound firewall rules needed
- Outbound-only connection
- DDoS protection included

### CORS

```nginx
# Restrictive CORS (can tighten further)
add_header 'Access-Control-Allow-Origin' '*';
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
```

### Secrets Management

- API keys in environment variables
- Cloudflare token in `.env`
- No hardcoded credentials in code

## Scaling Considerations

### Current Limits (M4 Max)

- **4 concurrent requests** max (configured)
- **1 model loaded** for best performance
- **32k context window** total
- **96-100 tokens/sec** throughput

### Horizontal Scaling

To scale beyond one machine:

**1. Load Balancer**
```
Nginx (Load Balancer)
  ├─> Ollama Instance 1 (GPU 1)
  ├─> Ollama Instance 2 (GPU 2)
  └─> Ollama Instance 3 (GPU 3)
```

**2. Shared PostgreSQL**
- Centralized logging database
- All instances log to same DB

**3. Redis for Caching**
- Cache common responses
- Reduce redundant inference

### Vertical Scaling

**Larger Models:**
- llama3.1:70b requires ~48GB RAM
- Slower (10-20 tokens/sec) but more capable

**Multiple Models:**
```python
OLLAMA_MAX_LOADED_MODELS=2  # Load 2 models simultaneously
```

### Cost at Scale

**1,000 requests/day:**
- ~1000 tokens avg per request
- ~10 seconds avg duration
- Power: 10,000 seconds × 80W = 0.222 kWh
- Cost: $0.085/day = $2.55/month

**10,000 requests/day:**
- Cost: $25.50/month

Compare to OpenAI GPT-4:
- 1,000 requests × $0.03 = $30/day = $900/month

---

**Architecture designed for:**
- ✅ High performance (96-100 tok/sec)
- ✅ Low cost ($0.000074/request)
- ✅ Easy deployment (Docker Compose)
- ✅ OpenAI compatibility (N8N, etc.)
- ✅ Privacy (local inference)
- ✅ Observability (full logging + dashboard)

For implementation details, see source code in `logger/` and `dashboard/` directories.
