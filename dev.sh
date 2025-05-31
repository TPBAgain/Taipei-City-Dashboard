#!/bin/bash
set -e

echo "🌐 [dev] Starting main services..."
docker-compose -f docker/docker-compose.yaml up -d

echo "🧪 [dev] Site live at https://localhost:8080"
echo "📎 [dev] Hot-reload enabled (frontend only). Backend changes need container restart."
