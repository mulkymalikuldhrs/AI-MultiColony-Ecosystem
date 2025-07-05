"""launcher_base.py
Shared helper class for the unified launcher.
Contains utilities for:
• Directory preparation (logs / output)
• Logging configuration (single root logger)
• Minimal dependency bootstrap (pip install -r requirements_min.txt)

All launch modes import `LauncherBase` to reuse these helpers.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List

ROOT_DIR = Path(__file__).resolve().parents[2]  # project root (src/core/..)
LOG_DIR = ROOT_DIR / "logs"
OUTPUT_DIR = ROOT_DIR / "agent_output"

REQUIREMENTS_MIN = ROOT_DIR / "requirements_min.txt"

class LauncherBase:  # noqa: D101
    def __init__(self) -> None:
        self.start_time = datetime.now()
        self.prepare_directories()
        self.logger = self.configure_logging()

    # ---------------------------------------------------------------------
    def prepare_directories(self) -> None:  # noqa: D401
        """Ensure common directories exist."""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def configure_logging(self) -> logging.Logger:  # noqa: D401
        """Set up root logger for entire ecosystem."""
        log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        logfile = LOG_DIR / "colony_activity.log"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(logfile),
                logging.StreamHandler(sys.stdout),
            ],
        )
        logger = logging.getLogger("UnifiedLauncher")
        logger.info("🚀 Unified Launcher started at %s", self.start_time.isoformat())
        return logger

    # ------------------------------------------------------------------
    def ensure_min_dependencies(self) -> None:  # noqa: D401
        """Try to install minimal requirements at runtime (best-effort)."""
        if not REQUIREMENTS_MIN.exists():
            self.logger.warning("requirements_min.txt not found – skipping auto-install")
            return

        # Attempt to import a core package (requests) to decide if we need install
        try:
            import requests  # type: ignore  # noqa: F401
            return  # already present
        except Exception:  # pragma: no cover
            self.logger.info("Installing minimal dependencies from %s", REQUIREMENTS_MIN)
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", "-r", str(REQUIREMENTS_MIN)]
                )
                self.logger.info("✅ Dependencies installed")
            except subprocess.CalledProcessError as exc:
                self.logger.warning("⚠️  Auto-install failed: %s", exc)

    # ------------------------------------------------------------------
    @staticmethod
    def run_async(coro):  # noqa: ANN001, D401
        """Helper to run async coroutine from sync context."""
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError:
            return asyncio.run(coro)

    # ------------------------------------------------------------------
    def banner(self) -> None:  # noqa: D401
        """Print startup banner."""
        print(
            """
╔══════════════════════════════════════════════════════════════╗
║                   🚀  ULTIMATE AGI FORCE  🚀                 ║
╚══════════════════════════════════════════════════════════════╝
            """
        )