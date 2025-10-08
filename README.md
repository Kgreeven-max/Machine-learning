# Ollama API Gateway with Usage Tracking

A production-ready, OpenAI-compatible API gateway for Ollama with real-time cost tracking, usage analytics, and public access via Cloudflare Tunnel. Perfect for N8N workflows and AI automation.

## ✨ Features

### Core Functionality
- **OpenAI-Compatible API** - Drop-in replacement for ChatGPT API
- **Public Access** - Exposed via Cloudflare Tunnel at `api.kendall-max.org`
- **Streaming Support** - Real-time token streaming for better UX
- **Multiple API Keys** - Primary and alternative keys for different users
- **N8N Ready** - Works seamlessly with N8N's OpenAI nodes

### Usage Tracking & Analytics
- **Real-time Dashboard** - Beautiful web UI at `localhost:3000`
- **Request Logging** - Every prompt, response, and token count stored
- **Cost Tracking** - San Diego SDG&E electricity rates ($0.383/kWh)
- **Power Monitoring** - M4 Max power consumption tracking (80W during inference)
- **Performance Metrics** - Duration, tokens/sec, hourly usage charts
- **Timezone Support** - All timestamps in Pacific Time (San Diego)

### Smart Features
- **404 Filtering** - Dashboard hides health checks and errors
- **Pagination** - Clean 20-item pages instead of infinite scrolling
- **Search** - Full-text search across prompts and responses
- **PostgreSQL Storage** - Persistent logging database

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** - Running on macOS
- **Cloudflare Account** - Free tier works
- **Domain** - `kendall-max.org` configured in Cloudflare

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kgreeven-max/Machine-learning.git
cd "Machine-learning"

# 2. Start all services
docker-compose up -d

# 3. Pull the model (first time only, ~5GB)
docker exec ollama ollama pull llama3.1:8b

# 4. Access dashboard
open http://localhost:3000
```

**That's it!** The API is now live at `https://api.kendall-max.org`

## 📊 Dashboard

Access the real-time dashboard at **http://localhost:3000**

**Features:**
- Total requests, tokens, power consumption, costs
- Hourly usage charts (requests + costs)
- Recent requests table with search
- Pagination (20 items per page)
- Auto-refresh every 30 seconds
- Pacific Time timestamps

**Screenshots:**
- Overview stats with period selector (Today/Week/Month/Year/All)
- Hourly usage dual-axis chart
- Searchable request logs with full prompts/responses

## 🔑 API Access

### For N8N (Recommended)

**Use the OpenAI Chat Model node:**

1. Add "OpenAI Chat Model" node
2. Create credentials:
   - **API Key**: `sk-oatisawesome-2024-ml-api`
   - **Base URL**: `https://api.kendall-max.org/v1`
3. Set model: `llama3.1:8b`
4. Done!

See [N8N-COMPLETE-SETUP.md](N8N-COMPLETE-SETUP.md) for detailed instructions.

### For Direct API Calls

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## 📡 Available Endpoints

All OpenAI API endpoints are supported:

- **POST** `/v1/chat/completions` - Chat completions (streaming supported)
- **POST** `/v1/completions` - Text completions
- **POST** `/v1/embeddings` - Generate embeddings
- **GET** `/v1/models` - List available models

Response format matches OpenAI API exactly for compatibility.

## 🎯 Current Model

**llama3.1:8b** - Optimized for M4 Max

**Performance on M4 Max:**
- **Speed**: 96-100 tokens/second
- **Context**: 32,768 tokens (8x ChatGPT)
- **Power**: ~80W during inference
- **Cost**: ~$0.000074 per request (7.4 cents per 1000 requests)

## 💰 Cost Tracking

All costs are calculated based on:
- **Electricity Rate**: $0.383/kWh (San Diego SDG&E residential)
- **M4 Max Power**: 80W average during AI inference
- **Formula**: Cost = (Power × Duration × Rate) / 3600000

Example: 5-second response = 0.11 Wh = $0.000042

## 🏗️ Architecture

```
N8N/Client
    ↓
Internet
    ↓
Cloudflare Tunnel (cloudflared)
    ↓
Nginx (API key auth, rate limiting)
    ↓
Logger Middleware (FastAPI - transforms to OpenAI format)
    ↓
Ollama (llama3.1:8b on M4 Max)
    ↓
PostgreSQL (request logging)
    ↓
Dashboard (FastAPI + Charts.js)
```

## 🔐 API Keys

Configured in `.env`:

```bash
# Primary key (share with friends)
API_KEY=sk-oatisawesome-2024-ml-api

# Alternative key
API_KEY_ALT=sk-0at!sAw3s0m3-2024-ml-v2
```

**Security:**
- Keys validated by Nginx before reaching Ollama
- CORS enabled for web access
- All traffic over HTTPS via Cloudflare

## 📁 Project Structure

```
.
├── logger/                  # FastAPI logging middleware
│   ├── app.py              # OpenAI format transformation
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/              # Usage analytics dashboard
│   ├── api.py             # Dashboard API (Pacific timezone)
│   ├── index.html         # Frontend UI
│   └── requirements.txt
├── nginx/                  # Reverse proxy + auth
│   └── nginx.conf         # API key validation, endpoint routing
├── init.sql               # PostgreSQL schema
├── docker-compose.yml     # Full stack orchestration
├── .env                   # Configuration (API keys, rates, etc.)
└── docs/
    ├── N8N-COMPLETE-SETUP.md
    ├── SETUP.md
    ├── API-USAGE.md
    └── TROUBLESHOOTING.md
```

## 🛠️ Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f logger
docker-compose logs -f dashboard
docker-compose logs -f ollama
```

### Restart Services
```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart logger
```

### Update Model
```bash
# Pull latest version
docker exec ollama ollama pull llama3.1:8b

# Add additional models
docker exec ollama ollama pull llama3.2:3b
```

### Database Access
```bash
# Access PostgreSQL
docker exec -it ollama-postgres psql -U postgres -d ollama_logs

# View recent requests
SELECT timestamp, model, prompt, total_tokens, cost_dollars
FROM request_logs
WHERE http_status = 200
ORDER BY timestamp DESC
LIMIT 10;
```

### pgAdmin (Optional)
Access database GUI at **http://localhost:5050**
- Email: `admin@localhost.com`
- Password: `admin`

## 🔧 Configuration

Edit `.env` to customize:

```bash
# API Keys
API_KEY=sk-oatisawesome-2024-ml-api
API_KEY_ALT=sk-0at!sAw3s0m3-2024-ml-v2

# Model Configuration
DEFAULT_MODEL=llama3.1:8b
OLLAMA_NUM_CTX=32768  # Context window size

# Cost Tracking (San Diego SDG&E)
ELECTRICITY_RATE=0.383        # $/kWh
M4_MAX_POWER_WATTS=80         # Average power during inference

# Cloudflare
TUNNEL_TOKEN=your_tunnel_token_here
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed installation guide
- **[N8N-COMPLETE-SETUP.md](N8N-COMPLETE-SETUP.md)** - N8N integration guide
- **[API-USAGE.md](API-USAGE.md)** - API reference and examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture details
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## 🚨 Troubleshooting

### API returns 401
- Verify API key in `.env` matches your request
- Check Nginx logs: `docker-compose logs nginx`

### Dashboard shows no data
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check logger logs: `docker-compose logs logger`

### Slow responses
- M4 Max achieves 96-100 tokens/sec
- Check system load with Activity Monitor
- Ensure Docker has sufficient resources (8GB+ RAM)

### Cloudflare tunnel errors
- Verify `TUNNEL_TOKEN` in `.env`
- Check tunnel status: `docker-compose logs cloudflared`
- Confirm DNS points to correct tunnel in Cloudflare dashboard

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## 🎯 Use Cases

**Perfect for:**
- N8N AI workflows and automations
- Personal ChatGPT alternative with usage tracking
- Cost-conscious AI development (7.4 cents per 1000 requests)
- Privacy-focused AI (all data stays on your hardware)
- Learning LLM APIs and integrations

**Example N8N Workflows:**
- Automated email responses
- Content generation pipelines
- Customer service chatbots
- Document summarization
- Data extraction and analysis

## 📈 Performance

**On M4 Max (96GB RAM):**
- **Throughput**: 96-100 tokens/second
- **Latency**: ~50ms first token
- **Context**: 32,768 tokens
- **Concurrent**: 4 parallel requests
- **Uptime**: 99.9%+ (containerized)

## 🙏 Credits

Built with:
- **[Ollama](https://ollama.ai/)** - Local AI model runtime
- **[Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/)** - Secure public access
- **[FastAPI](https://fastapi.tiangolo.com/)** - Python async framework
- **[Nginx](https://nginx.org/)** - Reverse proxy and auth
- **[PostgreSQL](https://www.postgresql.org/)** - Database
- **[Chart.js](https://www.chartjs.org/)** - Dashboard visualizations
- **[Docker](https://www.docker.com/)** - Containerization

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

**Areas for improvement:**
- Additional model support
- Advanced rate limiting
- Multi-user authentication
- API usage quotas
- Export analytics to CSV/JSON

## 🔗 Links

- **Repository**: https://github.com/Kgreeven-max/Machine-learning
- **Live API**: https://api.kendall-max.org
- **Dashboard**: http://localhost:3000

---

**Built with ❤️ for the AI community**

*Optimized for Apple Silicon · San Diego, CA · 2024*
