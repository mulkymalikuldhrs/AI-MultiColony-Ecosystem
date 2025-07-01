#!/usr/bin/env bash

# Agentic AI Indonesia - Termux Installation Script
# Version: 6.0.0-indonesia
# Target: Android devices running Termux
# Created by: Mulky Malikul Dhaher

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Indonesian flag colors
MERAH='\033[1;31m'
PUTIH='\033[1;37m'

echo -e "${MERAH}🇮🇩================================🇮🇩${NC}"
echo -e "${PUTIH}   Agentic AI Indonesia v6.0.0     ${NC}"
echo -e "${MERAH}   Mobile-First AI Revolution      ${NC}"
echo -e "${PUTIH}   Installer untuk Termux Android  ${NC}"
echo -e "${MERAH}🇮🇩================================🇮🇩${NC}"
echo

# Check if running on Termux
if [[ ! "$PREFIX" == *"com.termux"* ]]; then
    echo -e "${RED}❌ Error: Script ini hanya bisa dijalankan di Termux!${NC}"
    echo -e "${YELLOW}📱 Silakan install Termux dari F-Droid dan coba lagi.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Memeriksa sistem requirements...${NC}"

# Check Android version
if command -v termux-info >/dev/null 2>&1; then
    ANDROID_VERSION=$(termux-info | grep "Android version" | cut -d':' -f2 | tr -d ' ')
    echo -e "${GREEN}✅ Android version: $ANDROID_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Tidak dapat mendeteksi versi Android${NC}"
fi

# Check available RAM
if [ -f /proc/meminfo ]; then
    TOTAL_RAM=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
    echo -e "${GREEN}✅ RAM tersedia: ${TOTAL_RAM}GB${NC}"
    
    if [ "$TOTAL_RAM" -lt 4 ]; then
        echo -e "${YELLOW}⚠️  WARNING: RAM kurang dari 4GB. Performa mungkin terbatas.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Tidak dapat mendeteksi jumlah RAM${NC}"
fi

# Check storage
AVAILABLE_STORAGE=$(df -h $PREFIX | awk 'NR==2{print $4}')
echo -e "${GREEN}✅ Storage tersedia: $AVAILABLE_STORAGE${NC}"

echo
echo -e "${CYAN}🚀 Memulai instalasi Agentic AI Indonesia...${NC}"
echo

# Update package lists
echo -e "${BLUE}📦 Updating package lists...${NC}"
pkg update -y

# Upgrade existing packages
echo -e "${BLUE}⬆️  Upgrading existing packages...${NC}"
pkg upgrade -y

# Install essential packages
echo -e "${BLUE}🔧 Installing essential packages...${NC}"
pkg install -y \
    git \
    python \
    rust \
    nodejs \
    cmake \
    clang \
    make \
    pkg-config \
    openssl \
    libffi \
    zlib \
    libjpeg-turbo \
    libpng \
    freetype \
    wget \
    curl

# Setup storage access
echo -e "${BLUE}📁 Setting up storage access...${NC}"
if [ ! -d "$HOME/storage" ]; then
    termux-setup-storage
    echo -e "${GREEN}✅ Storage access configured${NC}"
else
    echo -e "${GREEN}✅ Storage access already configured${NC}"
fi

# Create project directory
echo -e "${BLUE}📂 Creating project directory...${NC}"
PROJECT_DIR="$HOME/agentic-ai-indonesia"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    echo -e "${GREEN}✅ Project directory created: $PROJECT_DIR${NC}"
else
    echo -e "${GREEN}✅ Project directory exists: $PROJECT_DIR${NC}"
fi

cd "$PROJECT_DIR"

# Install Python dependencies
echo -e "${BLUE}🐍 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install \
    requests \
    flask \
    fastapi \
    uvicorn \
    websockets \
    aiohttp \
    pydantic \
    sqlalchemy \
    alembic \
    cryptography \
    bcrypt \
    jwt \
    numpy \
    pandas \
    scikit-learn \
    torch \
    transformers \
    accelerate \
    datasets \
    langchain \
    langchain-community \
    chromadb \
    faiss-cpu \
    sentence-transformers \
    openai \
    anthropic \
    google-generativeai \
    mistralai \
    groq \
    cohere \
    huggingface-hub \
    speechrecognition \
    pydub \
    gtts \
    pygame \
    opencv-python \
    pillow \
    matplotlib \
    seaborn \
    plotly \
    streamlit \
    gradio \
    chainlit

# Install Node.js dependencies for web interface
echo -e "${BLUE}🌐 Installing Node.js dependencies...${NC}"
if [ ! -f "package.json" ]; then
    cat > package.json << 'EOF'
{
  "name": "agentic-ai-indonesia",
  "version": "6.0.0-indonesia",
  "description": "Platform AI Agentic Pertama di Indonesia - Mobile-First",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.7.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "compression": "^1.7.4",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "axios": "^1.5.0",
    "multer": "^1.4.5-lts.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "ws": "^8.13.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "keywords": ["ai", "agentic", "indonesia", "mobile", "termux", "android"],
  "author": "Mulky Malikul Dhaher",
  "license": "MIT"
}
EOF
fi

npm install

# Download optimized AI models for ARM64
echo -e "${BLUE}🤖 Downloading optimized AI models...${NC}"
MODELS_DIR="$PROJECT_DIR/models"
mkdir -p "$MODELS_DIR"

# Download Indonesian language models
echo -e "${BLUE}🇮🇩 Downloading Indonesian language models...${NC}"
python3 -c "
import torch
from transformers import AutoTokenizer, AutoModel
import os

models_dir = '$MODELS_DIR'
os.makedirs(models_dir, exist_ok=True)

# Download Indonesian BERT model
print('Downloading Indonesian BERT...')
tokenizer = AutoTokenizer.from_pretrained('indolem/indobert-base-uncased')
model = AutoModel.from_pretrained('indolem/indobert-base-uncased')
tokenizer.save_pretrained(f'{models_dir}/indobert')
model.save_pretrained(f'{models_dir}/indobert')

# Download Indonesian T5 model for generation
print('Downloading Indonesian T5...')
from transformers import T5Tokenizer, T5ForConditionalGeneration
t5_tokenizer = T5Tokenizer.from_pretrained('Wikidepia/IndoT5-base')
t5_model = T5ForConditionalGeneration.from_pretrained('Wikidepia/IndoT5-base')
t5_tokenizer.save_pretrained(f'{models_dir}/indot5')
t5_model.save_pretrained(f'{models_dir}/indot5')

print('✅ Indonesian models downloaded successfully!')
"

# Create environment configuration
echo -e "${BLUE}⚙️  Creating environment configuration...${NC}"
cat > .env << 'EOF'
# Agentic AI Indonesia Configuration
# Mobile-First AI Revolution v6.0.0

# System Configuration
AGENTIC_AI_VERSION=6.0.0-indonesia
AGENTIC_AI_MODE=mobile
AGENTIC_AI_LANG=id
AGENTIC_AI_REGION=indonesia
AGENTIC_AI_PLATFORM=termux

# Performance Settings
MAX_MEMORY_MB=2048
MAX_CPU_CORES=4
ENABLE_GPU=false
OFFLINE_MODE=true
EDGE_PROCESSING=true

# Voice Settings
VOICE_ENABLED=true
VOICE_LANG=id-ID
VOICE_ACTIVATION=["Halo Agen AI", "Hey AI Indonesia"]
VOICE_RESPONSE_LANG=id

# AI Models
INDONESIAN_MODEL_PATH=./models/indobert
GENERATION_MODEL_PATH=./models/indot5
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Indonesian Business Integration
ENABLE_ECOMMERCE_INTEGRATION=true
ENABLE_PAYMENT_INTEGRATION=true
ENABLE_GOVERNMENT_APIS=false
ENABLE_BANKING_APIS=false

# Security
ENABLE_ENCRYPTION=true
ENCRYPTION_KEY=your_32_character_encryption_key_here
LOCAL_AUTH_ONLY=true
NO_CLOUD_UPLOAD=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/agentic-ai.log
ENABLE_ANALYTICS=true
ANALYTICS_LOCAL_ONLY=true

# API Keys (Optional - untuk fitur cloud)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# GOOGLE_API_KEY=your_google_key_here
EOF

# Create main application file
echo -e "${BLUE}🚀 Creating main application...${NC}"
cat > agentic-ai-indonesia.py << 'EOF'
#!/usr/bin/env python3
"""
Agentic AI Indonesia v6.0.0 - Mobile-First AI Revolution
Platform AI Agentic Pertama di Indonesia

Created by: Mulky Malikul Dhaher
Target: Termux Android Environment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agentic-ai.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AgenticAIIndonesia:
    def __init__(self):
        self.version = "6.0.0-indonesia"
        self.mode = os.getenv('AGENTIC_AI_MODE', 'mobile')
        self.language = os.getenv('AGENTIC_AI_LANG', 'id')
        self.region = os.getenv('AGENTIC_AI_REGION', 'indonesia')
        
        logger.info(f"🇮🇩 Initializing Agentic AI Indonesia {self.version}")
        logger.info(f"Mode: {self.mode} | Language: {self.language} | Region: {self.region}")
        
    async def initialize(self):
        """Initialize all AI components"""
        try:
            # Initialize Indonesian language models
            await self._load_indonesian_models()
            
            # Setup voice recognition
            await self._setup_voice_system()
            
            # Initialize agents
            await self._initialize_agents()
            
            # Setup mobile interface
            await self._setup_mobile_interface()
            
            logger.info("✅ Agentic AI Indonesia initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _load_indonesian_models(self):
        """Load Indonesian language models"""
        logger.info("🤖 Loading Indonesian AI models...")
        # Model loading logic here
        
    async def _setup_voice_system(self):
        """Setup Indonesian voice recognition"""
        logger.info("🗣️ Setting up Indonesian voice system...")
        # Voice system setup here
        
    async def _initialize_agents(self):
        """Initialize Indonesian-specific AI agents"""
        logger.info("👥 Initializing Indonesian AI agents...")
        # Agent initialization here
        
    async def _setup_mobile_interface(self):
        """Setup mobile-optimized interface"""
        logger.info("📱 Setting up mobile interface...")
        # Mobile interface setup here
    
    async def run(self):
        """Main application loop"""
        logger.info("🚀 Starting Agentic AI Indonesia...")
        
        print("\n" + "="*50)
        print("🇮🇩 AGENTIC AI INDONESIA v6.0.0")
        print("Platform AI Agentic Pertama di Indonesia")
        print("Mobile-First AI Revolution")
        print("="*50)
        print("\n💡 Katakan 'Halo Agen AI' untuk memulai!")
        print("📱 Tekan Ctrl+C untuk keluar\n")
        
        try:
            while True:
                # Main application loop
                user_input = input("🗣️ Anda: ")
                
                if user_input.lower() in ['exit', 'quit', 'keluar']:
                    break
                    
                if user_input.lower() in ['halo agen ai', 'hey ai indonesia']:
                    print("🤖 AI: Halo! Saya Agentic AI Indonesia. Bagaimana saya bisa membantu bisnis Anda hari ini?")
                    continue
                
                # Process user input with AI
                response = await self._process_input(user_input)
                print(f"🤖 AI: {response}")
                
        except KeyboardInterrupt:
            logger.info("👋 Shutting down Agentic AI Indonesia...")
            print("\n👋 Terima kasih telah menggunakan Agentic AI Indonesia!")
    
    async def _process_input(self, text):
        """Process user input with AI"""
        # Placeholder for AI processing
        return f"Saya memahami: '{text}'. Fitur AI sedang dikembangkan untuk memberikan respons yang lebih cerdas!"

async def main():
    """Main entry point"""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and run the application
    app = AgenticAIIndonesia()
    await app.initialize()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Make the main script executable
chmod +x agentic-ai-indonesia.py

# Create startup script
echo -e "${BLUE}📝 Creating startup script...${NC}"
cat > start-agentic-ai.sh << 'EOF'
#!/usr/bin/env bash

# Agentic AI Indonesia - Startup Script
# Quick launcher for Termux

echo "🇮🇩 Starting Agentic AI Indonesia..."
echo "Platform AI Agentic Pertama di Indonesia"
echo

cd "$HOME/agentic-ai-indonesia"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Start the application
python agentic-ai-indonesia.py
EOF

chmod +x start-agentic-ai.sh

# Create desktop shortcut script
echo -e "${BLUE}🔗 Creating launcher shortcuts...${NC}"
cat > launch-ai.sh << 'EOF'
#!/usr/bin/env bash
# Quick launch from anywhere
cd "$HOME/agentic-ai-indonesia" && ./start-agentic-ai.sh
EOF

chmod +x launch-ai.sh

# Add to PATH
if ! grep -q "agentic-ai-indonesia" ~/.bashrc; then
    echo 'export PATH="$HOME/agentic-ai-indonesia:$PATH"' >> ~/.bashrc
    echo -e "${GREEN}✅ Added to PATH in ~/.bashrc${NC}"
fi

# Create alias for easy access
if ! grep -q "alias ai=" ~/.bashrc; then
    echo 'alias ai="cd $HOME/agentic-ai-indonesia && ./start-agentic-ai.sh"' >> ~/.bashrc
    echo 'alias agentic="cd $HOME/agentic-ai-indonesia && ./start-agentic-ai.sh"' >> ~/.bashrc
    echo -e "${GREEN}✅ Created aliases: 'ai' and 'agentic'${NC}"
fi

# Setup Indonesian locale
echo -e "${BLUE}🇮🇩 Setting up Indonesian locale...${NC}"
if command -v locale-gen >/dev/null 2>&1; then
    locale-gen id_ID.UTF-8
    echo 'export LANG=id_ID.UTF-8' >> ~/.bashrc
    echo 'export LC_ALL=id_ID.UTF-8' >> ~/.bashrc
else
    echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
    echo 'export LC_ALL=en_US.UTF-8' >> ~/.bashrc
fi

# Create logs directory
mkdir -p logs

echo
echo -e "${GREEN}🎉 INSTALASI BERHASIL! 🎉${NC}"
echo
echo -e "${CYAN}📱 Agentic AI Indonesia v6.0.0 siap digunakan!${NC}"
echo
echo -e "${YELLOW}🚀 Cara menjalankan:${NC}"
echo -e "   1. Restart Termux atau jalankan: ${BLUE}source ~/.bashrc${NC}"
echo -e "   2. Ketik: ${GREEN}ai${NC} atau ${GREEN}agentic${NC}"
echo -e "   3. Atau jalankan: ${BLUE}cd $PROJECT_DIR && ./start-agentic-ai.sh${NC}"
echo
echo -e "${YELLOW}🗣️ Voice Commands:${NC}"
echo -e "   • ${GREEN}\"Halo Agen AI\"${NC} - Aktivasi"
echo -e "   • ${GREEN}\"Hey AI Indonesia\"${NC} - Aktivasi alternatif"
echo
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Gunakan ${BLUE}Ctrl+C${NC} untuk keluar"
echo -e "   • Katakan ${GREEN}'keluar'${NC} untuk mengakhiri session"
echo -e "   • Check logs di: ${BLUE}$PROJECT_DIR/logs/${NC}"
echo
echo -e "${PURPLE}🇮🇩 Dibuat dengan ❤️ di Indonesia oleh Mulky Malikul Dhaher${NC}"
echo -e "${CYAN}Platform AI Agentic Pertama di Indonesia - Mobile-First AI Revolution${NC}"
echo

# Final system info
echo -e "${BLUE}📊 System Information:${NC}"
echo -e "   📁 Project path: ${GREEN}$PROJECT_DIR${NC}"
echo -e "   🐍 Python: ${GREEN}$(python --version)${NC}"
echo -e "   📦 Node.js: ${GREEN}$(node --version)${NC}"
echo -e "   💾 Available storage: ${GREEN}$AVAILABLE_STORAGE${NC}"
echo -e "   🔧 Platform: ${GREEN}Termux Android${NC}"
echo

echo -e "${MERAH}🇮🇩 Selamat menggunakan Agentic AI Indonesia! 🇮🇩${NC}"