AGENT_REGISTRY = {}

def register_agent(cls):
    """
    A decorator to automatically register agent classes in the AGENT_REGISTRY.
    """
    agent_name = cls.__name__
    if agent_name in AGENT_REGISTRY:
        print(f"Warning: Agent '{agent_name}' is already registered. Overwriting.")
    AGENT_REGISTRY[agent_name] = cls()
    return cls
