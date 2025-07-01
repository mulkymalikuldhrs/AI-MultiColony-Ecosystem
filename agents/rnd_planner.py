"""📚 RnDPlannerAgent – conducts research on future upgrades & generates sprint backlog.
Spawns DocMinerWorker (scrapes papers), TrendAnalyzer, TechScout.
"""
from __future__ import annotations
from typing import Dict, List
from agents.role_archetype import BaseRoleAgent
from agents.idea_generator import idea_generator_agent

class DocMinerWorker(BaseRoleAgent):
    capabilities=["paper_scrape"]
    def execute(self, task):
        print("[DocMiner] scraping arXiv for", task)

class TrendAnalyzerWorker(BaseRoleAgent):
    capabilities=["trend_analysis"]
    def execute(self, task):
        ideas=idea_generator_agent().generate_ideas(); print("[TrendAnalyzer]",ideas)

class TechScoutWorker(BaseRoleAgent):
    capabilities=["tech_scout"]
    def execute(self, task):
        print("[TechScout] scanning GitHub stars for", task)

class RnDPlannerAgent(BaseRoleAgent):
    capabilities=["research","generate_backlog"]
    def __init__(self): super().__init__("RnD Planner","research")
    def research_topic(self, topic:str):
        self.spawn(DocMinerWorker).execute(topic)
        self.spawn(TrendAnalyzerWorker).execute(topic)
        self.spawn(TechScoutWorker).execute(topic)
        return {"topic":topic,"status":"done"}

def rnd_planner_agent():
    return RnDPlannerAgent()