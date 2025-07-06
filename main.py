#!/usr/bin/env python3
"""
🚀 AI-MultiColony-Ecosystem - Main Entry Point
Ultimate entry point that redirects to unified launcher

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Main entry point - redirect to unified launcher"""
    print("🚀 AI-MultiColony-Ecosystem v7.0.0")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")
    print("📂 Redirecting to Unified Launcher System...")
    print("="*60)
    
    try:
        from unified_launcher import main as unified_main
        import asyncio
        asyncio.run(unified_main())
    except ImportError as e:
        print(f"❌ Error importing unified launcher: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    # Ensure LLM7 public endpoint and key are always set for all agents
    os.environ["LLM7_API_KEY"] = "unused"
    os.environ["LLM7_API_BASE_URL"] = "https://api.llm7.io/v1"
    os.environ["OPENAI_API_KEY"] = "unused"
    os.environ["OPENAI_API_BASE_URL"] = "https://api.llm7.io/v1"
    main()