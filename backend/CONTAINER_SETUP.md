# Container Setup Guide - Docker & Podman Support

This project supports both **Docker** and **Podman** as container runtimes. Podman is recommended for rootless operation and better security.

---

## Quick Start

### Auto-Detection (Recommended)
```bash
cd backend
./compose.sh up -d
```

This script automatically detects and uses the available runtime (prefers Podman if both are installed).

### Explicit Selection

**Podman:**
```bash
./compose-podman.sh up -d
```

**Docker:**
```bash
./compose-docker.sh up -d
```

---

## Installation

### Podman Installation

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y podman podman-compose
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install -y podman podman-compose
```

#### macOS
```bash
brew install podman podman-compose
```

#### Windows (WSL2)
```bash
# In WSL2
sudo apt-get update
sudo apt-get install -y podman podman-compose
```

### Docker Installation

See official documentation: https://docs.docker.com/get-docker/

---

## Configuration

### Environment Variable Override

You can force a specific runtime using the `CONTAINER_RUNTIME` environment variable:

```bash
# Force Podman
export CONTAINER_RUNTIME="podman-compose"
./compose.sh up -d

# Force Docker Compose V1
export CONTAINER_RUNTIME="docker-compose"
./compose.sh up -d

# Force Docker Compose V2
export CONTAINER_RUNTIME="docker"
./compose.sh up -d
```

---

## Common Commands

### Start Services
```bash
# Auto-detect
./compose.sh up -d

# Podman
./compose-podman.sh up -d

# Docker
./compose-docker.sh up -d
```

### Stop Services
```bash
./compose.sh down
```

### View Logs
```bash
./compose.sh logs -f db
./compose.sh logs -f redis
```

### Restart Services
```bash
./compose.sh restart db
```

### Remove Volumes (Clean Start)
```bash
./compose.sh down -v
```

---

## Podman-Specific Notes

### Rootless Operation
Podman runs rootless by default, which is more secure. The compose script handles this automatically.

### User Namespaces
Podman uses user namespaces by default. If you encounter permission issues:

```bash
# Check podman info
podman info

# Ensure user namespaces are enabled
echo $USER:$(id -u):1 | sudo tee -a /etc/subuid
echo $USER:$(id -g):1 | sudo tee -a /etc/subgid
```

### Volume Permissions
If you encounter volume permission issues with Podman:

```bash
# Fix volume permissions
podman unshare chown -R $(id -u):$(id -g) ~/.local/share/containers/storage/volumes/
```

---

## Docker-Specific Notes

### Docker Compose V2
If using Docker Compose V2 (newer Docker installations), the script automatically detects and uses `docker compose` (space instead of hyphen).

### Volume Locations
Docker volumes are typically stored in:
- Linux: `/var/lib/docker/volumes/`
- macOS: `~/Library/Containers/com.docker.docker/Data/vms/0/`
- Windows: `C:\ProgramData\docker\volumes\`

---

## Troubleshooting

### Container Runtime Not Found
```bash
# Check if Podman is installed
podman --version
podman-compose --version

# Check if Docker is installed
docker --version
docker-compose --version
```

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# Stop conflicting services or change ports in docker-compose.yml
```

### Permission Denied
```bash
# Podman: Usually not needed (rootless)
# Docker: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Volume Mount Issues (Podman)
```bash
# Ensure SELinux context is correct (if using SELinux)
chcon -Rt svirt_sandbox_file_t /path/to/volume
```

---

## Migration from Docker to Podman

If you're migrating from Docker to Podman:

1. **Stop Docker containers:**
   ```bash
   docker-compose down
   ```

2. **Export volumes (if needed):**
   ```bash
   docker run --rm -v kronos_eam_consolidated_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
   ```

3. **Start with Podman:**
   ```bash
   ./compose-podman.sh up -d
   ```

4. **Import volumes (if needed):**
   ```bash
   podman run --rm -v kronos_eam_consolidated_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
   ```

---

## Best Practices

1. **Use Auto-Detection**: Let the script choose the best available runtime
2. **Podman for Development**: Better security with rootless operation
3. **Docker for CI/CD**: More widespread CI/CD support
4. **Volume Backups**: Regularly backup volumes before major changes
5. **Environment Variables**: Use `.env` files for configuration (not committed to git)

---

## Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Podman vs Docker](https://www.redhat.com/en/topics/containers/what-is-podman)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)

