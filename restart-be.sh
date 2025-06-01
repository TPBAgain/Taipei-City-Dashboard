#!/bin/bash
set -e

SERVICE_NAME="dashboard-be"

echo "🔁 Restarting $SERVICE_NAME..."

# Check if running
if docker ps --filter "name=$SERVICE_NAME" --format '{{.Names}}' | grep -q "$SERVICE_NAME"; then
  echo "🛑 Stopping $SERVICE_NAME..."
  docker-compose down "$SERVICE_NAME"
else
  echo "ℹ️ $SERVICE_NAME not currently running."
fi

# Wait until it's fully stopped
while docker ps --filter "name=$SERVICE_NAME" --format '{{.Names}}' | grep -q "$SERVICE_NAME"; do
  sleep 1
done

# Restart it
echo "🚀 Starting $SERVICE_NAME..."
docker-compose up -d "$SERVICE_NAME"

echo "✅ $SERVICE_NAME restarted."
