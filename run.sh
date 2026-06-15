#!/bin/bash

# AI-IPS Quick Start Script

# Get current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛡 AI-IPS Cyber Defense Platform${NC}"
echo "======================================"

# Check if setup is needed
if [ ! -d "logs" ] || [ ! -f "configs/app_config.json" ]; then
    echo -e "${GREEN}Running initial setup...${NC}"
    python3 -m pip install -e .
    ai-ips setup
fi

# Function to show help
show_help() {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start the IPS engine (requires sudo)"
    echo "  monitor   Start the SOC terminal monitor"
    echo "  dashboard Launch the web dashboard"
    echo "  status    Show system status"
    echo "  setup     Run environment setup"
}

case "$1" in
    start)
        echo -e "${GREEN}Starting Engine...${NC}"
        sudo ai-ips start
        ;;
    monitor)
        echo -e "${GREEN}Starting Monitor...${NC}"
        ai-ips monitor
        ;;
    dashboard)
        echo -e "${GREEN}Starting Dashboard...${NC}"
        ai-ips dashboard
        ;;
    status)
        ai-ips status
        ;;
    setup)
        ai-ips setup
        ;;
    *)
        show_help
        ;;
esac
