#!/bin/bash
set -e

# Paths
PGADMIN_DIR="./docker/pgadmin"
ENV_FILE="docker/.env"
SERVER_FILE="$PGADMIN_DIR/servers.json"
PGPASS_FILE="$PGADMIN_DIR/pgpass"

mkdir -p "$PGADMIN_DIR"

# Color output
green() { echo -e "\033[32m$1\033[0m"; }
red() { echo -e "\033[31m$1\033[0m"; }

# Load from .env
get_env_var() {
  key="$1"
  val=$(grep -E "^${key}=" "$ENV_FILE" | cut -d '=' -f2-)
  if [ -z "$val" ]; then
    red "❌ Missing $key in .env"
    exit 1
  fi
  echo "$val"
}

# Extract needed env vars
DB_DASHBOARD_PASSWORD=$(get_env_var "DB_DASHBOARD_PASSWORD")
DB_MANAGER_PASSWORD=$(get_env_var "DB_MANAGER_PASSWORD")

green "🧾 Generating pgpass..."
cat > "$PGPASS_FILE" <<EOF
*:*:*:postgres:$DB_DASHBOARD_PASSWORD
*:*:*:postgres:$DB_MANAGER_PASSWORD
EOF

chmod 600 "$PGPASS_FILE"

green "🧾 Generating servers.json..."
cat > "$SERVER_FILE" <<EOF
{
  "Servers": {
    "1": {
      "Name": "dashboard",
      "Group": "Servers",
      "Host": "postgres-data",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "postgres",
      "SSLMode": "prefer",
      "PassFile": "/pgpass"
    },
    "2": {
      "Name": "dashboardmanager",
      "Group": "Servers",
      "Host": "postgres-manager",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "postgres",
      "SSLMode": "prefer",
      "PassFile": "/pgpass"
    }
  }
}
EOF

green "✅ pgAdmin config created at $PGADMIN_DIR"
