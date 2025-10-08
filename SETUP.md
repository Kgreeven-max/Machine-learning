# Complete Setup Guide

This guide walks you through setting up the Ollama API Gateway from scratch, including Cloudflare Tunnel configuration, Docker setup, and first-time model installation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Cloudflare Configuration](#cloudflare-configuration)
4. [Environment Configuration](#environment-configuration)
5. [Starting Services](#starting-services)
6. [Model Installation](#model-installation)
7. [Verification](#verification)
8. [Next Steps](#next-steps)

## Prerequisites

### Required Software

**1. Docker Desktop for Mac**
```bash
# Download from: https://www.docker.com/products/docker-desktop/
# Or install via Homebrew:
brew install --cask docker

# Launch Docker Desktop and wait for it to be running
```

**Recommended Docker Settings:**
- **Memory**: 8GB minimum, 16GB recommended
- **CPUs**: 4+ cores
- **Disk**: 50GB+ available space

**2. Git**
```bash
# Check if installed:
git --version

# Install if needed:
brew install git
```

### Required Accounts

**1. Cloudflare Account** (Free tier works)
- Sign up at https://www.cloudflare.com/
- Add your domain (`kendall-max.org`)
- Update nameservers to Cloudflare's

**2. GitHub Account** (Optional - for cloning)
- Sign up at https://github.com/

## Initial Setup

### 1. Clone the Repository

```bash
# Clone to your desired location
git clone https://github.com/Kgreeven-max/Machine-learning.git

# Navigate into the directory
cd Machine-learning
```

### 2. Verify File Structure

```bash
# Should see these key files:
ls -la

# Expected output includes:
# - docker-compose.yml
# - .env (or .env.example)
# - logger/
# - dashboard/
# - nginx/
# - init.sql
```

## Cloudflare Configuration

### Option 1: Automatic Setup (Recommended)

```bash
# Run the setup script
./setup-cloudflare.sh
```

**What it does:**
1. Authenticates with Cloudflare (browser opens)
2. Creates a new tunnel automatically
3. Generates credentials and token
4. Creates DNS record for `api.kendall-max.org`
5. Updates your `.env` file

### Option 2: Manual Setup

**Step 1: Create Cloudflare Tunnel**

1. Go to **Cloudflare Dashboard** → **Networks** → **Tunnels**
2. Click **Create a tunnel**
3. Choose **Cloudflared**
4. Name: `ollama-api-YYYYMMDD` (e.g., `ollama-api-20241007`)
5. Click **Save tunnel**

**Step 2: Get Tunnel Token**

1. In the tunnel overview, copy the **Tunnel Token**
2. It looks like: `eyJhIjoiXXXXX...` (long base64 string)
3. Save it for the next step

**Step 3: Configure Public Hostname**

1. In your tunnel, go to **Public Hostname** tab
2. Click **Add a public hostname**
3. Configure:
   - **Subdomain**: `api`
   - **Domain**: `kendall-max.org`
   - **Service**: `http://nginx:80`
4. Click **Save**

**Step 4: Update .env**

Add the tunnel token to your `.env` file:
```bash
TUNNEL_TOKEN=eyJhIjoiXXXXX...your-token-here
```

## Environment Configuration

### 1. Copy Environment Template

```bash
# If .env doesn't exist, create it:
cp .env.example .env

# Or create from scratch:
touch .env
```

### 2. Configure .env File

Open `.env` in your editor and set these values:

```bash
# ============================================
# Cloudflare Configuration
# ============================================
CLOUDFLARE_API_KEY=your_cloudflare_api_key_here
CLOUDFLARE_DOMAIN=kendall-max.org
TUNNEL_TOKEN=eyJhIjoiXXXXX...your-tunnel-token-here

# ============================================
# API Authentication
# ============================================
# Primary API key (share with friends/N8N)
API_KEY=sk-oatisawesome-2024-ml-api

# Alternative API key
API_KEY_ALT=sk-0at!sAw3s0m3-2024-ml-v2

# ============================================
# Model Configuration
# ============================================
DEFAULT_MODEL=llama3.1:8b
OLLAMA_MODELS=llama3.1:8b

# Max context window (32k tokens - 8x ChatGPT)
OLLAMA_NUM_CTX=32768

# Number of parallel requests
OLLAMA_NUM_PARALLEL=4

# Max loaded models (1 for M4 Max to ensure performance)
OLLAMA_MAX_LOADED_MODELS=1

# ============================================
# Cost Tracking Configuration
# ============================================
# Electricity rate in $/kWh (San Diego SDG&E residential rate)
ELECTRICITY_RATE=0.383

# M4 Max average power consumption during AI inference (watts)
M4_MAX_POWER_WATTS=80
```

### 3. Customize API Keys (Optional but Recommended)

Generate unique API keys for security:

```bash
# Generate a random API key
openssl rand -hex 16

# Example output: 7f9e3a1b4c6d8e2f5a9b3c7d1e4f6a8b

# Use this in your .env:
API_KEY=sk-custom-$(openssl rand -hex 8)
```

## Starting Services

### 1. Start Docker Compose

```bash
# Start all services in background
docker-compose up -d

# View startup logs
docker-compose logs -f
```

**Expected services:**
- `postgres` - PostgreSQL database
- `pgadmin` - Database admin interface
- `ollama` - AI model runtime
- `logger` - Request logging middleware
- `nginx` - API gateway
- `dashboard` - Usage analytics UI
- `cloudflared` - Cloudflare tunnel

### 2. Verify All Containers Started

```bash
# Check container status
docker-compose ps

# All containers should show "Up" or "healthy"
```

**Expected output:**
```
NAME                    STATUS
cloudflare-tunnel       Up
nginx-proxy             Up (healthy)
ollama                  Up (healthy)
ollama-dashboard        Up (healthy)
ollama-logger           Up (healthy)
ollama-pgadmin          Up
ollama-postgres         Up (healthy)
```

### 3. Check Service Health

```bash
# Test Ollama
docker exec ollama ollama list

# Test Nginx (should return 401 without API key)
curl -I http://localhost:8080/health

# Test Logger
curl http://localhost:8000/health

# Test Dashboard
curl http://localhost:3000/health

# Test Cloudflare tunnel
docker-compose logs cloudflared | grep -i "registered"
```

## Model Installation

### 1. Pull llama3.1:8b Model

```bash
# This downloads ~5GB, takes 5-15 minutes depending on connection
docker exec ollama ollama pull llama3.1:8b
```

**Expected output:**
```
pulling manifest
pulling 8eeb52dfb3bb... 100% ▕████████████████████▏ 4.7 GB
pulling 73b313b5552d... 100% ▕████████████████████▏  169 B
pulling 0ba8f0e314b4... 100% ▕████████████████████▏  12 KB
pulling 56bb8bd477a5... 100% ▕████████████████████▏   96 B
pulling 1a4c3c319823... 100% ▕████████████████████▏  485 B
verifying sha256 digest
writing manifest
success
```

### 2. Verify Model Installation

```bash
# List installed models
docker exec ollama ollama list

# Expected output:
# NAME              ID              SIZE      MODIFIED
# llama3.1:8b       42182419e950    4.7 GB    2 minutes ago
```

### 3. Test Model Locally

```bash
# Test a simple prompt
docker exec ollama ollama run llama3.1:8b "Say hello in 5 words"

# Expected output similar to:
# Hello there, nice day today!
```

## Verification

### 1. Test Local API (HTTP)

```bash
# Test via localhost (no auth required)
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 2. Test via Nginx (with API Key)

```bash
# Test via Nginx proxy (requires API key)
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Test"}],
    "stream": false
  }'
```

### 3. Test Public API (via Cloudflare)

```bash
# Test via public URL
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello from the internet!"}],
    "stream": false
  }'
```

**Expected response:**
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
      "content": "Hello! How can I help you today?"
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

### 4. Verify Dashboard

```bash
# Open dashboard in browser
open http://localhost:3000
```

**What to check:**
- ✅ Stats cards showing data (if you've made requests)
- ✅ Hourly chart rendering
- ✅ Recent requests table populated
- ✅ Search box functional
- ✅ Pagination controls visible

### 5. Verify Database

```bash
# Connect to PostgreSQL
docker exec -it ollama-postgres psql -U postgres -d ollama_logs

# Check for logged requests
SELECT count(*) FROM request_logs;

# View recent successful requests
SELECT
  timestamp AT TIME ZONE 'America/Los_Angeles' as pst_time,
  model,
  LEFT(prompt, 50) as prompt,
  total_tokens,
  cost_dollars
FROM request_logs
WHERE http_status = 200
ORDER BY timestamp DESC
LIMIT 5;

# Exit psql
\q
```

## Next Steps

### 1. Configure N8N

See [N8N-COMPLETE-SETUP.md](N8N-COMPLETE-SETUP.md) for detailed N8N configuration.

**Quick version:**
1. Add "OpenAI Chat Model" node in N8N
2. Set Base URL: `https://api.kendall-max.org/v1`
3. Set API Key: `sk-oatisawesome-2024-ml-api`
4. Set Model: `llama3.1:8b`

### 2. Share with Friends

Send them this info:

```
🤖 AI API Access

URL: https://api.kendall-max.org/v1
API Key: sk-oatisawesome-2024-ml-api
Model: llama3.1:8b

For N8N: Use the "OpenAI Chat Model" node with the above settings.
Full guide: https://github.com/Kgreeven-max/Machine-learning/blob/master/N8N-COMPLETE-SETUP.md
```

### 3. Monitor Usage

```bash
# Watch logs in real-time
docker-compose logs -f logger

# View dashboard
open http://localhost:3000

# Check PostgreSQL
open http://localhost:5050  # pgAdmin
```

### 4. Optional: Install Additional Models

```bash
# Smaller, faster model (3B parameters)
docker exec ollama ollama pull llama3.2:3b

# Larger, more capable (70B parameters - requires 48GB+ RAM)
docker exec ollama ollama pull llama3.1:70b

# List all available models at ollama.com/library
```

## Common Issues During Setup

### Docker containers won't start

```bash
# Check Docker Desktop is running
docker ps

# Restart Docker Desktop
# macOS: Click Docker icon > Restart

# View specific container logs
docker-compose logs postgres
docker-compose logs ollama
```

### Cloudflare tunnel shows "unhealthy"

```bash
# Check tunnel logs
docker-compose logs cloudflared

# Common issues:
# 1. Invalid TUNNEL_TOKEN - regenerate in Cloudflare dashboard
# 2. DNS not configured - check Cloudflare DNS tab
# 3. Service URL wrong - should be http://nginx:80
```

### Model download fails

```bash
# Check internet connection
curl -I https://ollama.com

# Check disk space (need 10GB+ free)
df -h

# Try pulling again
docker exec ollama ollama pull llama3.1:8b
```

### Can't access dashboard

```bash
# Check if dashboard is running
docker-compose ps dashboard

# Check logs
docker-compose logs dashboard

# Verify port not in use
lsof -i :3000

# Restart dashboard
docker-compose restart dashboard
```

### API returns 401 Unauthorized

```bash
# Verify .env has correct API key
cat .env | grep API_KEY

# Test with exact key from .env
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer $(grep '^API_KEY=' .env | cut -d'=' -f2)" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "test"}]}'
```

## Security Checklist

Before sharing your API:

- [ ] Changed default API keys in `.env`
- [ ] `.env` file is in `.gitignore` (not committed to Git)
- [ ] Cloudflare tunnel is showing "Healthy"
- [ ] Tested public API works with curl
- [ ] Dashboard is only accessible locally (port 3000)
- [ ] PostgreSQL is only accessible locally (port 5433)
- [ ] Nginx is validating API keys (401 without valid key)

## Backup & Recovery

### Backup Database

```bash
# Backup all request logs
docker exec ollama-postgres pg_dump -U postgres ollama_logs > backup.sql

# Backup to compressed file
docker exec ollama-postgres pg_dump -U postgres ollama_logs | gzip > backup-$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker exec -i ollama-postgres psql -U postgres ollama_logs < backup.sql
```

### Backup .env and configs

```bash
# Create backup directory
mkdir -p backups

# Backup important files
cp .env backups/env-$(date +%Y%m%d)
cp docker-compose.yml backups/
cp nginx/nginx.conf backups/
```

## Performance Tuning

### For M4 Max (96GB RAM)

Recommended `.env` settings:

```bash
# Max context for long conversations
OLLAMA_NUM_CTX=32768

# Parallel requests (4 for M4 Max)
OLLAMA_NUM_PARALLEL=4

# Keep only 1 model loaded for best performance
OLLAMA_MAX_LOADED_MODELS=1

# Enable debug logging
OLLAMA_DEBUG=2
```

### Docker Resource Allocation

Go to **Docker Desktop** → **Settings** → **Resources**:

- **CPUs**: 8-10 cores
- **Memory**: 16GB (out of 96GB)
- **Swap**: 2GB
- **Disk**: 100GB+

## Maintenance

### Weekly Tasks

```bash
# Update Ollama models
docker exec ollama ollama pull llama3.1:8b

# Clean up old Docker images
docker system prune -a

# Backup database
docker exec ollama-postgres pg_dump -U postgres ollama_logs | gzip > weekly-backup.sql.gz
```

### Monthly Tasks

- Review dashboard analytics
- Check disk space usage
- Update Docker images: `docker-compose pull`
- Review and rotate old logs

---

**Setup complete!** 🎉

Your Ollama API Gateway is now running and accessible at `https://api.kendall-max.org`

For API usage examples, see [API-USAGE.md](API-USAGE.md)

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
