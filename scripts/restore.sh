#!/usr/bin/env bash
set -e
if [ -z "$1" ]; then
  echo "Usage: $0 path/to/backup.db"
  exit 1
fi
cp "$1" /data/bot_database.db
echo "Restored to /data/bot_database.db"

