#!/bin/bash

set -e

echo "🔧 Setting up Cloudflare Tunnel..."

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    brew install cloudflared
fi

# Create tunnel
TUNNEL_NAME="ollama-api"
echo "📡 Creating tunnel: $TUNNEL_NAME"

# Login to Cloudflare (this will open browser)
cloudflared tunnel login

# Create the tunnel
cloudflared tunnel create $TUNNEL_NAME

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to get tunnel ID"
    exit 1
fi

echo "✅ Tunnel created: $TUNNEL_ID"

# Create config file
cat > ~/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: api.kendall-max.org
    service: http://localhost:8080
  - service: http_status:404
EOF

# Route DNS
cloudflared tunnel route dns $TUNNEL_NAME api.kendall-max.org

# Get tunnel token
TUNNEL_TOKEN=$(cat ~/.cloudflared/$TUNNEL_ID.json | base64)

# Update .env
source .env
sed -i.bak "s|TUNNEL_TOKEN=.*|TUNNEL_TOKEN=${TUNNEL_TOKEN}|" .env
rm -f .env.bak

echo "✅ Tunnel configured!"
echo ""
echo "Tunnel ID: $TUNNEL_ID"
echo "Public URL: https://api.kendall-max.org"
echo ""
