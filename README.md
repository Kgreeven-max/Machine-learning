# Ollama API Gateway - Drop-in ChatGPT Replacement

A production-ready, OpenAI-compatible API gateway for Ollama with Cloudflare Tunnel, designed for seamless N8N integration.

## Features

✅ **OpenAI-Compatible API** - Works with any tool expecting ChatGPT API
✅ **Persistent API Key** - Never changes, configure once
✅ **Public Access** - Exposed via Cloudflare Tunnel
✅ **Apple Silicon Optimized** - Built for M4 Max
✅ **Internet Access** - Models can access real-time information
✅ **Zero Configuration for Users** - Just paste URL + API Key

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Cloudflare account (free tier works)
- Domain: kendall-max.org
- Homebrew (on macOS - for cloudflared installation)

### Installation

**One command setup:**

```bash
./auto-setup.sh
```

**What happens:**

1. **First run only:** Browser opens for Cloudflare authentication - just click authorize
2. Auto-creates Cloudflare Tunnel with unique name
3. Auto-configures DNS: api.kendall-max.org → your tunnel
4. Starts Ollama + Nginx in Docker
5. Starts Cloudflare Tunnel on your Mac
6. Downloads models: llama3:70b & mixtral (10-30 min)

**That's it!** Works on any Mac, no manual configuration needed.

## Your API Details

After setup completes, you'll see:

```
URL: https://api.kendall-max.org
API Keys:
  - sk-oatisawesome-2024-ml-api
  - sk-0at!sAw3s0m3-2024-ml-v2
```

**Share these with your friend for N8N!**

## N8N Configuration

### Using the HTTP Request Node

1. Add an **HTTP Request** node
2. Configure:
   - **Method**: POST
   - **URL**: `https://api.kendall-max.org/v1/chat/completions`
   - **Authentication**: Generic Credential Type > Header Auth
     - **Name**: `Authorization`
     - **Value**: `Bearer sk-ollama-kendallmax-2024-7f9e3a1b4c6d8e2f`
   - **Body**:
     ```json
     {
       "model": "llama3:70b",
       "messages": [
         {"role": "user", "content": "Your message here"}
       ]
     }
     ```

### Using the OpenAI Node (Recommended)

1. Add an **OpenAI** node
2. Create new credentials:
   - **API Key**: `sk-ollama-kendallmax-2024-7f9e3a1b4c6d8e2f`
   - **Base URL**: `https://api.kendall-max.org/v1`
3. Set model: `llama3:70b` or `mixtral`

**That's it!** Works exactly like ChatGPT.

## Available Endpoints

All standard OpenAI endpoints are supported:

- `POST /v1/chat/completions` - Chat completions (streaming supported)
- `POST /v1/completions` - Text completions
- `POST /v1/embeddings` - Generate embeddings
- `GET /v1/models` - List available models

## Testing Your API

### Simple test:

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-ollama-kendallmax-2024-7f9e3a1b4c6d8e2f" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:70b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### With streaming:

```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-ollama-kendallmax-2024-7f9e3a1b4c6d8e2f" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:70b",
    "messages": [{"role": "user", "content": "Write a story"}],
    "stream": true
  }'
```

## Available Models

- **llama3:70b** - Most capable, slower (recommended for complex tasks)
- **mixtral** - Faster, good for most use cases

To add more models, edit `.env`:

```bash
OLLAMA_MODELS=llama3:70b,mixtral,llama3.1:8b
```

Then run:

```bash
docker exec ollama ollama pull llama3.1:8b
```

## Management Commands

**View Docker logs:**
```bash
docker-compose logs -f
```

**View tunnel logs:**
```bash
tail -f /tmp/cloudflared.log
```

**Stop everything:**
```bash
./stop.sh
```

**Start again:**
```bash
./auto-setup.sh
```

**Note:** Each run creates a new tunnel (old ones can be deleted from Cloudflare dashboard)

**Update models:**
```bash
docker exec ollama ollama pull llama3:70b
```

## Troubleshooting

### API returns 401 Unauthorized

- Check that you're using the correct API key from `.env`
- Make sure the `Authorization` header format is: `Bearer YOUR_API_KEY`

### Models not responding

```bash
# Check if Ollama is running
docker exec ollama curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama
```

### Cloudflare tunnel not working

```bash
# Check tunnel status
docker-compose logs cloudflared

# Verify in Cloudflare Dashboard:
# Networks > Tunnels > ollama-api should show "Healthy"
```

### Slow responses

- Try using `mixtral` instead of `llama3:70b` (faster)
- Check system resources: Docker Desktop > Settings > Resources
- Recommended: 16GB+ RAM allocated to Docker

## Security Notes

- ✅ API key authentication protects your endpoint
- ✅ CORS enabled for web access
- ⚠️ API key is persistent - keep `.env` file secure
- ⚠️ Don't commit `.env` to git (already in `.gitignore`)

## Architecture

```
Internet → Cloudflare Tunnel → Nginx (Auth + Proxy) → Ollama
```

- **Cloudflare Tunnel**: Securely exposes local service
- **Nginx**: API key validation, CORS, request logging
- **Ollama**: AI model inference on your M4 Max

## Support

**Check service health:**
```bash
curl https://api.kendall-max.org/health
```

**View Nginx logs:**
```bash
docker-compose logs nginx
```

**View Ollama logs:**
```bash
docker-compose logs ollama
```

## Credits

Built for easy AI model deployment with:
- [Ollama](https://ollama.ai/) - Local AI models
- [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/) - Secure tunneling
- [Nginx](https://nginx.org/) - Reverse proxy
- [Docker](https://www.docker.com/) - Containerization
