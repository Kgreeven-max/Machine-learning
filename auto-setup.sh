#!/bin/bash

set -e

echo "========================================="
echo "  🚀 Ollama API - Full Auto Setup"
echo "========================================="
echo ""

# Load environment variables
source .env

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflared
    else
        echo "Please install cloudflared manually: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        exit 1
    fi
fi

echo "✅ cloudflared installed"
echo ""

# Check if already logged in to Cloudflare
if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo "🔐 First time setup - logging into Cloudflare..."
    echo "A browser window will open - please authorize the connection"
    echo ""
    cloudflared tunnel login
    echo ""
    echo "✅ Cloudflare authentication complete!"
    echo ""
fi

# Create a unique tunnel name
TUNNEL_NAME="ollama-api-$(date +%s)"
echo "📡 Creating Cloudflare Tunnel: $TUNNEL_NAME"

# Create the tunnel
cloudflared tunnel create "$TUNNEL_NAME" 2>/dev/null || true

# Get the tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}' | head -1)

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to create tunnel"
    exit 1
fi

echo "✅ Tunnel created: $TUNNEL_ID"
echo ""

# Create tunnel config file
echo "📝 Creating tunnel configuration..."
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: api.$CLOUDFLARE_DOMAIN
    service: http://localhost:8080
  - service: http_status:404
EOF

echo "✅ Configuration created"
echo ""

# Route DNS
echo "🌐 Setting up DNS routing..."
cloudflared tunnel route dns "$TUNNEL_NAME" "api.$CLOUDFLARE_DOMAIN" 2>/dev/null || echo "DNS already configured"

echo "✅ DNS configured"
echo ""

# Get the tunnel credentials file path
CREDS_FILE="$HOME/.cloudflared/$TUNNEL_ID.json"

if [ ! -f "$CREDS_FILE" ]; then
    echo "❌ Credentials file not found at $CREDS_FILE"
    exit 1
fi

# Update .env with tunnel ID (for reference)
sed -i.bak "s|TUNNEL_TOKEN=.*|TUNNEL_TOKEN=$TUNNEL_ID|" .env
rm -f .env.bak

echo "✅ Tunnel configuration complete"
echo ""

# Stop any existing containers and cloudflared
echo "🔄 Stopping existing services..."
docker-compose down 2>/dev/null || true
pkill -f "cloudflared tunnel run" 2>/dev/null || true

# Start Docker containers (without cloudflared)
echo "🐳 Starting Docker containers..."
docker-compose up -d ollama nginx 2>/dev/null || true

echo "⏳ Waiting for services to start..."
sleep 10

# Check Ollama health
echo "🔍 Checking Ollama status..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
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

# Start cloudflared tunnel in background
echo "🌐 Starting Cloudflare Tunnel..."
nohup cloudflared tunnel run $TUNNEL_NAME > /tmp/cloudflared.log 2>&1 &
CLOUDFLARED_PID=$!

echo "✅ Tunnel running (PID: $CLOUDFLARED_PID)"
echo "   View tunnel logs: tail -f /tmp/cloudflared.log"
echo ""

echo "📦 Pulling Llama 3.1 8B (optimized for M4 Max speed)..."
echo "   Download size: ~4.7GB, should take 2-5 minutes..."
echo "   Performance: 96-100 tokens/sec on M4 Max!"
echo ""

# Pull the fastest model for M4 Max
docker exec ollama ollama pull llama3.1:8b

echo "✅ Llama 3.1 8B ready!"

echo ""
echo "========================================="
echo "  🎉 Setup Complete!"
echo "========================================="
echo ""
echo "Your API is now live at:"
echo "  🌐 https://api.${CLOUDFLARE_DOMAIN}"
echo ""
echo "API Keys for N8N:"
echo "  🔑 Primary: ${API_KEY}"
echo "  🔑 Alt: ${API_KEY_ALT}"
echo ""
echo "Test your API:"
echo "  curl -X POST https://api.${CLOUDFLARE_DOMAIN}/v1/chat/completions \\"
echo "    -H 'Authorization: Bearer ${API_KEY}' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"model\": \"llama3:70b\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}'"
echo ""
echo "Commands:"
echo "  📊 View Docker logs: docker-compose logs -f"
echo "  📊 View tunnel logs: tail -f /tmp/cloudflared.log"
echo "  🛑 Stop everything: ./stop.sh"
echo "  🔄 Restart: ./auto-setup.sh"
echo ""
echo "Tunnel ID: $TUNNEL_ID"
echo "Cloudflared PID: $CLOUDFLARED_PID"
echo ""
echo "========================================="
