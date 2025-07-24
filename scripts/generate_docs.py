import os
from datetime import datetime
from colony.core.agent_registry import get_all_agents

AGENT_DOC = "docs/AGENT_REGISTRY.md"
README = "docs/README.md"
CHANGELOG = "docs/CHANGELOG.md"

# 1. Generate AGENT_REGISTRY.md
def generate_agent_registry():
    agents = get_all_agents()
    with open(AGENT_DOC, 'w') as f:
        f.write(f"# Agent Registry\n\nTotal Agents: {len(agents)}\n\n")
        for name, info in agents.items():
            meta = info.get('metadata', {})
            f.write(f"- **{name}**: {meta.get('description', '')} (Route: {meta.get('route', '-')})\n")
    print(f"[DOC] Updated {AGENT_DOC}")

# 2. Update README.md (status, agent, endpoint)
def update_readme():
    agents = get_all_agents()
    with open(README, 'r') as f:
        lines = f.readlines()
    # Simple replace section
    start = end = None
    for i, line in enumerate(lines):
        if line.strip() == "<!-- AGENT_LIST_START -->":
            start = i
        if line.strip() == "<!-- AGENT_LIST_END -->":
            end = i
    if start is not None and end is not None:
        agent_lines = [f"- {name}\n" for name in agents.keys()]
        lines = lines[:start+1] + agent_lines + lines[end:]
        with open(README, 'w') as f:
            f.writelines(lines)
        print(f"[DOC] Updated {README}")

# 3. Append to CHANGELOG.md if changed
def append_changelog():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(CHANGELOG, 'a') as f:
        f.write(f"\n[{now}] Auto-update docs/AGENT_REGISTRY.md & README.md\n")
    print(f"[DOC] Appended to {CHANGELOG}")

def main():
    generate_agent_registry()
    update_readme()
    append_changelog()

if __name__ == "__main__":
    main()