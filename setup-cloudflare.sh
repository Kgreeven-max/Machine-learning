#!/bin/bash

set -e

echo "🔧 Setting up Cloudflare Tunnel via API..."

# Load environment
source .env

# Get Cloudflare Account ID (we'll need to check zones)
ZONE_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=${CLOUDFLARE_DOMAIN}" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_KEY}" \
  -H "Content-Type: application/json")

ACCOUNT_ID=$(echo "$ZONE_RESPONSE" | grep -o '"account":{"id":"[^"]*' | head -1 | cut -d'"' -f6)

if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Could not find account ID for domain ${CLOUDFLARE_DOMAIN}"
    echo "Response: $ZONE_RESPONSE"
    exit 1
fi

echo "✅ Found Account ID: $ACCOUNT_ID"

# Create tunnel
TUNNEL_NAME="ollama-api-$(date +%s)"
echo "📡 Creating tunnel: $TUNNEL_NAME"

TUNNEL_RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/cfd_tunnel" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${TUNNEL_NAME}\",\"tunnel_secret\":\"$(openssl rand -base64 32)\"}")

TUNNEL_ID=$(echo "$TUNNEL_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
TUNNEL_TOKEN=$(echo "$TUNNEL_RESPONSE" | grep -o '"token":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to create tunnel"
    echo "Response: $TUNNEL_RESPONSE"
    exit 1
fi

echo "✅ Tunnel created: $TUNNEL_ID"

# Configure tunnel DNS
echo "🌐 Configuring DNS for api.${CLOUDFLARE_DOMAIN}..."

ZONE_ID=$(echo "$ZONE_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

DNS_RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\":\"CNAME\",
    \"name\":\"api\",
    \"content\":\"${TUNNEL_ID}.cfargotunnel.com\",
    \"proxied\":true
  }")

echo "✅ DNS configured"

# Configure tunnel routes
echo "🔗 Configuring tunnel routes..."

ROUTE_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"config\": {
      \"ingress\": [
        {
          \"hostname\": \"api.${CLOUDFLARE_DOMAIN}\",
          \"service\": \"http://nginx:80\"
        },
        {
          \"service\": \"http_status:404\"
        }
      ]
    }
  }")

echo "✅ Tunnel routes configured"

# Update .env with tunnel token
sed -i.bak "s|TUNNEL_TOKEN=.*|TUNNEL_TOKEN=${TUNNEL_TOKEN}|" .env
rm -f .env.bak

echo ""
echo "========================================="
echo "✅ Cloudflare Tunnel Setup Complete!"
echo "========================================="
echo ""
echo "Tunnel ID: $TUNNEL_ID"
echo "Public URL: https://api.${CLOUDFLARE_DOMAIN}"
echo ""
