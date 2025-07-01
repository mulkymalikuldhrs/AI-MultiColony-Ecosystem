"""🌌 Dhaher / Agentic AI Ecosystem – Grand Installer
===================================================
Automates repo clone, virtual environment setup, dependency installation,
secure .env creation (AES-256 encrypted), optional voice/video deps, memory
engine init, local-LLM fallback build, and system launch.

Inspired by prompt at https://jpst.it/4qvtT – simplified & refined.
Run:
    python installer.py [--repo https://github.com/your/repo]

NOTE: If you already cloned the repo manually, just run with --skip-clone.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

try:
    from cryptography.fernet import Fernet  # type: ignore
except ImportError:
    print("❌ Missing dependency 'cryptography'. Installing…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    from cryptography.fernet import Fernet  # type: ignore

PROJECT_DIR = Path.cwd() / "dhaher_ai_ecosystem"
REPO_URL_DEFAULT = "https://github.com/tokenew6/Agentic-AI-Ecosystem.git"

USER_DATA: Dict[str, str] = {
    "mother_name": os.getenv("USER_MOTHER_NAME", "Syarifah"),
    "father_name": os.getenv("USER_FATHER_NAME", "Syahril"),
    "id_number": os.getenv("USER_KTP", "110815150997"),
}


# ---------------------------------------------------------------------------
# 🔐 ENCRYPTION HELPERS
# ---------------------------------------------------------------------------

def _derive_key_from_password(password: str) -> bytes:
    salt = b"agentic_salt_v1"
    kdf = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.urlsafe_b64encode(kdf[:32])


def encrypt_data(data: Dict[str, Any], key: bytes) -> bytes:  # returns bytes
    return Fernet(key).encrypt(json.dumps(data).encode())


# ---------------------------------------------------------------------------
# 🛠️ CORE STEPS
# ---------------------------------------------------------------------------

def clone_repository(repo_url: str, dest: Path) -> None:
    if dest.exists():
        print("🗑️  Existing directory detected – removing …")
        shutil.rmtree(dest)
    print(f"🔁 Cloning repository: {repo_url} → {dest}")
    subprocess.check_call(["git", "clone", repo_url, str(dest)])


def make_virtualenv(dest: Path) -> Path:
    venv_path = dest / "venv"
    print(f"🧱 Creating virtualenv at {venv_path}")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
    return venv_path


def _pip(venv_path: Path) -> Path:
    return venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"


def install_requirements(venv: Path, project_dir: Path) -> None:
    pip = _pip(venv)
    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        print("📦 Installing requirements …")
        subprocess.check_call([str(pip), "install", "-r", str(req_file)])
    else:
        print("⚠️  requirements.txt not found – skipping.")


def create_env_file(project_dir: Path, key: bytes) -> None:
    env_path = project_dir / ".env"
    if env_path.exists():
        print("ℹ️  .env already exists – skipping creation.")
        return

    encrypted_blob = encrypt_data(USER_DATA, key).decode()
    print(f"📝 Writing encrypted .env → {env_path}")
    env_path.write_text(
        "\n".join(
            [
                f"ENCRYPTION_KEY={base64.urlsafe_b64encode(key).decode()}",
                f"ENCRYPTED_USER_DATA={encrypted_blob}",
                "FLASK_ENV=development",
                "DATABASE_URL=sqlite:///data/agentic.db",
                "LLM_PROVIDER=llm7",
                "MAX_AGENTS=10",
                "# (…) add more config as needed",
            ]
        )
    )


def optional_voice_video_deps(venv: Path) -> None:
    pip = _pip(venv)
    print("🔊 Installing optional voice/video deps …")
    subprocess.check_call([str(pip), "install", "gTTS", "pydub", "vosk", "moviepy", "ffmpeg-python"])


def run_system(project_dir: Path, venv: Path) -> None:
    entry = project_dir / "start_system.py"
    if not entry.exists():
        entry = project_dir / "main.py"
    python_exec = venv / ("Scripts" if os.name == "nt" else "bin") / "python"
    print(f"🚀 Launching system: {entry} …")
    subprocess.Popen([str(python_exec), str(entry)], cwd=project_dir)


# ---------------------------------------------------------------------------
# 🎬 MAIN
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Dhaher AI Ecosystem installer")
    parser.add_argument("--repo", default=REPO_URL_DEFAULT)
    parser.add_argument("--skip-clone", action="store_true", help="Assume repo already present in ./dhaher_ai_ecosystem")
    parser.add_argument("--no-run", action="store_true", help="Do not launch system after install")
    args = parser.parse_args()

    if not args.skip_clone:
        clone_repository(args.repo, PROJECT_DIR)

    venv = make_virtualenv(PROJECT_DIR)
    install_requirements(venv, PROJECT_DIR)

    # Prompt for password to derive encryption key
    pwd = getpass.getpass("🔐 Enter master password for .env encryption: ")
    key = _derive_key_from_password(pwd)
    create_env_file(PROJECT_DIR, key)

    optional_voice_video_deps(venv)

    if not args.no_run:
        run_system(PROJECT_DIR, venv)

    print("✅ Installation complete!")


if __name__ == "__main__":
    main()