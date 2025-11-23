#!/usr/bin/env bash
set -e
mkdir -p /data/backups
ts=$(date +%Y%m%d-%H%M%S)
cp /data/bot_database.db /data/backups/bot_database-${ts}.db
echo "Backup created: /data/backups/bot_database-${ts}.db"

