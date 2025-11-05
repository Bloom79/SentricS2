#!/bin/bash
#
# Test Runner Script for SentricS2 Backend
# Provides convenient commands for running tests with coverage
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SentricS2 Backend Test Runner       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found!${NC}"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Parse command line arguments
COMMAND="${1:-all}"

case "$COMMAND" in
    all)
        echo -e "${YELLOW}Running all tests with coverage...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term-missing -v
        ;;

    unit)
        echo -e "${YELLOW}Running unit tests...${NC}"
        pytest tests/unit/ -v
        ;;

    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        pytest tests/integration/ -v
        ;;

    api)
        echo -e "${YELLOW}Running API tests...${NC}"
        pytest tests/unit/api/ -v
        ;;

    services)
        echo -e "${YELLOW}Running service tests...${NC}"
        pytest tests/unit/services/ -v
        ;;

    coverage)
        echo -e "${YELLOW}Generating coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated!${NC}"
        echo -e "Open ${GREEN}htmlcov/index.html${NC} in your browser"
        ;;

    quick)
        echo -e "${YELLOW}Running quick tests (no coverage)...${NC}"
        pytest -x -v
        ;;

    watch)
        echo -e "${YELLOW}Running tests in watch mode...${NC}"
        pytest-watch -v
        ;;

    clean)
        echo -e "${YELLOW}Cleaning test artifacts...${NC}"
        rm -rf .pytest_cache htmlcov .coverage
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}Cleanup complete!${NC}"
        ;;

    help|--help|-h)
        echo "Usage: ./run_tests.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  all          Run all tests with coverage (default)"
        echo "  unit         Run only unit tests"
        echo "  integration  Run only integration tests"
        echo "  api          Run only API tests"
        echo "  services     Run only service tests"
        echo "  coverage     Generate coverage report (HTML + terminal)"
        echo "  quick        Run tests quickly without coverage"
        echo "  watch        Run tests in watch mode (requires pytest-watch)"
        echo "  clean        Clean test artifacts and cache"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests"
        echo "  ./run_tests.sh unit               # Run unit tests only"
        echo "  ./run_tests.sh coverage           # Generate coverage report"
        echo ""
        ;;

    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Display summary
if [ "$COMMAND" != "help" ] && [ "$COMMAND" != "clean" ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Test run complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
fi
