# Test API Locally (Without Cloudflare)

## Your friend can test the API on your local network

### Step 1: Find Your Local IP
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Step 2: Update N8N-COMPLETE-SETUP.md

Tell your friend to use:
- **API URL:** `http://YOUR_LOCAL_IP:8080/v1`
- **API Key:** `sk-oatisawesome-2024-ml-api`
- **Model:** `llama3.1:8b`

Replace `YOUR_LOCAL_IP` with the IP from Step 1 (like `192.168.1.100`)

### Step 3: Test It

**Your friend's N8N must be on the same WiFi network as you!**

From terminal:
```bash
curl -X POST http://YOUR_LOCAL_IP:8080/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Current Working Endpoints (Local Only):

✅ **Ollama:** http://localhost:11434
✅ **Nginx API:** http://localhost:8080
✅ **Dashboard:** http://localhost:3000
✅ **pgAdmin:** http://localhost:5050

The API **works locally** - just not through Cloudflare tunnel yet.
