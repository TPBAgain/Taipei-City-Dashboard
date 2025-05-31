#!/bin/bash

BASE_URL="http://localhost:8088/api/v1/test"
BACKUP_DIR="~/hackathon/TaipeiCityDashboard/backup"


# Colors for UX
green() { echo -e "\033[32m$1\033[0m"; }
red() { echo -e "\033[31m$1\033[0m"; }

# Upload a SQL file
upload_sql() {
  FILE="$1"
  if [ ! -f "$FILE" ]; then
    red "❌ File not found: $FILE"
    exit 1
  fi
  green "📤 Uploading $FILE to server..."
  curl -v -X POST "$BASE_URL/upload" -F "sql_file=@$FILE"
}

# Export a component by index
export_component() {
  INDEX="$1"
  OUTFILE="$BACKUP_DIR/${INDEX}.sql"
  green "📦 Exporting component: $INDEX → $OUTFILE"
  curl -s "$BASE_URL/component/$INDEX" > "$OUTFILE"
  green "✅ Saved."
}

# Export a table (dataset) by name
export_table() {
  TABLE="$1"
  OUTFILE="$BACKUP_DIR/${TABLE}.sql"
  green "📦 Exporting table: $TABLE → $OUTFILE"
  curl -s "$BASE_URL/$TABLE" > "$OUTFILE"
  green "✅ Saved."
}

# CLI help
show_help() {
  echo "Usage: $0 [upload|component|table] [ARG]"
  echo ""
  echo "  upload [file.sql]       → Import SQL file to server"
  echo "  component [index]       → Export component to backup/*.sql"
  echo "  table [table_name]      → Export dataset table to backup/*.sql"
  echo ""
  echo "Examples:"
  echo "  $0 upload backup/ebus_percent.sql"
  echo "  $0 component ebus_percent"
  echo "  $0 table bus_info_new_tpe"
}

# Dispatcher
case "$1" in
  upload)
    upload_sql "$2"
    ;;
  component)
    export_component "$2"
    ;;
  table)
    export_table "$2"
    ;;
  *)
    show_help
    ;;
esac

