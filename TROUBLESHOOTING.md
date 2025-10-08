# Troubleshooting Guide

Common issues, error messages, and their solutions. Use this guide when something isn't working as expected.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [API Issues](#api-issues)
3. [Docker & Container Issues](#docker--container-issues)
4. [Cloudflare Tunnel Issues](#cloudflare-tunnel-issues)
5. [Database Issues](#database-issues)
6. [Dashboard Issues](#dashboard-issues)
7. [Model Issues](#model-issues)
8. [Performance Issues](#performance-issues)
9. [N8N Integration Issues](#n8n-integration-issues)

## Quick Diagnostics

### Check All Services

```bash
# View status of all containers
docker-compose ps

# Should see all containers "Up" or "healthy"
```

### Run Health Checks

```bash
# 1. Test Ollama
docker exec ollama ollama list

# 2. Test Nginx (should return 401 without key)
curl -I http://localhost:8080/v1/models

# 3. Test Logger
curl http://localhost:8000/health

# 4. Test Dashboard
curl http://localhost:3000/health

# 5. Test public API
curl https://api.kendall-max.org/health
```

### View Logs

```bash
# All services
docker-compose logs --tail=50

# Specific service
docker-compose logs -f logger
docker-compose logs -f ollama
docker-compose logs -f cloudflared
docker-compose logs -f nginx
```

## API Issues

### Issue: API Returns 401 Unauthorized

**Symptoms:**
```json
{
  "error": "Unauthorized"
}
```

**Causes & Solutions:**

**1. Invalid API Key**
```bash
# Check your .env file
cat .env | grep API_KEY

# Verify you're using the exact key
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "test"}]}'
```

**2. Missing Authorization Header**
```bash
# Must include: Authorization: Bearer YOUR_KEY
# Wrong: -H "API-Key: sk-..."
# Correct: -H "Authorization: Bearer sk-..."
```

**3. Nginx not started**
```bash
# Check nginx status
docker-compose ps nginx

# Restart nginx
docker-compose restart nginx
```

### Issue: API Returns 404 Not Found

**Symptoms:**
```
404 Not Found
```

**Causes & Solutions:**

**1. Wrong Endpoint**
```bash
# Wrong: /api/chat/completions
# Correct: /v1/chat/completions

# Wrong: /chat/completions
# Correct: /v1/chat/completions
```

**2. Nginx Configuration Error**
```bash
# Check nginx config syntax
docker exec nginx-proxy nginx -t

# View nginx logs
docker-compose logs nginx | grep -i error
```

### Issue: API Timeout or No Response

**Symptoms:**
- Request hangs for minutes
- Eventually times out
- No response returned

**Causes & Solutions:**

**1. Ollama Not Running**
```bash
# Check Ollama status
docker-compose ps ollama

# Restart Ollama
docker-compose restart ollama

# Wait for it to be healthy
docker-compose ps ollama | grep healthy
```

**2. Model Not Loaded**
```bash
# Check if model exists
docker exec ollama ollama list

# If not listed, pull it
docker exec ollama ollama pull llama3.1:8b
```

**3. Context Too Large**
```bash
# Check if your prompt exceeds 32k tokens
# Each token ≈ 4 characters
# 32k tokens ≈ 128,000 characters

# Reduce prompt size or split into multiple requests
```

**4. System Resources Maxed Out**
```bash
# Check Docker resources
docker stats

# If CPU/memory at 100%, increase Docker resources:
# Docker Desktop > Settings > Resources
```

### Issue: Streaming Not Working

**Symptoms:**
- No tokens received until complete response
- N8N doesn't show progress

**Causes & Solutions:**

**1. Stream Parameter False**
```json
{
  "stream": true  // Must be true for streaming
}
```

**2. Nginx Buffering Enabled**
```bash
# Check nginx config has:
# proxy_buffering off;
# proxy_request_buffering off;

# If missing, add and restart:
docker-compose restart nginx
```

**3. Client Not Handling SSE**
```python
# Make sure using stream=True in requests
response = requests.post(url, json=data, stream=True)

# Read line by line
for line in response.iter_lines():
    # Process each chunk
```

## Docker & Container Issues

### Issue: Containers Won't Start

**Symptoms:**
```
Error response from daemon: Conflict
```

**Solutions:**

**1. Port Already in Use**
```bash
# Find what's using the port
lsof -i :3000  # Dashboard
lsof -i :8080  # Nginx
lsof -i :11434 # Ollama
lsof -i :5433  # PostgreSQL

# Kill the process or change port in docker-compose.yml
```

**2. Container Name Conflict**
```bash
# Remove old containers
docker-compose down
docker-compose up -d
```

**3. Image Pull Failure**
```bash
# Manually pull images
docker-compose pull

# If fails, check internet connection
curl -I https://hub.docker.com
```

### Issue: Container Keeps Restarting

**Symptoms:**
```
Restarting (1) Less than a second ago
```

**Solutions:**

**1. Check Container Logs**
```bash
# View crash logs
docker-compose logs --tail=100 <service-name>

# Common services that restart:
docker-compose logs cloudflared
docker-compose logs logger
docker-compose logs ollama
```

**2. Invalid Environment Variables**
```bash
# Verify .env file exists
ls -la .env

# Check for syntax errors
cat .env

# No spaces around =
# Correct: API_KEY=sk-...
# Wrong: API_KEY = sk-...
```

**3. Dependency Not Ready**
```bash
# Services depend on postgres being healthy
# Check postgres is running:
docker-compose ps postgres

# Restart all services in order:
docker-compose down
docker-compose up -d postgres
# Wait 10 seconds
docker-compose up -d
```

### Issue: Out of Disk Space

**Symptoms:**
```
Error: No space left on device
```

**Solutions:**

```bash
# Check Docker disk usage
docker system df

# Remove unused images/containers
docker system prune -a

# Remove old logs
docker-compose down
rm -rf /var/lib/docker/containers/*/log*

# Increase Docker disk limit:
# Docker Desktop > Settings > Resources > Disk image size
```

## Cloudflare Tunnel Issues

### Issue: Tunnel Shows "Unhealthy" or "Down"

**Symptoms:**
- Cloudflare dashboard shows tunnel as unhealthy
- Public API not accessible

**Solutions:**

**1. Invalid Tunnel Token**
```bash
# Check .env has valid TUNNEL_TOKEN
cat .env | grep TUNNEL_TOKEN

# Should be long base64 string starting with "eyJ"
# If invalid, regenerate in Cloudflare dashboard:
# Networks > Tunnels > Your Tunnel > Configure
```

**2. Check Tunnel Logs**
```bash
# View cloudflared logs
docker-compose logs cloudflared | tail -50

# Look for errors like:
# "failed to connect to the edge"
# "authentication failed"
# "unable to reach origin"
```

**3. Verify Tunnel Configuration**
```bash
# Check tunnel is configured correctly
cat cloudflared-config.yml

# Should have:
# ingress:
#   - hostname: api.kendall-max.org
#     service: http://nginx:80
```

**4. Docker Network Issue (macOS)**
```bash
# On Mac, Docker needs extra_hosts
# Check docker-compose.yml has:
# cloudflared:
#   extra_hosts:
#     - "host.docker.internal:host-gateway"

# If missing, add and restart:
docker-compose down
docker-compose up -d
```

### Issue: DNS Not Resolving

**Symptoms:**
```
curl: (6) Could not resolve host: api.kendall-max.org
```

**Solutions:**

**1. Check DNS Record**
- Go to Cloudflare Dashboard > DNS
- Verify record exists:
  - Type: CNAME
  - Name: api
  - Target: <tunnel-id>.cfargotunnel.com
  - Proxied: Yes (orange cloud)

**2. Wait for DNS Propagation**
```bash
# DNS can take up to 5 minutes
# Check current DNS:
dig api.kendall-max.org

# Or use online tools:
# https://dnschecker.org/#A/api.kendall-max.org
```

**3. Clear DNS Cache**
```bash
# macOS
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Test again
curl https://api.kendall-max.org/health
```

### Issue: Error 1033 - Argo Tunnel Error

**Symptoms:**
```
Error 1033: Argo Tunnel error
```

**Solutions:**

**1. Service URL Wrong**
```bash
# In Cloudflare tunnel config, service should be:
# http://nginx:80  (NOT https, NOT localhost)

# Update in Cloudflare dashboard:
# Networks > Tunnels > Your Tunnel > Public Hostname
```

**2. Nginx Not Responding**
```bash
# Test nginx locally
docker exec nginx-proxy curl http://localhost:80/health

# If fails, check nginx logs:
docker-compose logs nginx
```

## Database Issues

### Issue: Dashboard Shows No Data

**Symptoms:**
- Dashboard loads but shows 0 requests
- Stats are all zero

**Solutions:**

**1. Make Some API Requests**
```bash
# Generate test data
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "Hello"}], "stream": false}'

# Refresh dashboard
open http://localhost:3000
```

**2. Check PostgreSQL Running**
```bash
# Verify postgres is up
docker-compose ps postgres

# Test connection
docker exec -it ollama-postgres psql -U postgres -d ollama_logs -c "SELECT COUNT(*) FROM request_logs;"
```

**3. Logger Not Writing**
```bash
# Check logger logs for database errors
docker-compose logs logger | grep -i "error\|database"

# Common issue: Connection refused
# Solution: Restart postgres then logger
docker-compose restart postgres
docker-compose restart logger
```

### Issue: Database Connection Refused

**Symptoms:**
```
Error logging to database: connection refused
```

**Solutions:**

**1. PostgreSQL Not Started**
```bash
# Start postgres
docker-compose up -d postgres

# Wait for healthy status
docker-compose ps postgres | grep healthy
```

**2. Wrong Database Credentials**
```bash
# Check .env matches init.sql
cat .env | grep DB_

# Should be:
# DB_HOST=postgres
# DB_PORT=5432
# DB_NAME=ollama_logs
# DB_USER=postgres
# DB_PASSWORD=postgres
```

**3. Database Not Initialized**
```bash
# Recreate database
docker-compose down postgres
docker volume rm publickml_postgres_data
docker-compose up -d postgres

# Wait 10 seconds for init.sql to run
sleep 10

# Verify table exists
docker exec -it ollama-postgres psql -U postgres -d ollama_logs -c "\dt"
```

## Dashboard Issues

### Issue: Dashboard Won't Load

**Symptoms:**
- Browser shows "Connection refused"
- Page doesn't load

**Solutions:**

**1. Dashboard Not Running**
```bash
# Check status
docker-compose ps dashboard

# Start if down
docker-compose up -d dashboard

# View logs
docker-compose logs dashboard
```

**2. Port 3000 In Use**
```bash
# Check what's using port 3000
lsof -i :3000

# Kill other process or change dashboard port:
# docker-compose.yml: "3001:3000"
```

**3. Browser Cache Issue**
```bash
# Hard refresh browser
# Chrome/Firefox: Cmd+Shift+R

# Or clear browser cache
```

### Issue: Dashboard Shows Wrong Time

**Symptoms:**
- Timestamps are 7 hours off
- Shows UTC instead of Pacific Time

**Solution:**

Should be fixed now, but if not:

```bash
# Verify dashboard API has timezone conversion
docker exec ollama-dashboard grep -r "America/Los_Angeles" /app/

# If missing, update and rebuild:
docker-compose build dashboard
docker-compose up -d dashboard
```

### Issue: 404 Errors Showing in Dashboard

**Symptoms:**
- Table full of N/A entries
- Status 404 visible

**Solution:**

Should be filtered now, but if not:

```bash
# Check dashboard API filters http_status = 200
docker exec ollama-dashboard grep "http_status = 200" /app/api.py

# If missing, filter is not applied
# Rebuild with updated code
docker-compose build dashboard
docker-compose up -d dashboard
```

## Model Issues

### Issue: Model Not Found

**Symptoms:**
```json
{
  "error": "model 'llama3.1:8b' not found"
}
```

**Solutions:**

**1. Pull the Model**
```bash
# Download model (5GB, takes 5-15 min)
docker exec ollama ollama pull llama3.1:8b

# Verify it's installed
docker exec ollama ollama list
```

**2. Wrong Model Name**
```bash
# Check available models
docker exec ollama ollama list

# Use exact name from list
# Correct: llama3.1:8b
# Wrong: llama3.1, llama3.1:latest
```

### Issue: Model Loading Slow

**Symptoms:**
- First request takes 30+ seconds
- Subsequent requests fast

**Explanation:**
- First request loads model into memory
- Normal behavior
- After loaded, stays in RAM for fast responses

**Solutions:**

**1. Pre-warm Model**
```bash
# Send dummy request after starting
docker exec ollama ollama run llama3.1:8b "test"
```

**2. Keep Model Loaded**
```yaml
# In .env:
OLLAMA_MAX_LOADED_MODELS=1  # Keep 1 model loaded always
```

## Performance Issues

### Issue: Slow Response Times

**Symptoms:**
- Takes 30+ seconds for simple prompt
- Tokens/sec < 50

**Solutions:**

**1. Check System Resources**
```bash
# View Docker resource usage
docker stats

# If CPU/memory maxed:
# Docker Desktop > Settings > Resources
# Increase CPU cores (8+)
# Increase Memory (16GB+)
```

**2. Reduce Context Window**
```bash
# In .env, reduce context:
OLLAMA_NUM_CTX=16384  # From 32768

# Restart:
docker-compose restart ollama
```

**3. Check Concurrent Requests**
```bash
# Too many parallel requests slow down each
# In .env:
OLLAMA_NUM_PARALLEL=2  # Reduce from 4

docker-compose restart ollama
```

**4. Close Other Applications**
```bash
# M4 Max should handle easily, but close:
# - Other Docker containers
# - Memory-intensive apps
# - Browser with 100+ tabs
```

### Issue: High Costs in Dashboard

**Symptoms:**
- Cost seems too high for number of requests

**Solutions:**

**1. Verify Electricity Rate**
```bash
# Check .env has correct rate for your area
cat .env | grep ELECTRICITY_RATE

# San Diego SDG&E: 0.383
# Update if different
```

**2. Verify Power Consumption**
```bash
# M4 Max typically 60-80W during inference
# If showing 200W+, check:
cat .env | grep M4_MAX_POWER_WATTS

# Should be: M4_MAX_POWER_WATTS=80
```

**3. Duration Calculation**
```bash
# Cost = Power (W) × Duration (s) × Rate ($/kWh) / 3600000
# Example: 80W × 5s × $0.383/kWh = $0.000042
```

## N8N Integration Issues

### Issue: N8N "Cannot read properties of undefined (reading 'message')"

**Symptoms:**
- N8N OpenAI node shows error
- Connection test passes but execution fails

**Solution:**

Should be fixed with OpenAI format transformation, but verify:

```bash
# Test API returns OpenAI format
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "test"}], "stream": false}'

# Should see:
# "choices": [{"message": {"content": "..."}}]
# NOT: "message": {"content": "..."}
```

If response is wrong format:

```bash
# Rebuild logger with OpenAI transformation
docker-compose build --no-cache logger
docker-compose up -d logger
```

### Issue: N8N Connection Test Fails

**Symptoms:**
- "Could not connect to API"
- Timeout error

**Solutions:**

**1. Check Base URL**
```
Correct: https://api.kendall-max.org/v1
Wrong: https://api.kendall-max.org
Wrong: https://api.kendall-max.org/v1/
```

**2. Check API Key**
```
Include "Bearer" in N8N? NO
Just paste: sk-oatisawesome-2024-ml-api
```

**3. Test API Manually**
```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "test"}]}'

# If this works, N8N should work too
```

### Issue: N8N Model Not Found

**Symptoms:**
- Model "llama3.1:8b" not available

**Solutions:**

**1. Use Exact Model Name**
```
In N8N model field: llama3.1:8b
NOT: llama3.1, llama-3.1-8b, etc.
```

**2. Check Model List**
```bash
curl https://api.kendall-max.org/v1/models \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api"
```

## Still Having Issues?

### Collect Debug Information

```bash
# 1. Service status
docker-compose ps > debug.txt

# 2. All logs
docker-compose logs --tail=200 >> debug.txt

# 3. Environment (redact API keys!)
cat .env | grep -v "KEY\|TOKEN" >> debug.txt

# 4. Docker info
docker info >> debug.txt
docker system df >> debug.txt

# 5. Test API
curl -v https://api.kendall-max.org/health 2>&1 >> debug.txt
```

### Get Help

1. Check [GitHub Issues](https://github.com/Kgreeven-max/Machine-learning/issues)
2. Search for error message
3. Open new issue with debug.txt attached

### Nuclear Option: Complete Reset

```bash
# ⚠️ This deletes ALL data!

# 1. Stop everything
docker-compose down

# 2. Remove all volumes (deletes database!)
docker volume rm publickml_postgres_data
docker volume rm publickml_ollama_data
docker volume rm publickml_pgadmin_data
docker volume rm publickml_nginx_logs

# 3. Remove all images
docker-compose down --rmi all

# 4. Start fresh
docker-compose up -d

# 5. Pull model again
docker exec ollama ollama pull llama3.1:8b
```

---

**Most issues can be resolved by:**
1. Checking logs: `docker-compose logs <service>`
2. Restarting service: `docker-compose restart <service>`
3. Verifying .env configuration

For deeper issues, see [ARCHITECTURE.md](ARCHITECTURE.md) to understand how components interact.
