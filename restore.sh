#!/usr/bin/env bash

set -euo pipefail


BACKUP_FILE="backup.sql"

docker compose exec -T postgres psql -U barq_app -d barq_tasks -v ON_ERROR_STOP=1 < "$BACKUP_FILE"
