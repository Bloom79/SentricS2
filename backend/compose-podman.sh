#!/bin/bash
# Podman-specific compose wrapper
# Usage: ./compose-podman.sh [command] [args...]

export CONTAINER_RUNTIME="podman-compose"
exec "$(dirname "$0")/compose.sh" "$@"

