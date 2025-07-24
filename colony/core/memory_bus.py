"""Simple Memory Bus without Redis dependency"""


class MemoryBusAgent:
    def __init__(self):
        self.data = {}
        self.status = "ready"
        self.agent_id = "memory_bus"
        self.name = "Memory Bus Agent"

    def store(self, key, value):
        self.data[key] = value
        return True

    def retrieve(self, key):
        return self.data.get(key)

    def exists(self, key):
        return key in self.data

    def get_usage_stats(self):
        return {
            "total_items": len(self.data),
            "memory_usage": "Minimal",
            "status": "ready",
        }

    def cleanup_expired(self):
        """Cleanup expired data"""
        # For now, just clear all data
        self.data.clear()
        return True


class SimpleMemoryBus(MemoryBusAgent):
    pass


memory_bus = MemoryBusAgent()
