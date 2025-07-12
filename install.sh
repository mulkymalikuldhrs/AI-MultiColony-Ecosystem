#!/bin/bash

# ╔══════════════════════════════════════════════════════════════╗
# ║                🚀 AI-MultiColony-Ecosystem v7.2.4            ║
# ║                     Unified Installer System                 ║
# ║          🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩        ║
# ╚══════════════════════════════════════════════════════════════╝

# Set colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ ${YELLOW}$1${BLUE} ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}ℹ️ $1${NC}"
}

# Check if Python 3.8+ is installed
check_python() {
    print_header "Checking Python Installation"
    
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version is installed"
        
        # Check if Python version is 3.8+
        if [[ $(echo "$python_version" | cut -d. -f1) -ge 3 && $(echo "$python_version" | cut -d. -f2) -ge 8 ]]; then
            print_success "Python version is 3.8+"
        else
            print_error "Python version must be 3.8+. Please upgrade Python and try again."
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
}

# Install core dependencies
install_core_dependencies() {
    print_header "Installing Core Dependencies"
    
    print_info "Installing Flask, Flask-SocketIO, Flask-CORS, PyYAML, Requests, and other core packages..."
    pip install flask flask-socketio flask-cors pyyaml requests aiofiles fastapi uvicorn
    
    if [ $? -eq 0 ]; then
        print_success "Core dependencies installed successfully"
    else
        print_error "Failed to install core dependencies"
        exit 1
    fi
}

# Install optional dependencies
install_optional_dependencies() {
    print_header "Installing Optional Dependencies"
    
    print_info "Installing additional packages for extended functionality..."
    
    # Network and system packages
    pip install netifaces paramiko asyncpg dnspython
    
    # AI and data science packages
    pip install arxiv nltk scikit-learn seaborn spacy
    
    # Security and utilities
    pip install pyotp whois python-nmap qrcode
    
    # Image processing
    pip install opencv-python-headless pillow
    
    # Cryptography
    pip install cryptography
    
    # Docker support (if available)
    pip install docker
    
    print_success "Optional dependencies installed successfully"
}

# Download NLTK data
download_nltk_data() {
    print_header "Downloading NLTK Data"
    
    print_info "Downloading NLTK data for natural language processing..."
    python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
    
    print_success "NLTK data downloaded successfully"
}

# Download spaCy model
download_spacy_model() {
    print_header "Downloading spaCy Model"
    
    print_info "Downloading spaCy English model..."
    python3 -m spacy download en_core_web_sm
    
    print_success "spaCy model downloaded successfully"
}

# Create necessary directories
create_directories() {
    print_header "Creating System Directories"
    
    mkdir -p logs data data/task_queue agent_output projects
    
    print_success "System directories created successfully"
}

# Configure system
configure_system() {
    print_header "Configuring System"
    
    # Create a default configuration if it doesn't exist
    if [ ! -f "config/system_config.yaml" ]; then
        mkdir -p config
        cat > config/system_config.yaml << EOL
system:
  name: "AI MultiColony Ecosystem"
  version: "7.2.4"
  owner: "Mulky Malikul Dhaher"
  owner_id: "1108151509970001"

web_interface:
  enabled: true
  port: 8080
  host: "0.0.0.0"
  debug: false

agents:
  auto_discover: true
  agents_dir: "colony/agents"
  default_status: "inactive"

llm:
  provider: "llm7"
  api_key: ""
  endpoint: "https://api.llm7.io/v1"
EOL
        print_success "Default configuration created"
    else
        print_info "Configuration file already exists, skipping"
    fi
}

# Fix permissions
fix_permissions() {
    print_header "Fixing Permissions"
    
    chmod +x main.py
    chmod +x system_analyzer.py
    
    print_success "Permissions fixed successfully"
}

# Run system analyzer
run_system_analyzer() {
    print_header "Running System Analyzer"
    
    print_info "Analyzing system health..."
    if [ -f "system_analyzer.py" ]; then
        python3 system_analyzer.py
    else
        print_info "System analyzer not found, skipping"
    fi
}

# Launch the system
launch_system() {
    print_header "Launching AI-MultiColony-Ecosystem"
    
    print_info "Starting the system with web UI..."
    python3 main.py --web-ui
}

# Main installation process
main() {
    clear
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                🚀 AI-MultiColony-Ecosystem v7.2.4            ║"
    echo "║                     Unified Installer System                 ║"
    echo "║          🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${YELLOW}This installer will set up the AI-MultiColony-Ecosystem with all dependencies.${NC}"
    echo -e "${YELLOW}The process may take several minutes depending on your internet connection.${NC}"
    echo ""
    
    read -p "Do you want to continue? (y/n): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Run installation steps
    check_python
    install_core_dependencies
    install_optional_dependencies
    download_nltk_data
    download_spacy_model
    create_directories
    configure_system
    fix_permissions
    run_system_analyzer
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                🎉 Installation Complete! 🎉                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}To launch the system, run:${NC}"
    echo -e "${BLUE}python main.py --web-ui${NC}"
    echo ""
    echo -e "${YELLOW}Or you can launch it now:${NC}"
    read -p "Launch the system now? (y/n): " launch_choice
    if [[ "$launch_choice" =~ ^[Yy]$ ]]; then
        launch_system
    else
        echo -e "${GREEN}Installation completed successfully. You can launch the system later.${NC}"
    fi
}

# Run the main function
main