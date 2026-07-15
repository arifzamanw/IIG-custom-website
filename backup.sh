#!/bin/bash

# Load env vars
set -a
source /root/invest_in_georgia/.env
set +a

# Variables
CONTAINER_NAME=investgeorgia_postgres
BACKUP_DIR=/root/backups
MEDIA_DIR=/root/invest_in_georgia/media
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
DB_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
MEDIA_FILE="$BACKUP_DIR/media_backup_$DATE.tar.gz"

# Ensure backup dir exists
mkdir -p "$BACKUP_DIR"

# Backup DB
docker exec -e PGPASSWORD="$IG_DB_PASSWORD" "$CONTAINER_NAME" \
    pg_dump -U "$IG_DB_USER" -d "$IG_DB_NAME" > "$DB_FILE"

# Backup media folder
tar czf "$MEDIA_FILE" -C "$(dirname "$MEDIA_DIR")" "$(basename "$MEDIA_DIR")"

# Delete backups older than 30 days
find "$BACKUP_DIR" -type f \( -name "*.sql" -o -name "*.tar.gz" \) -mtime +30 -delete

echo "DB backup:    $DB_FILE ($(du -h "$DB_FILE" | cut -f1))"
echo "Media backup: $MEDIA_FILE ($(du -h "$MEDIA_FILE" | cut -f1))"
