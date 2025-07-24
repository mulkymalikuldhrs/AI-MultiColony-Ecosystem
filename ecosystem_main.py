#!/usr/bin/env python3
"""
🌟 AGENTIC AI ECOSYSTEM - UNIVERSAL DEPLOYMENT MAIN
The Ultimate Autonomous AI System that runs everywhere

🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

Supports: Cursor, Replit, Bolt, GitPod, Codespaces, Vercel, Netlify, Local, and more!
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import core components
try:
    from agents.system_supervisor import SystemSupervisor
    from web_interface.app import app, socketio

    from ecosystem.ecosystem_orchestrator import EcosystemOrchestrator
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("📦 Installing missing dependencies...")
    # Auto-install basic dependencies if missing
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "flask", "flask-socketio"]
    )
    from web_interface.app import app, socketio


class EnvironmentDetector:
    """🔍 Detects the current deployment environment"""

    @staticmethod
    def detect() -> str:
        """Detect current environment"""
        # Environment detection logic
        env_indicators = {
            "replit": ["REPL_ID", "REPL_SLUG", "REPLIT_DB_URL"],
            "cursor": ["CURSOR_USER", "CURSOR_SESSION", "VSCODE_IPC_HOOK"],
            "bolt": ["BOLT_*", "STACKBLITZ_*"],
            "gitpod": ["GITPOD_WORKSPACE_ID", "GITPOD_WORKSPACE_URL"],
            "codespaces": ["CODESPACES", "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"],
            "colab": ["COLAB_GPU", "COLAB_TPU_ADDR"],
            "kaggle": ["KAGGLE_KERNEL_RUN_TYPE", "KAGGLE_URL_BASE"],
            "vercel": ["VERCEL", "VERCEL_URL"],
            "netlify": ["NETLIFY", "NETLIFY_BUILD_BASE"],
            "heroku": ["DYNO", "HEROKU_APP_NAME"],
            "aws": ["AWS_LAMBDA_FUNCTION_NAME", "AWS_EXECUTION_ENV"],
            "gcp": ["GOOGLE_CLOUD_PROJECT", "GAE_SERVICE"],
            "azure": ["WEBSITE_SITE_NAME", "AZURE_FUNCTIONS_ENVIRONMENT"],
        }

        for env_name, indicators in env_indicators.items():
            for indicator in indicators:
                if indicator.endswith("*"):
                    # Pattern matching
                    pattern = indicator[:-1]
                    if any(key.startswith(pattern) for key in os.environ):
                        return env_name
                elif indicator in os.environ:
                    return env_name

        # Check for Docker
        if os.path.exists("/.dockerenv"):
            return "docker"

        # Check for common cloud indicators
        if os.path.exists("/app"):
            return "cloud"

        return "local"


class UniversalDeployer:
    """🚀 Universal deployment manager for all environments"""

    def __init__(self):
        self.environment = EnvironmentDetector.detect()
        self.port = self.get_port()
        self.host = self.get_host()
        self.debug = self.get_debug_mode()

    def get_port(self) -> int:
        """Get appropriate port for environment"""
        # Environment-specific port detection
        port_env_vars = ["PORT", "HTTP_PORT", "WEB_PORT", "SERVER_PORT"]

        for var in port_env_vars:
            if var in os.environ:
                try:
                    return int(os.environ[var])
                except ValueError:
                    continue

        # Default ports by environment
        default_ports = {
            "replit": 5000,
            "cursor": 5000,
            "bolt": 3000,
            "gitpod": 8080,
            "codespaces": 8000,
            "vercel": 3000,
            "netlify": 8888,
            "heroku": 5000,
            "local": 5000,
        }

        return default_ports.get(self.environment, 5000)

    def get_host(self) -> str:
        """Get appropriate host for environment"""
        if self.environment in ["local", "cursor"]:
            return "127.0.0.1"
        return "0.0.0.0"  # Cloud environments

    def get_debug_mode(self) -> bool:
        """Get debug mode for environment"""
        if os.environ.get("DEBUG", "").lower() in ["true", "1", "yes"]:
            return True

        # Debug mode by environment
        debug_environments = ["local", "cursor", "gitpod", "codespaces"]
        return self.environment in debug_environments

    def setup_environment_specific_config(self):
        """Setup environment-specific configurations"""
        print(f"🔧 Configuring for {self.environment} environment...")

        if self.environment == "replit":
            self.setup_replit()
        elif self.environment == "cursor":
            self.setup_cursor()
        elif self.environment == "bolt":
            self.setup_bolt()
        elif self.environment == "gitpod":
            self.setup_gitpod()
        elif self.environment == "vercel":
            self.setup_vercel()
        elif self.environment == "netlify":
            self.setup_netlify()
        elif self.environment == "heroku":
            self.setup_heroku()
        else:
            self.setup_generic()

    def setup_replit(self):
        """Setup for Replit environment"""
        # Replit-specific optimizations
        os.environ.setdefault("PYTHONPATH", str(project_root))
        os.environ.setdefault("FLASK_ENV", "production")

        # Create .replit config if it doesn't exist
        if not os.path.exists(".replit"):
            replit_config = """
modules = ["python-3.11"]

[nix]
channel = "stable-24_05"

[[ports]]
localPort = 5000
externalPort = 80

[deployment]
run = ["python", "ecosystem_main.py"]
deploymentTarget = "cloudrun"

[env]
PYTHONPATH = "$PYTHONPATH:."
FLASK_APP = "ecosystem_main.py"
"""
            with open(".replit", "w") as f:
                f.write(replit_config)

        print("✅ Replit configuration optimized")

    def setup_cursor(self):
        """Setup for Cursor environment"""
        # Create VS Code configuration
        os.makedirs(".vscode", exist_ok=True)

        settings = {
            "python.defaultInterpreterPath": "/usr/bin/python3",
            "python.terminal.activateEnvironment": True,
            "files.associations": {"*.py": "python"},
        }

        try:
            import json

            with open(".vscode/settings.json", "w") as f:
                json.dump(settings, f, indent=2)
        except:
            pass

        print("✅ Cursor configuration optimized")

    def setup_bolt(self):
        """Setup for Bolt environment"""
        # Create bolt-specific configuration
        print("✅ Bolt configuration optimized")

    def setup_gitpod(self):
        """Setup for GitPod environment"""
        # Create .gitpod.yml if needed
        gitpod_config = """
tasks:
  - init: pip install -r requirements.txt
    command: python ecosystem_main.py

ports:
  - port: 5000
    onOpen: open-browser
"""
        if not os.path.exists(".gitpod.yml"):
            with open(".gitpod.yml", "w") as f:
                f.write(gitpod_config)

        print("✅ GitPod configuration optimized")

    def setup_vercel(self):
        """Setup for Vercel environment"""
        # Create vercel.json configuration
        vercel_config = """
{
  "version": 2,
  "builds": [
    {
      "src": "ecosystem_main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "ecosystem_main.py"
    }
  ]
}
"""
        if not os.path.exists("vercel.json"):
            with open("vercel.json", "w") as f:
                f.write(vercel_config)

        print("✅ Vercel configuration optimized")

    def setup_netlify(self):
        """Setup for Netlify environment"""
        print("✅ Netlify configuration optimized")

    def setup_heroku(self):
        """Setup for Heroku environment"""
        # Create Procfile if needed
        if not os.path.exists("Procfile"):
            with open("Procfile", "w") as f:
                f.write("web: python ecosystem_main.py")

        print("✅ Heroku configuration optimized")

    def setup_generic(self):
        """Setup for generic/local environment"""
        print("✅ Generic environment configuration")


async def start_ecosystem():
    """🌟 Start the complete autonomous ecosystem"""
    print("🌟" + "=" * 60 + "🌟")
    print("  🚀 AGENTIC AI ECOSYSTEM v3.0.0 - STARTING UP")
    print("  🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")
    print("  🌍 The World's First Autonomous AI Ecosystem")
    print("🌟" + "=" * 60 + "🌟")

    # Environment detection and setup
    deployer = UniversalDeployer()
    deployer.setup_environment_specific_config()

    print(f"🔍 Environment: {deployer.environment}")
    print(f"🌐 Host: {deployer.host}:{deployer.port}")
    print(f"🐛 Debug Mode: {deployer.debug}")

    # Initialize core components
    try:
        print("🧠 Initializing Ecosystem Orchestrator...")
        orchestrator = EcosystemOrchestrator()

        print("🔧 Starting System Supervisor...")
        supervisor = SystemSupervisor()

        print("✅ Core ecosystem components initialized!")

    except Exception as e:
        print(f"⚠️ Some advanced features may be limited: {e}")
        print("🔄 Starting in basic mode...")

    # Configure Flask app for environment
    configure_flask_app(deployer)

    # Start the ecosystem
    print(f"🚀 Starting Agentic AI Ecosystem...")
    print(f"📱 Access the system at: http://{deployer.host}:{deployer.port}")
    print(f"📖 Documentation: http://{deployer.host}:{deployer.port}/docs")
    print(
        f"🎨 Workflow Builder: http://{deployer.host}:{deployer.port}/workflow-builder"
    )
    print(
        f"🔌 Plugin Marketplace: http://{deployer.host}:{deployer.port}/plugin-marketplace"
    )
    print(f"📱 Mobile App: http://{deployer.host}:{deployer.port}/mobile-companion")
    print(f"📊 Analytics: http://{deployer.host}:{deployer.port}/business-intelligence")

    return deployer


def configure_flask_app(deployer: UniversalDeployer):
    """⚙️ Configure Flask app for the detected environment"""

    # Basic app configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "agentic-ai-ecosystem-secret-key"
    )
    app.config["DEBUG"] = deployer.debug

    # Environment-specific configurations
    if deployer.environment in ["vercel", "netlify"]:
        # Serverless optimizations
        app.config["PREFERRED_URL_SCHEME"] = "https"

    if deployer.environment == "replit":
        # Replit-specific settings
        app.config["SERVER_NAME"] = None  # Let Replit handle this

    # Database configuration
    db_url = os.environ.get("DATABASE_URL", f"sqlite:///{project_root}/ecosystem.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def main():
    """🎯 Main entry point"""
    try:
        # Create asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start ecosystem
        deployer = loop.run_until_complete(start_ecosystem())

        # Run the web application
        if deployer.environment in ["vercel", "netlify"]:
            # For serverless environments, return the app
            return app
        else:
            # For server environments, run with socketio
            socketio.run(
                app,
                host=deployer.host,
                port=deployer.port,
                debug=deployer.debug,
                use_reloader=False,  # Disable reloader in production
                log_output=True,
            )

    except KeyboardInterrupt:
        print("\n🛑 Ecosystem shutdown requested")
        print("👋 Thank you for using Agentic AI Ecosystem!")
        print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher")

    except Exception as e:
        print(f"❌ Error starting ecosystem: {e}")
        print("🔧 Please check your configuration and try again")
        sys.exit(1)


# Health check endpoint for cloud deployments
@app.route("/health")
def health_check():
    """🏥 Health check endpoint"""
    return {
        "status": "healthy",
        "environment": EnvironmentDetector.detect(),
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "creator": "Mulky Malikul Dhaher",
        "country": "Indonesia",
    }


# Root endpoint
@app.route("/")
def root():
    """🏠 Root endpoint"""
    return """
    <html>
    <head>
        <title>🌟 Agentic AI Ecosystem v3.0.0</title>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; text-align: center; padding: 2rem;
                margin: 0; min-height: 100vh; display: flex;
                flex-direction: column; justify-content: center;
            }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { font-size: 3rem; margin-bottom: 1rem; }
            .subtitle { font-size: 1.5rem; margin-bottom: 2rem; opacity: 0.9; }
            .links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }
            .link { background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; text-decoration: none; color: white; transition: all 0.3s; }
            .link:hover { background: rgba(255,255,255,0.2); transform: translateY(-5px); }
            .footer { margin-top: 2rem; opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 Agentic AI Ecosystem</h1>
            <div class="subtitle">The World's First Autonomous AI System</div>
            
            <div class="links">
                <a href="/workflow-builder" class="link">
                    🎨 Workflow Builder<br>
                    <small>Create AI workflows visually</small>
                </a>
                <a href="/plugin-marketplace" class="link">
                    🔌 Plugin Marketplace<br>
                    <small>Discover amazing plugins</small>
                </a>
                <a href="/mobile-companion" class="link">
                    📱 Mobile Companion<br>
                    <small>Voice-controlled AI assistant</small>
                </a>
                <a href="/business-intelligence" class="link">
                    📊 Business Intelligence<br>
                    <small>Analytics and insights</small>
                </a>
                <a href="/agents" class="link">
                    🤖 AI Agents<br>
                    <small>Manage your AI workforce</small>
                </a>
                <a href="/credentials" class="link">
                    🔐 Credentials<br>
                    <small>Secure authentication</small>
                </a>
            </div>
            
            <div class="footer">
                <p>🇮🇩 Made with ❤️ by <strong>Mulky Malikul Dhaher</strong> in Indonesia</p>
                <p>🚀 Autonomous • 🌍 Global • 🔮 Revolutionary</p>
            </div>
        </div>
    </body>
    </html>
    """


# For serverless deployments (Vercel, Netlify)
if __name__ == "__main__":
    main()
else:
    # For import-based deployments
    deployer = UniversalDeployer()
    configure_flask_app(deployer)
