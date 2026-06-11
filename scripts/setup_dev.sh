#!/bin/bash
# Development setup script for AI MultiColony Ecosystem

set -e

echo "=== AI MultiColony Ecosystem - Development Setup ==="

# Create data directory
mkdir -p data
mkdir -p data/chroma

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -e ".[dev]"

# Install optional dependencies
echo "Installing optional dependencies..."
pip install -e ".[all]" 2>/dev/null || echo "Some optional dependencies skipped"

# Install Playwright browsers (optional)
echo "Installing Playwright browsers..."
playwright install chromium 2>/dev/null || echo "Playwright browser install skipped (optional)"

# Verify installation
echo ""
echo "Verifying installation..."
python -c "
from ai_multicolony.mcp import MCPServer, MCPClient
from ai_multicolony.memory import MemoryManager, VectorStore
from ai_multicolony.colony import ColonyManager
from ai_multicolony.browser import StealthBrowser
from ai_multicolony.sandbox import DockerSandbox
from ai_multicolony.security import SecurityAnalyzer
from ai_multicolony.api import create_app
from ai_multicolony.channels import BaseChannel
print('All modules imported successfully!')
" || echo "Warning: Some modules could not be imported"

echo ""
echo "Setup complete! Run 'make api' to start the API server."
echo "Run 'make help' to see available commands."
