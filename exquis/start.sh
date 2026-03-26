# ============================================
# EXQUIS - Quick Start Script
# ============================================

#!/bin/bash

echo "🧠 Exquis - Quick Start"
echo "======================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✓ Docker found"

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo "📝 Creating .env from template..."
    cp config/.env.example config/.env
    echo "⚠️  Please edit config/.env and add your API keys!"
fi

echo ""
echo "Available commands:"
echo "  docker-compose up --build    # Start all services"
echo "  docker-compose up             # Start (if already built)"
echo "  docker-compose down           # Stop all services"
echo "  docker-compose logs -f api    # View API logs"
echo ""
echo "Once running, access:"
echo "  - Dashboard: http://localhost:3000"
echo "  - API:      http://localhost:8000"
echo "  - Neo4j:    http://localhost:7474"
echo ""
echo "🧪 To test without running full Docker:"
echo "  python test_setup.py"
echo ""