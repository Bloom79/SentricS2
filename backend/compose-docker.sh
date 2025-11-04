#!/bin/bash
# Docker-specific compose wrapper
# Usage: ./compose-docker.sh [command] [args...]

export CONTAINER_RUNTIME="docker-compose"
exec "$(dirname "$0")/compose.sh" "$@"

