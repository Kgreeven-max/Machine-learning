#!/bin/bash

set -e

echo "========================================="
echo "  Ollama API Gateway Setup"
echo "========================================="
echo ""

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

source .env

# Check if Cloudflare tunnel is configured
if [ -z "$TUNNEL_TOKEN" ]; then
    echo "⚠️  Cloudflare tunnel not configured yet."
    echo ""
    echo "Setting up Cloudflare Tunnel..."
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to: https://one.dash.cloudflare.com/"
    echo "2. Navigate to: Networks > Tunnels"
    echo "3. Create a new tunnel named 'ollama-api'"
    echo "4. Configure the tunnel:"
    echo "   - Public hostname: api.${CLOUDFLARE_DOMAIN}"
    echo "   - Service: http://nginx:80"
    echo "5. Copy the tunnel token and paste it below"
    echo ""
    read -p "Paste your Cloudflare Tunnel Token: " tunnel_token

    # Update .env file with tunnel token
    sed -i.bak "s|TUNNEL_TOKEN=.*|TUNNEL_TOKEN=$tunnel_token|" .env
    rm .env.bak

    # Reload environment
    source .env

    echo "✅ Tunnel configured!"
    echo ""
fi

# Start Docker containers
echo "🚀 Starting Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose up -d

echo ""
echo "⏳ Waiting for Ollama to be ready..."
sleep 10

# Wait for Ollama to be healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec ollama curl -f http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Still waiting... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama failed to start"
    exit 1
fi

echo ""
echo "📦 Pulling AI models (this may take a while)..."
echo ""

# Pull models
IFS=',' read -ra MODELS <<< "$OLLAMA_MODELS"
for model in "${MODELS[@]}"; do
    model=$(echo "$model" | xargs) # trim whitespace
    echo "   Pulling $model..."
    docker exec ollama ollama pull "$model"
    echo "   ✅ $model ready!"
    echo ""
done

echo ""
echo "========================================="
echo "  🎉 Setup Complete!"
echo "========================================="
echo ""
echo "Your API is now live at:"
echo "  URL: https://api.${CLOUDFLARE_DOMAIN}"
echo ""
echo "API Key (share this with your friend):"
echo "  ${API_KEY}"
echo ""
echo "========================================="
echo "  N8N Configuration"
echo "========================================="
echo ""
echo "In N8N OpenAI node, use:"
echo "  • Base URL: https://api.${CLOUDFLARE_DOMAIN}/v1"
echo "  • API Key: ${API_KEY}"
echo "  • Model: ${DEFAULT_MODEL}"
echo ""
echo "========================================="
echo ""
echo "Test your API with:"
echo "curl -X POST https://api.${CLOUDFLARE_DOMAIN}/v1/chat/completions \\"
echo "  -H 'Authorization: Bearer ${API_KEY}' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"model\": \"${DEFAULT_MODEL}\","
echo "    \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]"
echo "  }'"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
echo ""
