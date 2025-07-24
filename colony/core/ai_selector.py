"""Simple AI Selector"""


class AISelectorAgent:
    def __init__(self):
        self.status = "ready"
        self.agent_id = "ai_selector"
        self.name = "AI Selector Agent"

    def select_best_agent(self, task):
        return "agent_maker"  # Default fallback


class SimpleAISelector(AISelectorAgent):
    pass


ai_selector = AISelectorAgent()
