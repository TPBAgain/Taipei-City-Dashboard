#!/bin/bash
set -e

ENV_FILE="docker/.env"
TEMPLATE_FILE="docker/.env.template"

echo "📁 [init] Ensuring .env exists..."
if [ ! -f "$ENV_FILE" ]; then
  cp "$TEMPLATE_FILE" "$ENV_FILE"
  echo "Copied .env.template → .env"
  echo "🔧 [init] Prompting for required env vars..."
  fill_env_var "VITE_MAPBOXTOKEN"
  fill_env_var "DASHBOARD_DEFAULT_USERNAME"
  fill_env_var "DASHBOARD_DEFAULT_Email"
  fill_env_var "DASHBOARD_DEFAULT_PASSWORD"
  fill_env_var "DB_DASHBOARD_PASSWORD"
  fill_env_var "DB_MANAGER_PASSWORD"
  fill_env_var "PGADMIN_DEFAULT_EMAIL"
  fill_env_var "PGADMIN_DEFAULT_PASSWORD"
fi

read -p "Do you want to disable HTTPS? (comment out lines 11-15 of nginx config) [y/N]: " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
  echo "📝 Commenting out lines 11–15 in nginx config..."
  sed -i.bak '11,15 s/^/# /' ./docker/nginx/conf.d/default.conf
  echo "✅ HTTPS disabled. You can re-enable it by restoring the .bak file or uncommenting manually."
fi


fill_env_var() {
  key="$1"
  if ! grep -q "^$key=" "$ENV_FILE"; then
    read -p "Enter value for $key: " val
    echo "$key=$val" >> "$ENV_FILE"
  fi
}

echo "🌐 [init] Creating Docker network..."
docker network inspect br_dashboard >/dev/null 2>&1 || \
  docker network create --driver=bridge --subnet=192.168.128.0/24 --gateway=192.168.128.1 br_dashboard

echo "🐘 [init] Starting DB containers..."
docker-compose -f docker/docker-compose-db.yaml up -d

echo "⏳ [init] Waiting for DBs to accept connections..."
wait_for_log() {
  while ! docker logs "$1" 2>&1 | grep -q "$2"; do sleep 2; done
}
wait_for_log postgres-data "database system is ready to accept connections"
wait_for_log postgres-manager "database system is ready to accept connections"

echo "🚀 Starting init containers..."
docker-compose -f docker/docker-compose-init.yaml up -d

# Define names of the init containers (match your docker-compose-init.yaml)
INIT_CONTAINERS=("dashboard-fe-init" "dashboard-be-init-manager" "dashboard-be-init-dashboard")

# Wait for each to exit
for container in "${INIT_CONTAINERS[@]}"; do
  echo "⏳ Waiting for $container to exit..."
  docker wait "$container"
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "❌ $container exited with code $exit_code"
    exit 1
  fi
done

bash ./pgadmin-wizard.sh

echo "✅ All init containers finished successfully."

echo "✅ [init] Done. You can now run './dev.sh'"
