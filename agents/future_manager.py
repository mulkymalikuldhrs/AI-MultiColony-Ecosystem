"""🪐 FutureManagerAgent – oversees FutureSimulationEngine and foresight team.
Spawns DataSynthesizer and ScenarioGenerator agents, keeps simulation time moving.
"""
from __future__ import annotations
import threading
import time
from typing import List, Dict

from core.future_engine import future_engine
from agents.scenario_generator import scenario_generator_agent

try:
    from agents.data_synthesizer import data_synthesizer_agent  # optional
except ImportError:
    data_synthesizer_agent = None

class FutureManagerAgent:
    status = "ready"
    capabilities = ["advance_time", "generate_scenarios", "update_dataset"]

    def __init__(self, tick_years: int = 1, interval_sec: int = 60):
        self.tick_years = tick_years
        self.interval_sec = interval_sec
        self.scenario_bot = scenario_generator_agent()
        self.synth_bot = data_synthesizer_agent() if data_synthesizer_agent else None
        self._start_loop()

    # --------------------------------------------------
    def _start_loop(self):
        th = threading.Thread(target=self._loop, daemon=True)
        th.start()

    def _loop(self):
        while True:
            future_engine.tick(self.tick_years)
            print(f"[FutureManager] advanced to {future_engine.now()}")
            if self.synth_bot:
                self.synth_bot.add_random_data(future_engine.now())  # hypothetical
            # generate quick foresight sample
            self.scenario_bot.generate("Energy Consumption", yrs_ahead=0)
            time.sleep(self.interval_sec)

    # public quick action
    def summary(self) -> Dict:
        return {
            "sim_year": future_engine.now(),
            "population": future_engine.stat("population"),
            "energy_zj": future_engine.stat("energy_zettajoule"),
        }

def future_manager_agent():
    return FutureManagerAgent()