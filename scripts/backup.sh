"""اسکریپت‌های کمکی"""

#!/bin/bash
# بکاپ از دیتابیس

BACKUP_DIR="/opt/proxyman/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/proxyman_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

docker exec proxyman_db pg_dump -U proxyman proxyman > "$BACKUP_FILE"
gzip "$BACKUP_FILE"

echo "✅ Backup created: ${BACKUP_FILE}.gz"
