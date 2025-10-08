#!/bin/bash

echo "🛑 Stopping all services..."
echo ""

# Stop Docker containers
echo "Stopping Docker containers..."
docker-compose down

# Stop cloudflared
echo "Stopping Cloudflare Tunnel..."
pkill -f "cloudflared tunnel run" 2>/dev/null && echo "✅ Tunnel stopped" || echo "⚠️  No tunnel running"

echo ""
echo "✅ All services stopped"
echo ""
echo "To start again: ./auto-setup.sh"
