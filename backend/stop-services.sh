#!/bin/bash
# Stop all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping Kronos EAM Services..."
echo ""

# Stop backend
if pgrep -f "uvicorn app.main:app" > /dev/null; then
  echo "Stopping backend..."
  pkill -f "uvicorn app.main:app"
  echo "✓ Backend stopped"
fi

# Stop frontend
if pgrep -f "vite" > /dev/null; then
  echo "Stopping frontend..."
  pkill -f "vite"
  echo "✓ Frontend stopped"
fi

# Stop containers (but keep data)
echo "Stopping containers..."
podman stop kronos-eam-db kronos-eam-redis 2>/dev/null || true
echo "✓ Containers stopped"

echo ""
echo "✅ All services stopped!"
echo ""
echo "Note: Container data is preserved. To remove containers:"
echo "  podman rm kronos-eam-db kronos-eam-redis"
echo ""
echo "To remove volumes (deletes data):"
echo "  podman volume rm kronos_eam_postgres_data kronos_eam_redis_data"

