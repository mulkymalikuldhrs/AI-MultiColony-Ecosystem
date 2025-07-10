# main.py
import argparse
from colony.core.agent_registry import get_agent, list_all_agents
from colony.core.system_bootstrap import bootstrap_systems

def main():
    parser = argparse.ArgumentParser(description="AI MultiColony Ecosystem")
    parser.add_argument("--agent", help="Run a specific agent")
    parser.add_argument("--all", action="store_true", help="Run all agents")
    parser.add_argument("--monitor", action="store_true", help="Enable monitoring")
    parser.add_argument("--web-ui", action="store_true", help="Launch web UI")
    args = parser.parse_args()

    bootstrap_systems()

    if args.agent:
        agent_cls = get_agent(args.agent)
        if agent_cls:
            agent = agent_cls()
            agent.run()
        else:
            print(f"Agent {args.agent} not found")
    elif args.all:
        for agent_name in list_all_agents():
            agent_cls = get_agent(agent_name)
            agent = agent_cls()
            agent.run()
    # Add handling for --monitor and --web-ui

if __name__ == "__main__":
    main()