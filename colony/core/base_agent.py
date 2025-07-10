# colony/core/base_agent.py
class BaseAgent:
    def __init__(self, name, config, memory):
        self.name = name
        self.config = config
        self.memory = memory

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")
