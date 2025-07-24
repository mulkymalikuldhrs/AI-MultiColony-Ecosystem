"""Simple Scheduler"""


class SchedulerAgent:
    def __init__(self):
        self.status = "ready"
        self.tasks = []
        self.agent_id = "scheduler"
        self.name = "Scheduler Agent"

    def start(self):
        self.status = "active"
        return True

    def stop(self):
        self.status = "stopped"
        return True

    def schedule_task(self, task, delay=0):
        self.tasks.append(task)
        return True

    def get_status(self):
        return {"status": "ready", "pending_tasks": len(self.tasks)}

    def get_scheduler_status(self):
        return {
            "status": self.status,
            "pending_tasks": len(self.tasks),
            "agent_id": self.agent_id,
        }


class SimpleScheduler(SchedulerAgent):
    pass


agent_scheduler = SchedulerAgent()
