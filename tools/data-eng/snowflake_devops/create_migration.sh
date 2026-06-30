#!/bin/bash

# Usage: ./create_migration.sh <table_name>

# Check if table name was provided
if [ -z "$1" ]; then
  echo "❌ Error: No table name provided."
  echo "Usage: $0 <table_name>"
  echo "Example: $0 customer_orders"
  exit 1
fi

TABLE_NAME=$1
DATE=$(date +%Y%m%d)

# Try to get Git username; fallback to `FILL_IN_USERNAME` if not found
GIT_USERNAME=$(git config user.name | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
if [ -z "$GIT_USERNAME" ]; then
  echo "⚠️ Warning: No Git username found, using default 'FILL_IN_USERNAME'."
  GIT_USERNAME="FILL_IN_USERNAME"
fi

FILENAME="migrations/${DATE}_${TABLE_NAME}.sql"

cat <<EOF > "$FILENAME"
-- liquibase formatted sql

-- changeset ${GIT_USERNAME}:${DATE}_${TABLE_NAME}
CREATE OR REPLACE TABLE ${TABLE_NAME} (
  id INTEGER
);

-- rollback DROP TABLE ${TABLE_NAME};
EOF

echo "✅ Created migration file: $FILENAME"
