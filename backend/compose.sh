#!/bin/bash
# Universal compose wrapper - supports both Docker and Podman
# Usage: ./compose.sh [docker-compose|podman-compose] [command] [args...]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect available container runtime
detect_runtime() {
    if command -v podman &> /dev/null && command -v podman-compose &> /dev/null; then
        echo "podman-compose"
    elif command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        echo "docker"
    else
        echo "none"
    fi
}

# Get runtime preference from environment or detect
if [ -n "$CONTAINER_RUNTIME" ]; then
    RUNTIME="$CONTAINER_RUNTIME"
else
    RUNTIME=$(detect_runtime)
fi

# Determine compose command
case "$RUNTIME" in
    "podman-compose")
        COMPOSE_CMD="podman-compose"
        echo -e "${GREEN}Using Podman Compose${NC}"
        ;;
    "docker-compose")
        COMPOSE_CMD="docker-compose"
        echo -e "${GREEN}Using Docker Compose${NC}"
        ;;
    "docker")
        COMPOSE_CMD="docker compose"
        echo -e "${GREEN}Using Docker Compose V2${NC}"
        ;;
    "none")
        echo -e "${RED}Error: Neither Docker nor Podman found!${NC}"
        echo "Please install Docker or Podman:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Podman: https://podman.io/getting-started/installation"
        exit 1
        ;;
    *)
        echo -e "${RED}Error: Unknown runtime '$RUNTIME'${NC}"
        echo "Set CONTAINER_RUNTIME to: podman-compose, docker-compose, or docker"
        exit 1
        ;;
esac

# Get compose file location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# Execute command
if [ "$RUNTIME" = "docker" ]; then
    # Docker Compose V2 uses space instead of hyphen
    $COMPOSE_CMD -f "$COMPOSE_FILE" "$@"
else
    # Docker Compose V1 and Podman Compose use hyphen
    $COMPOSE_CMD -f "$COMPOSE_FILE" "$@"
fi

