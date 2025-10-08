from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx
import time
import json
import os
import asyncpg
from datetime import datetime
from typing import Optional
import asyncio

app = FastAPI()

# Persistent HTTP client for proxying
http_client = None

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ollama_logs")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
ELECTRICITY_RATE = float(os.getenv("ELECTRICITY_RATE", "0.383"))  # San Diego SDG&E rate $/kWh
M4_MAX_POWER_WATTS = float(os.getenv("M4_MAX_POWER_WATTS", "80"))  # Average power during AI inference

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool():
    """Get or create database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=2,
            max_size=10
        )
    return db_pool

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
    """Log request to PostgreSQL database"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO request_logs (
                    timestamp, ip_address, api_key, model, prompt, response,
                    prompt_tokens, completion_tokens, total_tokens,
                    duration_seconds, power_wh, cost_dollars,
                    http_status, error_message
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            ''', timestamp, ip_address, api_key, model, prompt, response_text,
                 prompt_tokens, completion_tokens, total_tokens,
                 duration_seconds, power_wh, cost_dollars,
                 http_status, error_message)
    except Exception as e:
        print(f"Error logging to database: {e}")

def calculate_cost(duration_seconds: float) -> tuple[float, float]:
    """Calculate power consumption (Wh) and cost ($) based on duration"""
    # Energy = Power × Time
    # Convert watts to kilowatts and seconds to hours
    power_kwh = (M4_MAX_POWER_WATTS * duration_seconds) / 3600000  # kWh
    power_wh = (M4_MAX_POWER_WATTS * duration_seconds) / 3600  # Wh
    cost_dollars = power_kwh * ELECTRICITY_RATE
    return power_wh, cost_dollars

def transform_ollama_to_openai_streaming(ollama_chunk: dict, model: str) -> dict:
    """Transform Ollama streaming chunk to OpenAI format"""
    import uuid
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # Extract content from Ollama format
    content = ""
    finish_reason = None

    if "message" in ollama_chunk:
        content = ollama_chunk["message"].get("content", "")
    elif "response" in ollama_chunk:
        content = ollama_chunk.get("response", "")

    if ollama_chunk.get("done", False):
        finish_reason = "stop"

    # Build OpenAI streaming format
    openai_chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"content": content} if content else {},
                "finish_reason": finish_reason
            }
        ]
    }

    return openai_chunk

def transform_ollama_to_openai_complete(ollama_response: dict, model: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """Transform Ollama complete response to OpenAI format"""
    import uuid
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # Extract content from Ollama format
    content = ""
    if "message" in ollama_response:
        content = ollama_response["message"].get("content", "")
    elif "response" in ollama_response:
        content = ollama_response.get("response", "")

    # Build OpenAI completion format
    openai_response = {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    }

    return openai_response

def transform_models_response(ollama_models: dict) -> dict:
    """Transform Ollama models list to OpenAI format"""
    models_list = []

    if "models" in ollama_models:
        for model in ollama_models["models"]:
            models_list.append({
                "id": model.get("name", "unknown"),
                "object": "model",
                "created": int(time.time()),
                "owned_by": "ollama"
            })

    return {
        "object": "list",
        "data": models_list
    }

@app.on_event("startup")
async def startup():
    """Initialize database connection and HTTP client on startup"""
    global http_client
    http_client = httpx.AsyncClient(timeout=300.0)
    await get_db_pool()
    print(f"Logger started - forwarding to {OLLAMA_URL}")
    print(f"Electricity rate: ${ELECTRICITY_RATE}/kWh (San Diego SDG&E)")
    print(f"M4 Max power consumption: {M4_MAX_POWER_WATTS}W during inference")

@app.on_event("shutdown")
async def shutdown():
    """Close database connection and HTTP client on shutdown"""
    global db_pool, http_client
    if http_client:
        await http_client.aclose()
    if db_pool:
        await db_pool.close()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, path: str):
    """Proxy all requests to Ollama and log everything"""

    # Get request details
    timestamp = datetime.utcnow()
    ip_address = request.client.host
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")

    # Read request body
    body = await request.body()
    body_json = {}
    prompt = ""
    model = ""

    try:
        if body:
            body_json = json.loads(body)
            model = body_json.get("model", "unknown")

            # Extract prompt from different formats
            if "messages" in body_json:
                # Chat completion format
                messages = body_json["messages"]
                if messages and isinstance(messages, list):
                    prompt = messages[-1].get("content", "")
            elif "prompt" in body_json:
                # Completion format
                prompt = body_json["prompt"]
    except:
        pass

    # Start timing
    start_time = time.time()

    # Forward request to Ollama
    url = f"{OLLAMA_URL}/{path}"

    try:
        # Check if streaming is enabled (GET requests are never streaming)
        is_streaming = body_json.get("stream", True) if body_json and request.method == "POST" else False

        if is_streaming:
            # Handle streaming response
            async def stream_and_collect():
                full_response = ""
                response_status = 200

                async with http_client.stream(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=body
                ) as response:
                    response_status = response.status_code

                    async for chunk in response.aiter_bytes():
                        # Collect response text and transform to OpenAI format
                        try:
                            chunk_str = chunk.decode('utf-8')
                            for line in chunk_str.split('\n'):
                                if line.strip():
                                    ollama_chunk = json.loads(line)

                                    # Collect content for logging
                                    if "message" in ollama_chunk:
                                        full_response += ollama_chunk["message"].get("content", "")
                                    elif "response" in ollama_chunk:
                                        full_response += ollama_chunk.get("response", "")

                                    # Transform to OpenAI format
                                    openai_chunk = transform_ollama_to_openai_streaming(ollama_chunk, model)
                                    transformed_line = json.dumps(openai_chunk) + "\n"
                                    yield transformed_line.encode('utf-8')
                        except Exception as e:
                            # If transformation fails, pass through original chunk
                            print(f"Chunk transformation error: {e}")
                            yield chunk

                # Calculate metrics
                end_time = time.time()
                duration_seconds = end_time - start_time
                power_wh, cost_dollars = calculate_cost(duration_seconds)

                # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
                prompt_tokens = len(prompt) // 4
                completion_tokens = len(full_response) // 4
                total_tokens = prompt_tokens + completion_tokens

                # Log to database
                asyncio.create_task(log_request(
                    timestamp=timestamp,
                    ip_address=ip_address,
                    api_key=api_key,
                    model=model,
                    prompt=prompt,
                    response_text=full_response,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    duration_seconds=duration_seconds,
                    power_wh=power_wh,
                    cost_dollars=cost_dollars,
                    http_status=response_status
                ))

            return StreamingResponse(
                stream_and_collect(),
                media_type="application/json"
            )

        else:
            # Handle non-streaming response
            response = await http_client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body
            )

            end_time = time.time()
            duration_seconds = end_time - start_time
            power_wh, cost_dollars = calculate_cost(duration_seconds)

            # Parse response
            response_json = {}
            response_text = ""
            try:
                response_json = response.json()
                if "message" in response_json:
                    response_text = response_json["message"].get("content", "")
                elif "response" in response_json:
                    response_text = response_json.get("response", "")
            except:
                pass

            # Estimate tokens
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(response_text) // 4
            total_tokens = prompt_tokens + completion_tokens

            # Log to database
            await log_request(
                timestamp=timestamp,
                ip_address=ip_address,
                api_key=api_key,
                model=model,
                prompt=prompt,
                response_text=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                duration_seconds=duration_seconds,
                power_wh=power_wh,
                cost_dollars=cost_dollars,
                http_status=response.status_code
            )

            # Transform to OpenAI format based on endpoint
            if path in ["api/chat", "api/generate"]:
                try:
                    openai_response = transform_ollama_to_openai_complete(
                        response_json, model, prompt_tokens, completion_tokens
                    )
                    return Response(
                        content=json.dumps(openai_response),
                        status_code=response.status_code,
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    print(f"Non-streaming transformation error: {e}")
                    # Fall through to original response
            elif path == "api/tags":
                try:
                    openai_response = transform_models_response(response_json)
                    return Response(
                        content=json.dumps(openai_response),
                        status_code=response.status_code,
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    print(f"Models transformation error: {e}")
                    # Fall through to original response

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

    except Exception as e:
        # Log error
        end_time = time.time()
        duration_seconds = end_time - start_time
        power_wh, cost_dollars = calculate_cost(duration_seconds)

        await log_request(
            timestamp=timestamp,
            ip_address=ip_address,
            api_key=api_key,
            model=model,
            prompt=prompt,
            response_text="",
            prompt_tokens=len(prompt) // 4,
            completion_tokens=0,
            total_tokens=len(prompt) // 4,
            duration_seconds=duration_seconds,
            power_wh=power_wh,
            cost_dollars=cost_dollars,
            http_status=500,
            error_message=str(e)
        )

        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ollama-logger"}
