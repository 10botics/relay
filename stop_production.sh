#!/bin/bash

# HTTP to HTTPS Relay Server - Production Stop Script

set -e

echo "🛑 Stopping HTTP to HTTPS Relay Server (PRODUCTION)..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running."
    exit 1
fi

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "📦 Stopping containers..."
    docker-compose down
    echo ""
    echo "✅ Relay server stopped successfully!"
else
    echo "ℹ️  No running containers found."
    echo "   Cleaning up anyway..."
    docker-compose down 2>/dev/null || true
    echo "✅ Cleanup complete!"
fi

echo ""
echo "💡 To start again, run: ./start_production.sh"

