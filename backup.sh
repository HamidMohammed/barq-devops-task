#!/usr/bin/env bash

set -euo pipefail

BACKUP_FILE="backup.sql"
docker compose exec -T postgres pg_dump -U barq_app -d barq_tasks > "$BACKUP_FILE"
