#!/bin/bash
# 🛡️ Ultimate AGI Force - Service Installer
# Install AGI Force as system service for autonomous operation
# Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Current directory
CURRENT_DIR=$(pwd)
SERVICE_NAME="agi-force"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo -e "${BLUE}🛡️ Ultimate AGI Force Service Installer v7.0.0${NC}"
echo -e "${BLUE}🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   echo "Usage: sudo bash install_service.sh"
   exit 1
fi

# Create service file
echo -e "${YELLOW}📝 Creating systemd service file...${NC}"
cat > $SERVICE_FILE << EOF
[Unit]
Description=Ultimate AGI Force - Autonomous AI Agent System
Documentation=https://github.com/mulkymalikuldhrtech/Agentic-AI-Ecosystem
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=forking
User=root
Group=root
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/daemon_manager.py start
ExecStop=/usr/bin/python3 $CURRENT_DIR/daemon_manager.py stop
ExecReload=/usr/bin/python3 $CURRENT_DIR/daemon_manager.py restart
PIDFile=$CURRENT_DIR/data/daemons/agi_force.pid
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/data/logs/service.log
StandardError=append:$CURRENT_DIR/data/logs/service.log
Environment=PYTHONPATH=$CURRENT_DIR
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service file created: $SERVICE_FILE${NC}"

# Create directories
echo -e "${YELLOW}📁 Creating required directories...${NC}"
mkdir -p "$CURRENT_DIR/data/daemons"
mkdir -p "$CURRENT_DIR/data/logs"
chmod 755 "$CURRENT_DIR/data"
chmod 755 "$CURRENT_DIR/data/daemons"
chmod 755 "$CURRENT_DIR/data/logs"

# Make daemon_manager.py executable
chmod +x "$CURRENT_DIR/daemon_manager.py"

# Reload systemd
echo -e "${YELLOW}🔄 Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable service
echo -e "${YELLOW}⚙️ Enabling AGI Force service...${NC}"
systemctl enable $SERVICE_NAME

echo -e "${GREEN}✅ AGI Force service installed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Service Management Commands:${NC}"
echo -e "  ${YELLOW}Start:${NC}   sudo systemctl start $SERVICE_NAME"
echo -e "  ${YELLOW}Stop:${NC}    sudo systemctl stop $SERVICE_NAME"
echo -e "  ${YELLOW}Status:${NC}  sudo systemctl status $SERVICE_NAME"
echo -e "  ${YELLOW}Logs:${NC}    sudo journalctl -u $SERVICE_NAME -f"
echo -e "  ${YELLOW}Restart:${NC} sudo systemctl restart $SERVICE_NAME"
echo ""
echo -e "${BLUE}🌐 Web Interface:${NC} http://localhost:5000"
echo -e "${BLUE}📊 Dashboard:${NC}     http://localhost:5000/dashboard"
echo ""
echo -e "${GREEN}🚀 To start AGI Force now: sudo systemctl start $SERVICE_NAME${NC}"
echo -e "${GREEN}🔄 To start on boot:      sudo systemctl enable $SERVICE_NAME${NC}"
