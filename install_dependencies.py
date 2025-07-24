#!/usr/bin/env python3
"""
🚀 AUTONOMOUS DEPENDENCY INSTALLER
Installs only essential dependencies for system operation
"""

import os
import subprocess
import sys


def install_dependencies():
    """Install minimal required dependencies"""
    print("🚀 Installing essential dependencies...")

    # Essential packages only
    essential_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "aiohttp>=3.9.1",
        "websockets>=12.0",
        "requests>=2.31.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "psutil>=5.9.6",
        "cryptography>=41.0.7",
        "rich>=13.7.0",
        "colorama>=0.4.6",
    ]

    for package in essential_packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            continue

    print("🎉 Essential dependencies installation complete!")


if __name__ == "__main__":
    install_dependencies()
