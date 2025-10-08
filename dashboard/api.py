from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ollama_logs")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Timezone configuration
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

def utc_to_pacific(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to Pacific Time"""
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone info
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(PACIFIC_TZ)

def format_timestamp(dt: datetime) -> str:
    """Format timestamp in Pacific Time"""
    pacific_dt = utc_to_pacific(dt)
    return pacific_dt.isoformat()

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

@app.on_event("startup")
async def startup():
    """Initialize database connection on startup"""
    await get_db_pool()
    print(f"Dashboard API started")

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    global db_pool
    if db_pool:
        await db_pool.close()

@app.get("/")
async def read_root():
    """Serve the main dashboard HTML"""
    return FileResponse("index.html")

@app.get("/api/stats/overview")
async def get_overview_stats(
    period: str = Query("today", regex="^(today|week|month|year|all)$")
):
    """Get overview statistics for a given period"""
    pool = await get_db_pool()

    # Calculate date range (using Pacific time for "today")
    now_utc = datetime.now(timezone.utc)
    now_pacific = now_utc.astimezone(PACIFIC_TZ)

    if period == "today":
        # Start of today in Pacific time, converted back to UTC for query
        start_date = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).replace(tzinfo=None)
    elif period == "week":
        start_date = now_utc - timedelta(days=7)
        start_date = start_date.replace(tzinfo=None)
    elif period == "month":
        start_date = now_utc - timedelta(days=30)
        start_date = start_date.replace(tzinfo=None)
    elif period == "year":
        start_date = now_utc - timedelta(days=365)
        start_date = start_date.replace(tzinfo=None)
    else:  # all
        start_date = datetime(2000, 1, 1)

    async with pool.acquire() as conn:
        stats = await conn.fetchrow('''
            SELECT
                COUNT(*) as total_requests,
                SUM(total_tokens) as total_tokens,
                SUM(duration_seconds) as total_duration_seconds,
                SUM(power_wh) as total_power_wh,
                SUM(cost_dollars) as total_cost_dollars,
                AVG(duration_seconds) as avg_duration_seconds,
                AVG(total_tokens) as avg_tokens,
                AVG(cost_dollars) as avg_cost_dollars,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as total_errors
            FROM request_logs
            WHERE timestamp >= $1 AND http_status = 200
        ''', start_date)

        return {
            "period": period,
            "total_requests": stats["total_requests"] or 0,
            "total_tokens": int(stats["total_tokens"] or 0),
            "total_power_wh": round(float(stats["total_power_wh"] or 0), 4),
            "total_power_kwh": round(float(stats["total_power_wh"] or 0) / 1000, 6),
            "total_cost_dollars": round(float(stats["total_cost_dollars"] or 0), 6),
            "avg_duration_seconds": round(float(stats["avg_duration_seconds"] or 0), 2),
            "avg_tokens": round(float(stats["avg_tokens"] or 0), 0),
            "avg_cost_dollars": round(float(stats["avg_cost_dollars"] or 0), 8),
            "total_errors": stats["total_errors"] or 0
        }

@app.get("/api/stats/hourly")
async def get_hourly_stats(hours: int = 24):
    """Get hourly statistics for the last N hours"""
    pool = await get_db_pool()

    now_utc = datetime.now(timezone.utc)
    start_time = (now_utc - timedelta(hours=hours)).replace(tzinfo=None)

    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as total_requests,
                SUM(total_tokens) as total_tokens,
                SUM(power_wh) as total_power_wh,
                SUM(cost_dollars) as total_cost_dollars
            FROM request_logs
            WHERE timestamp >= $1 AND http_status = 200
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour ASC
        ''', start_time)

        return {
            "hours": [
                {
                    "hour": format_timestamp(row["hour"]),
                    "requests": row["total_requests"],
                    "tokens": int(row["total_tokens"] or 0),
                    "power_wh": round(float(row["total_power_wh"] or 0), 4),
                    "cost_dollars": round(float(row["total_cost_dollars"] or 0), 6)
                }
                for row in rows
            ]
        }

@app.get("/api/logs/recent")
async def get_recent_logs(limit: int = 50, offset: int = 0):
    """Get recent request logs"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT
                id, timestamp, ip_address, api_key, model,
                LEFT(prompt, 100) as prompt_preview,
                LEFT(response, 100) as response_preview,
                prompt_tokens, completion_tokens, total_tokens,
                duration_seconds, power_wh, cost_dollars,
                http_status, error_message
            FROM request_logs
            WHERE http_status = 200
            ORDER BY timestamp DESC
            LIMIT $1 OFFSET $2
        ''', limit, offset)

        total_count = await conn.fetchval('SELECT COUNT(*) FROM request_logs WHERE http_status = 200')

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": row["id"],
                    "timestamp": format_timestamp(row["timestamp"]),
                    "ip_address": row["ip_address"],
                    "api_key": row["api_key"][:20] + "..." if row["api_key"] else None,
                    "model": row["model"],
                    "prompt_preview": row["prompt_preview"],
                    "response_preview": row["response_preview"],
                    "prompt_tokens": row["prompt_tokens"],
                    "completion_tokens": row["completion_tokens"],
                    "total_tokens": row["total_tokens"],
                    "duration_seconds": round(float(row["duration_seconds"]), 2),
                    "power_wh": round(float(row["power_wh"]), 4),
                    "cost_dollars": round(float(row["cost_dollars"]), 6),
                    "http_status": row["http_status"],
                    "error": row["error_message"]
                }
                for row in rows
            ]
        }

@app.get("/api/logs/{log_id}")
async def get_log_detail(log_id: int):
    """Get full details of a specific log entry"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow('''
            SELECT * FROM request_logs WHERE id = $1
        ''', log_id)

        if not row:
            return {"error": "Log not found"}

        return {
            "id": row["id"],
            "timestamp": format_timestamp(row["timestamp"]),
            "ip_address": row["ip_address"],
            "api_key": row["api_key"],
            "model": row["model"],
            "prompt": row["prompt"],
            "response": row["response"],
            "prompt_tokens": row["prompt_tokens"],
            "completion_tokens": row["completion_tokens"],
            "total_tokens": row["total_tokens"],
            "duration_seconds": round(float(row["duration_seconds"]), 4),
            "power_wh": round(float(row["power_wh"]), 6),
            "cost_dollars": round(float(row["cost_dollars"]), 8),
            "http_status": row["http_status"],
            "error_message": row["error_message"],
            "created_at": format_timestamp(row["created_at"])
        }

@app.get("/api/search")
async def search_logs(q: str, limit: int = 50):
    """Search logs by prompt or response content"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT
                id, timestamp, model,
                LEFT(prompt, 100) as prompt_preview,
                LEFT(response, 100) as response_preview,
                total_tokens, cost_dollars
            FROM request_logs
            WHERE prompt ILIKE $1 OR response ILIKE $1
            ORDER BY timestamp DESC
            LIMIT $2
        ''', f"%{q}%", limit)

        return {
            "query": q,
            "results": [
                {
                    "id": row["id"],
                    "timestamp": format_timestamp(row["timestamp"]),
                    "model": row["model"],
                    "prompt_preview": row["prompt_preview"],
                    "response_preview": row["response_preview"],
                    "total_tokens": row["total_tokens"],
                    "cost_dollars": round(float(row["cost_dollars"]), 6)
                }
                for row in rows
            ]
        }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ollama-dashboard"}
