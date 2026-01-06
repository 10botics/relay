#!/bin/bash

# HTTP to HTTPS Relay Server - Development Start Script

set -e

echo "🚀 Starting HTTP to HTTPS Relay Server (DEVELOPMENT)..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running."
    echo "   Please start Docker and try again."
    exit 1
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir -p logs
fi

# Build and start the containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.dev.yml up -d --build

# Wait a moment for the container to start
sleep 2

# Check container status
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo ""
    echo "✅ Relay server is running in DEVELOPMENT mode!"
    echo ""
    echo "📊 Container status:"
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    echo "🔗 Development endpoints:"
    echo "   - Health check: http://localhost:8080/health"
    echo "   - Service info:  http://localhost:8080/"
    echo "   - Relay endpoint: http://localhost:8080/relay"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose -f docker-compose.dev.yml logs -f relay"
    echo ""
    echo "🛑 Stop server:"
    echo "   ./stop_dev.sh"
else
    echo ""
    echo "⚠️  Warning: Container may not be running properly"
    echo "   Check logs with: docker-compose -f docker-compose.dev.yml logs relay"
    exit 1
fi

