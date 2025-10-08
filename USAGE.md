# Ollama API - Usage Guide

## 🚀 Quick Start

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down
```

## 📊 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Endpoint** | `http://localhost:8080/v1` | Bearer token (see below) |
| **Dashboard** | http://localhost:3000 | No login required |
| **pgAdmin** | http://localhost:5050 | admin@localhost.com / admin |
| **PostgreSQL** | localhost:5433 | postgres / postgres / ollama_logs |

## 🔑 API Keys

```bash
Primary: sk-oatisawesome-2024-ml-api
```

## 🌐 Public Access

Your friend uses this endpoint:
```
https://api.kendall-max.org/v1/chat/completions
```

## 📈 Dashboard Features

Open http://localhost:3000 to see:

- ✅ **Real-time Stats**: Total requests, tokens, power consumption, cost
- ✅ **Charts**: Hourly usage and cost trends
- ✅ **Search**: Find any prompt or response
- ✅ **Auto-refresh**: Updates every 30 seconds

## 💰 Cost Tracking

**San Diego SDG&E Rate**: $0.383/kWh

**Formula:**
```
Energy (kWh) = (80W × duration_seconds) / 3600000
Cost ($) = Energy × $0.383
```

**Example:**
- 100-token response in 1 second
- Power: 80W × 1s = 0.022 Wh
- Cost: $0.0000085 (less than a penny!)

## 🗄️ Database Access

### Using pgAdmin (Web UI):

1. Open http://localhost:5050
2. Login: `admin@localhost.com` / `admin`
3. Add Server:
   - Name: `Ollama Logs`
   - Host: `postgres` (use container name, not localhost!)
   - Port: `5432` (internal port)
   - Username: `postgres`
   - Password: `postgres`
   - Database: `ollama_logs`

### Using psql (Command Line):

```bash
# Connect to database
docker exec -it ollama-postgres psql -U postgres -d ollama_logs

# View recent requests
SELECT id, timestamp, LEFT(prompt, 50) as prompt, total_tokens, cost_dollars
FROM request_logs
ORDER BY timestamp DESC
LIMIT 10;

# Total cost today
SELECT SUM(cost_dollars) as total_cost
FROM request_logs
WHERE DATE(timestamp) = CURRENT_DATE;
```

## 📁 Database Schema

**Main Table: `request_logs`**

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-increment ID |
| timestamp | TIMESTAMP | When request was made |
| ip_address | VARCHAR(45) | Client IP address |
| api_key | VARCHAR(255) | API key used |
| model | VARCHAR(100) | Model name (llama3.1:8b) |
| prompt | TEXT | Full user prompt |
| response | TEXT | Full AI response |
| prompt_tokens | INTEGER | Tokens in prompt |
| completion_tokens | INTEGER | Tokens in response |
| total_tokens | INTEGER | Total tokens |
| duration_seconds | REAL | How long it took |
| power_wh | REAL | Power consumed (Wh) |
| cost_dollars | REAL | Cost in dollars |
| http_status | INTEGER | 200, 401, 500, etc. |
| error_message | TEXT | Error if failed |

## 🔍 Example Queries

### Top 10 most expensive requests:
```sql
SELECT
    timestamp,
    LEFT(prompt, 50) as prompt,
    total_tokens,
    cost_dollars,
    duration_seconds
FROM request_logs
ORDER BY cost_dollars DESC
LIMIT 10;
```

### Daily cost breakdown:
```sql
SELECT
    DATE(timestamp) as date,
    COUNT(*) as requests,
    SUM(total_tokens) as tokens,
    SUM(power_wh) as power_wh,
    SUM(cost_dollars) as cost
FROM request_logs
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Search for specific prompts:
```sql
SELECT id, timestamp, prompt, response
FROM request_logs
WHERE prompt ILIKE '%translate%'
ORDER BY timestamp DESC;
```

## 🔧 Maintenance

### View container status:
```bash
docker-compose ps
```

### View logs:
```bash
# All containers
docker-compose logs -f

# Specific container
docker logs ollama-logger -f
docker logs ollama-dashboard -f
docker logs ollama-postgres -f
```

### Restart containers:
```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart logger
```

### Clear all logs (DANGER!):
```bash
# Stop containers
docker-compose down

# Delete database volume (THIS DELETES ALL LOGS!)
docker volume rm publickml_postgres_data

# Start fresh
docker-compose up -d
```

## 📊 Performance Stats

**M4 Max Performance:**
- **Speed**: 96-100 tokens/second
- **Power**: 80W during inference, 3.5W idle
- **Context**: 32,768 tokens (8x ChatGPT)
- **Model**: Llama 3.1 8B (91% accuracy)

**Cost Examples:**
- 10-word response: $0.00001 (0.001 cents)
- 100-word response: $0.00008 (0.008 cents)
- 1000 requests/day (100 words each): $0.08/day = $2.40/month

## ✅ Testing

```bash
# Test local API
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Check if it was logged
curl "http://localhost:3000/api/logs/recent?limit=1"

# Get stats
curl "http://localhost:3000/api/stats/overview?period=today"
```

## 🎯 For Your Friend

Your friend doesn't need to know ANY of this!

He just needs:
- **URL**: `https://api.kendall-max.org/v1/chat/completions`
- **API Key**: `sk-oatisawesome-2024-ml-api`
- **Model**: `llama3.1:8b`

See `FRIEND-SETUP.md` for his instructions.

## 🛡️ Privacy

**✅ Everything stays local:**
- Database stored on your Mac
- Logs never leave your machine
- No external tracking
- Your friend's prompts are private (only you can see them)

**⚠️ You can see:**
- Every prompt he sends
- Every response he gets
- When he uses it
- How much it costs you

## 📞 Troubleshooting

**Dashboard shows "Internal Server Error":**
```bash
# Check if table exists
docker exec ollama-postgres psql -U postgres -d ollama_logs -c "\dt"

# If table is missing, create it
docker exec ollama-postgres psql -U postgres -d ollama_logs -f /docker-entrypoint-initdb.d/init.sql
```

**No logs appearing:**
```bash
# Check logger is running
docker logs ollama-logger --tail 50

# Test logger directly
curl http://localhost:8000/health
```

**Can't connect to pgAdmin:**
```bash
# Restart pgAdmin
docker-compose restart pgadmin

# Check logs
docker logs ollama-pgadmin
```
