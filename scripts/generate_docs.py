import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path to allow importing from 'colony'
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from colony.core.agent_registry import AGENT_INFO, get_all_agents, list_all_agents

DOCS_DIR = ROOT_DIR / "docs"
AGENT_DOC = DOCS_DIR / "AGENT_REGISTRY.md"
README = DOCS_DIR / "README.md"
CHANGELOG = DOCS_DIR / "CHANGELOG.md"


# 1. Generate AGENT_REGISTRY.md (robust table)
def generate_agent_registry():
    if not AGENT_INFO:
        print("Agent registry is empty. Cannot generate docs.")
        return
    DOCS_DIR.mkdir(exist_ok=True)
    with open(AGENT_DOC, "w") as f:
        f.write("# Agent Registry\n\n")
        f.write("This file is auto-generated. Do not edit manually.\n\n")
        f.write(f"Total agents registered: **{len(list_all_agents())}**\n\n")
        f.write("| Agent Name | Description | Route | Dependencies |\n")
        f.write("|------------|-------------|-------|--------------|\n")
        sorted_agents = sorted(AGENT_INFO.items())
        for agent_name, agent_data in sorted_agents:
            metadata = agent_data.get("metadata", {})
            name = metadata.get("name", agent_name)
            description = metadata.get("description", "N/A").replace("\n", " ").strip()
            route = f'`{metadata.get("route", "N/A")}`'
            dependencies = ", ".join(metadata.get("dependencies", []))
            f.write(f"| **{name}** | {description} | {route} | {dependencies} |\n")
    print(f"[DOC] Updated {AGENT_DOC}")


# 2. Update README.md (status, agent, endpoint)
def update_readme():
    agents = get_all_agents()
    if not README.exists():
        print(f"[WARN] {README} not found, skipping update.")
        return
    with open(README, "r") as f:
        lines = f.readlines()
    start = end = None
    for i, line in enumerate(lines):
        if line.strip() == "<!-- AGENT_LIST_START -->":
            start = i
        if line.strip() == "<!-- AGENT_LIST_END -->":
            end = i
    if start is not None and end is not None:
        agent_lines = [f"- {name}\n" for name in agents.keys()]
        lines = lines[: start + 1] + agent_lines + lines[end:]
        with open(README, "w") as f:
            f.writelines(lines)
        print(f"[DOC] Updated {README}")


# 3. Append to CHANGELOG.md if changed
def append_changelog():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(CHANGELOG, "a") as f:
        f.write(f"\n[{now}] Auto-update docs/AGENT_REGISTRY.md & README.md\n")
    print(f"[DOC] Appended to {CHANGELOG}")


def main():
    print("Attempting to discover agents before generating docs...")
    try:
        from colony.core import agent_registry

        agent_registry.reload_registry()
        generate_agent_registry()
        update_readme()
        append_changelog()
    except ImportError as e:
        print(f"Failed to import or run agent registry discovery: {e}")
        print(
            "Please ensure the script is run from the project root and all dependencies are installed."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
