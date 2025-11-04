#!/bin/bash
# Complete setup script for fresh installation
# This script sets up everything from scratch on a new device
# Usage: ./setup-from-scratch.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Kronos EAM - Complete Setup from Scratch${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check system requirements
echo -e "${YELLOW}[1/8] Checking system requirements...${NC}"

MISSING_DEPS=()

if ! command -v podman &> /dev/null; then
    MISSING_DEPS+=("podman")
fi
if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi
if ! command -v node &> /dev/null && ! command -v npm &> /dev/null; then
    MISSING_DEPS+=("nodejs/npm")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo ""
    echo "Installation instructions:"
    echo ""
    if [[ " ${MISSING_DEPS[@]} " =~ " podman " ]]; then
        echo "Podman:"
        echo "  Ubuntu/Debian: sudo apt-get install podman"
        echo "  Fedora/RHEL:   sudo dnf install podman"
        echo "  macOS:         brew install podman"
        echo ""
    fi
    if [[ " ${MISSING_DEPS[@]} " =~ " python3 " ]]; then
        echo "Python 3.11+:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
        echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip"
        echo "  macOS:         brew install python@3.11"
        echo ""
    fi
    if [[ " ${MISSING_DEPS[@]} " =~ " nodejs/npm " ]]; then
        echo "Node.js 18+:"
        echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
        echo "  Fedora/RHEL:   sudo dnf install nodejs npm"
        echo "  macOS:         brew install node"
        echo ""
    fi
    exit 1
fi

echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

# Setup backend
echo -e "${YELLOW}[2/8] Setting up backend...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}  Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

source venv/bin/activate
echo -e "${YELLOW}  Installing Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Setup frontend
echo -e "${YELLOW}[3/8] Setting up frontend...${NC}"
if [ -d "../frontend" ]; then
    cd ../frontend
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}  Installing Node.js dependencies...${NC}"
        npm install
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
    fi
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠ Frontend directory not found, skipping${NC}"
fi
echo ""

# Start services using the main startup script
echo -e "${YELLOW}[4/8] Starting all services...${NC}"
echo ""
exec ./start-services.sh

