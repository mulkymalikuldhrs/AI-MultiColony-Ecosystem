#!/usr/bin/env python3
"""
🔧 Quick Fix Script untuk Agentic AI System
Script untuk memperbaiki masalah yang tersisa setelah perbaikan utama

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🔧 AGENTIC AI QUICK FIX 🔧                            ║
║                                                                              ║
║                    Memperbaiki Masalah yang Tersisa                         ║
║                                                                              ║
║               🐛 Dependencies | 🔧 DevEngine Fix                             ║
║               📦 Installation | ✅ System Check                              ║
║                                                                              ║
║                Made with ❤️ by Mulky Malikul Dhaher 🇮🇩                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing missing dependencies...")
    
    dependencies = [
        "aiohttp>=3.9.1",
        "flask>=3.0.0",
        "flask-socketio>=5.3.6",
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "psutil>=5.9.6",
        "cryptography>=41.0.8"
    ]
    
    for dep in dependencies:
        try:
            print(f"  📥 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"  ✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All dependencies installed!")
    return True

def fix_dev_engine_error():
    """Fix the DevEngine missing method error"""
    print("🔧 Fixing DevEngine error...")
    
    dev_engine_file = Path("agents/dev_engine.py")
    
    if not dev_engine_file.exists():
        print("  ❌ DevEngine file not found!")
        return False
    
    # Read current content
    try:
        with open(dev_engine_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if method already exists
        if '_get_nextjs_package_json' in content:
            print("  ✅ Method already exists, no fix needed")
            return True
        
        # Add the missing method
        missing_method = '''
    def _get_nextjs_package_json(self, project_name: str) -> Dict[str, Any]:
        """Get package.json configuration for Next.js project"""
        return {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.4",
                "react": "^18",
                "react-dom": "^18"
            },
            "devDependencies": {
                "eslint": "^8",
                "eslint-config-next": "14.0.4",
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "typescript": "^5"
            }
        }
'''
        
        # Find a good place to insert the method (before the last method or class end)
        insert_position = content.rfind('# Global instance')
        
        if insert_position == -1:
            # Fallback: insert before class end
            insert_position = content.rfind('class DevEngineAgent:')
            if insert_position != -1:
                # Find end of class
                class_end = content.find('\n\n# ', insert_position)
                if class_end != -1:
                    insert_position = class_end
                else:
                    insert_position = len(content) - 100  # Near end
        
        # Insert the method
        new_content = content[:insert_position] + missing_method + '\n' + content[insert_position:]
        
        # Write back
        with open(dev_engine_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("  ✅ DevEngine missing method added successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to fix DevEngine: {e}")
        return False

def test_system():
    """Test if the system works after fixes"""
    print("🧪 Testing system...")
    
    try:
        # Test core imports
        print("  🔍 Testing core imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "from core import prompt_master, llm_client_available; print('Core OK')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Core imports working")
        else:
            print(f"  ❌ Core import failed: {result.stderr}")
            return False
        
        # Test agent imports
        print("  🔍 Testing agent imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "from agents import AGENTS_REGISTRY; print(f'Agents: {len(AGENTS_REGISTRY)}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"  ✅ Agent imports working: {result.stdout.strip()}")
        else:
            print(f"  ❌ Agent import failed: {result.stderr}")
            return False
        
        # Test main system
        print("  🔍 Testing main system boot...")
        result = subprocess.run([
            sys.executable, "main.py", "test system"
        ], capture_output=True, text=True, timeout=30)
        
        if "RUNNING" in result.stdout:
            print("  ✅ Main system boots successfully")
            return True
        else:
            print(f"  ❌ Main system test failed: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"  ❌ System test failed: {e}")
        return False

def create_env_template():
    """Create environment template file"""
    print("📄 Creating environment template...")
    
    env_template = """# 🌍 Environment Configuration for Agentic AI System
# Copy this file to .env and fill in your API keys

# LLM Provider API Keys (Optional - system works without these)
LLM7_API_KEY=public-key
CAMEL_API_KEY=public-access
OPENROUTER_API_KEY=your-openrouter-key-here

# Database Configuration
DATABASE_URL=sqlite:///data/agentic.db
REDIS_URL=redis://localhost:6379/0

# Web Interface
WEB_INTERFACE_PORT=5000
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO

# 🚀 Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""
    
    try:
        with open(".env.template", "w") as f:
            f.write(env_template)
        print("  ✅ Environment template created: .env.template")
        
        # Create .env if it doesn't exist
        if not Path(".env").exists():
            with open(".env", "w") as f:
                f.write(env_template)
            print("  ✅ Default .env file created")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to create env template: {e}")
        return False

def main():
    """Main fix routine"""
    print_header()
    
    print("🚀 Starting Agentic AI System Quick Fix...")
    print("=" * 60)
    
    success_count = 0
    total_fixes = 4
    
    # 1. Install dependencies
    if install_dependencies():
        success_count += 1
    
    # 2. Fix DevEngine error
    if fix_dev_engine_error():
        success_count += 1
    
    # 3. Create environment template
    if create_env_template():
        success_count += 1
    
    # 4. Test system
    if test_system():
        success_count += 1
    
    print("=" * 60)
    print(f"🎯 Fix Results: {success_count}/{total_fixes} successful")
    
    if success_count == total_fixes:
        print("""
✅ SEMUA PERBAIKAN BERHASIL!

🚀 Sistem Agentic AI siap digunakan:

   📚 Baca laporan lengkap: PERBAIKAN_SISTEM_REPORT.md
   🏃 Jalankan sistem: python3 main.py
   🎮 Mode interaktif: python3 main.py
   🌐 Web interface: http://localhost:5000

🎉 Selamat! Sistem telah diperbaiki dengan sukses!
        """)
    else:
        print(f"""
⚠️ BEBERAPA PERBAIKAN GAGAL ({total_fixes - success_count} issues)

❌ Silakan periksa error di atas dan perbaiki manual.
📚 Baca PERBAIKAN_SISTEM_REPORT.md untuk detail lengkap.

💡 Tips:
   - Pastikan Python 3.8+ terinstall
   - Periksa koneksi internet untuk install dependencies
   - Jalankan dengan administrator privileges jika diperlukan
        """)
    
    print("\n🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia")

if __name__ == "__main__":
    main()