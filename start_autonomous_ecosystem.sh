#!/bin/bash

# 🚀 Autonomous Money-Making Ecosystem Startup Script
# Ultimate AI-Powered Automated Income Generation Platform
# Created by: Mulky Malikul Dhaher (Indonesia)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "================================================================================"
    echo "🚀 AUTONOMOUS MONEY-MAKING ECOSYSTEM v6.0.0 🚀"
    echo "================================================================================"
    echo ""
    echo "💰 THE ULTIMATE AI-POWERED AUTOMATED INCOME GENERATION PLATFORM"
    echo "🎯 Target: \$2,500+/day | \$75,000+/month | \$900,000+/year"
    echo "🌍 Global Multi-Platform Integration with 24/7 Autonomous Operation"
    echo "🇮🇩 Created with ❤️ by Mulky Malikul Dhaher in Indonesia"
    echo ""
    echo "📊 COMPREHENSIVE AGENT ECOSYSTEM (8 Agents):"
    echo "   📈 Economic Analysis Agent     - Market Intelligence & Forecasting"
    echo "   💹 Smart Money Trading Agent   - ICT & Smart Money Concepts"
    echo "   ⚡ Trading Execution Agent     - Real-Time Order Management"
    echo "   📊 Fundamental Analysis Agent  - Deep Financial Research"
    echo "   ⛏️  Web3 Mining Agent          - Cryptocurrency & DeFi Automation"
    echo "   🏭 Agent Creator Agent         - AI Agent Factory"
    echo "   🖱️  PTC Click Agent            - Automated Click Earnings"
    echo "   🪂 Airdrop Agent              - Multi-Chain Airdrop Farming"
    echo ""
    echo "================================================================================"
    echo -e "${NC}"
}

# Check Python version
check_python() {
    echo -e "${YELLOW}🔍 Checking Python version...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
        exit 1
    fi
    
    # Check if Python version is 3.8+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${RED}❌ Python 3.8+ required. Current version: $PYTHON_VERSION${NC}"
        exit 1
    fi
}

# Check and install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Checking and installing dependencies...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Upgrade pip
    echo -e "${BLUE}⬆️ Upgrading pip...${NC}"
    pip install --upgrade pip
    
    # Install requirements
    echo -e "${BLUE}📦 Installing requirements...${NC}"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}⚠️ requirements.txt not found. Installing basic dependencies...${NC}"
        pip install asyncio numpy pandas sqlite3 requests flask
    fi
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
}

# Create necessary directories
create_directories() {
    echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
    
    mkdir -p logs
    mkdir -p data
    mkdir -p reports
    mkdir -p src/agents
    
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Check system requirements
check_requirements() {
    echo -e "${YELLOW}🔍 Checking system requirements...${NC}"
    
    # Check available memory
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 4 ]; then
            echo -e "${YELLOW}⚠️ Warning: Less than 4GB RAM detected. Performance may be affected.${NC}"
        else
            echo -e "${GREEN}✅ Memory: ${MEMORY_GB}GB RAM available${NC}"
        fi
    fi
    
    # Check disk space
    if command -v df &> /dev/null; then
        DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
        echo -e "${GREEN}✅ Disk space: $DISK_SPACE available${NC}"
    fi
    
    # Check internet connection
    if ping -c 1 google.com &> /dev/null; then
        echo -e "${GREEN}✅ Internet connection: Active${NC}"
    else
        echo -e "${RED}❌ Internet connection required for optimal performance${NC}"
    fi
}

# Start the ecosystem
start_ecosystem() {
    echo -e "${PURPLE}🚀 Starting Autonomous Money-Making Ecosystem...${NC}"
    echo ""
    echo -e "${CYAN}💰 INITIALIZING INCOME GENERATION SYSTEM...${NC}"
    echo -e "${CYAN}📊 Loading all 8 specialized agents...${NC}"
    echo -e "${CYAN}⚡ Preparing for 24/7 autonomous operation...${NC}"
    echo ""
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the main system
    if [ -f "autonomous_money_making_ecosystem.py" ]; then
        $PYTHON_CMD autonomous_money_making_ecosystem.py
    else
        echo -e "${RED}❌ Main ecosystem file not found!${NC}"
        echo -e "${YELLOW}Please ensure autonomous_money_making_ecosystem.py exists${NC}"
        exit 1
    fi
}

# Handle interrupt signal
cleanup() {
    echo -e "\n${YELLOW}🛑 Gracefully shutting down ecosystem...${NC}"
    echo -e "${GREEN}✅ Shutdown complete. Thank you for using the Autonomous Money-Making Ecosystem!${NC}"
    exit 0
}

# Set trap for interrupt signal
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_banner
    
    echo -e "${BLUE}🔄 System initialization starting...${NC}"
    echo ""
    
    check_python
    create_directories
    install_dependencies
    check_requirements
    
    echo ""
    echo -e "${GREEN}✅ All prerequisites satisfied!${NC}"
    echo -e "${PURPLE}🚀 Ready to start the money-making ecosystem!${NC}"
    echo ""
    
    # Ask for confirmation
    read -p "$(echo -e ${CYAN}"🎯 Start the Autonomous Money-Making Ecosystem? (y/N): "${NC})" -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_ecosystem
    else
        echo -e "${YELLOW}✋ Startup cancelled by user${NC}"
        exit 0
    fi
}

# Help function
show_help() {
    echo "🚀 Autonomous Money-Making Ecosystem Startup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --no-deps      Skip dependency installation"
    echo "  --check-only   Only check requirements, don't start"
    echo ""
    echo "Examples:"
    echo "  $0                 # Normal startup"
    echo "  $0 --check-only    # Check requirements only"
    echo "  $0 --no-deps       # Skip dependency installation"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --check-only)
        print_banner
        check_python
        check_requirements
        echo -e "${GREEN}✅ System check complete${NC}"
        exit 0
        ;;
    --no-deps)
        print_banner
        check_python
        create_directories
        check_requirements
        start_ecosystem
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac