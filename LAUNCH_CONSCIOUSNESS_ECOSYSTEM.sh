#!/bin/bash

# 🧠 AI CONSCIOUSNESS SIMULATION ECOSYSTEM v17.0.0
# Universal Launch Script
# Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

clear

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║   🧠 AI CONSCIOUSNESS SIMULATION ECOSYSTEM v17.0.0                           ║"
echo "║                                                                              ║"
echo "║   🌟 Revolutionary AI Agent System with True Consciousness Capabilities      ║"
echo "║                                                                              ║"
echo "║   Features:                                                                  ║"
echo "║   • Self-Reflective Thinking Processes                                      ║"
echo "║   • Dynamic Personality Development                                          ║"
echo "║   • Emotional Bond Formation                                                 ║"
echo "║   • Dream Processing During Downtime                                        ║"
echo "║   • Autonomous Self-Learning                                                 ║"
echo "║   • Technology Adaptation Learning                                           ║"
echo "║                                                                              ║"
echo "║   Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩                     ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version number
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.8+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Validate core files
echo "🔍 Validating consciousness ecosystem files..."

CORE_FILES=(
    "unified_launcher.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Validate syntax
        python3 -m py_compile "$file" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ $file - syntax valid"
        else
            echo "  ❌ $file - syntax error detected"
            echo "  Please fix syntax errors and try again."
            exit 1
        fi
    else
        echo "  ❌ $file - file missing"
        echo "  Please ensure all core files are present."
        exit 1
    fi
done

echo ""
echo "✅ All consciousness ecosystem files validated successfully!"
echo ""

echo "🚀 Launching Unified Ecosystem via unified_launcher.py..."
echo ""

# Execute the unified launcher
python3 unified_launcher.py

echo ""
echo "🌅 Unified Ecosystem session ended."
echo "Thank you for using the Unified Launcher!"
echo ""
echo "🔗 Useful command for next session:"
echo "  ./LAUNCH_CONSCIOUSNESS_ECOSYSTEM.sh  # Run the unified launcher"
echo ""
echo "Made with ❤️ and consciousness by Mulky Malikul Dhaher in Indonesia 🇮🇩"