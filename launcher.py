#!/usr/bin/env python3
"""Unified Launcher for Ultimate AGI Force.

Usage:
    python launcher.py --mode <cli|web|termux|autonomous|daemon>
If --mode is omitted it prompts interactively.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import sys
from typing import Callable

from src.core.launcher_base import LauncherBase


class UnifiedLauncher(LauncherBase):  # noqa: D101
    def __init__(self):
        super().__init__()
        self.ensure_min_dependencies()
        self.banner()

    # --------------------------------------------------------------
    def _run_ecosystem_mode(self, mode: str):  # noqa: D401, ANN001
        """Delegate to EcosystemManager async methods (cli/web/termux)."""
        try:
            mod = importlib.import_module("UNIFIED_ECOSYSTEM_LAUNCHER")
            manager = mod.EcosystemManager()
            self.logger.info("Launching EcosystemManager mode: %s", mode)
            coro = getattr(manager, f"launch_{mode}_mode")()
            self.run_async(coro)
        except Exception as exc:
            self.logger.error("Failed to launch %s mode: %s", mode, exc, exc_info=False)

    # --------------------------------------------------------------
    def mode_cli(self):  # noqa: D401
        self._run_ecosystem_mode("cli")

    def mode_web(self):  # noqa: D401
        self._run_ecosystem_mode("web")

    def mode_termux(self):  # noqa: D401
        self._run_ecosystem_mode("termux")

    # --------------------------------------------------------------
    def mode_autonomous(self):  # noqa: D401
        """Start Autonomous Execution Engine."""
        try:
            mod = importlib.import_module("AUTONOMOUS_EXECUTION_ENGINE")
            engine = mod.AutonomousExecutionEngine()
            self.logger.info("Starting Autonomous Execution Engine …")
            self.run_async(engine.main_execution_loop())
        except Exception as exc:
            self.logger.error("Autonomous engine failed: %s", exc, exc_info=False)

    # --------------------------------------------------------------
    def mode_daemon(self):  # noqa: D401
        """Start daemon manager (file: daemon_manager.py)."""
        try:
            mod = importlib.import_module("daemon_manager")
            self.run_async(mod.run_daemon())  # type: ignore[attr-defined]
        except Exception as exc:
            self.logger.error("Daemon manager failed: %s", exc, exc_info=False)

    # --------------------------------------------------------------
    def interactive_menu(self):  # noqa: D401
        print("\nSelect launch mode:")
        modes = [
            ("CLI", "cli"),
            ("Web UI", "web"),
            ("Termux", "termux"),
            ("Autonomous Engine", "autonomous"),
            ("Background Daemon", "daemon"),
        ]
        for idx, (label, _) in enumerate(modes, 1):
            print(f"  {idx}. {label}")
        choice = input("Enter choice [1-5]: ").strip()
        try:
            idx = int(choice) - 1
            _, mode_key = modes[idx]
        except Exception:  # pragma: no cover
            print("Invalid choice; exiting.")
            sys.exit(1)
        getattr(self, f"mode_{mode_key}")()


# ----------------------------------------------------------------------

def main():  # noqa: D401
    parser = argparse.ArgumentParser(description="Unified Launcher for Ultimate AGI Force")
    parser.add_argument("--mode", choices=["cli", "web", "termux", "autonomous", "daemon"], help="Launch mode")
    args = parser.parse_args()

    launcher = UnifiedLauncher()

    if args.mode:
        getattr(launcher, f"mode_{args.mode}")()
    else:
        launcher.interactive_menu()


if __name__ == "__main__":
    main()

