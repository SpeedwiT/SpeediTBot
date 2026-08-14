#!/bin/bash
# بروزرسانی پروژه

set -e

PROJECT_DIR="/opt/proxyman"
cd "$PROJECT_DIR"

echo "📥 Pulling latest changes..."
git pull

echo "🔨 Rebuilding containers..."
docker-compose build --no-cache

echo "🚀 Restarting services..."
docker-compose up -d

echo "✅ Update complete!"
echo ""
echo "📊 Status:"
docker-compose ps
