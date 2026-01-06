#!/bin/bash

# HTTP to HTTPS Relay Server - Production Start Script

set -e

echo "🚀 Starting HTTP to HTTPS Relay Server (PRODUCTION)..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running."
    echo "   Please start Docker and try again."
    exit 1
fi

# Check if docker05 network exists, create if it doesn't
if ! docker network inspect docker05 > /dev/null 2>&1; then
    echo "📡 Creating docker05 network..."
    docker network create docker05
    echo "✅ Network created"
    echo ""
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir -p logs
fi

# Build and start the containers
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait a moment for the container to start
sleep 2

# Check container status
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Relay server is running in PRODUCTION mode!"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "🔗 Production endpoints (via nginx-proxy):"
    echo "   - https://relay.10botics.co/health"
    echo "   - https://relay.10botics.co/"
    echo "   - https://relay.10botics.co/relay"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f relay"
    echo ""
    echo "🛑 Stop server:"
    echo "   ./stop_production.sh"
else
    echo ""
    echo "⚠️  Warning: Container may not be running properly"
    echo "   Check logs with: docker-compose logs relay"
    exit 1
fi

