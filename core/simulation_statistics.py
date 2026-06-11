"""
Simulation Statistics Collector

Provides a small reusable statistics system for tracking colony and agent
performance over time. The collected snapshots can be exported to CSV or JSON
for future dashboard and reporting features.
"""

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SimulationSnapshot:
    """
    Stores one point-in-time record of colony performance.

    step: Current simulation step/tick number.
    population: Number of active agents or colony members.
    resources: Resource values such as CPU, memory, storage, energy, etc.
    cooperation_rate: Value between 0 and 1 showing cooperation level.
    survival_time: How long the colony/system has stayed active.
    metadata: Optional extra details for future dashboard use.
    timestamp: Time when the snapshot was recorded.
    """

    step: int
    population: int
    resources: Dict[str, float]
    cooperation_rate: float
    survival_time: float
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SimulationStatisticsCollector:
    """
    Collects simulation statistics and exports them for analysis.

    This class is intentionally independent from the main system so it can be
    connected to different colony, agent, or simulation modules later.
    """

    def __init__(self):
        self.snapshots: List[SimulationSnapshot] = []

    def record_snapshot(
        self,
        step: int,
        population: int,
        resources: Dict[str, float],
        cooperation_rate: float,
        survival_time: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SimulationSnapshot:
        """
        Record a new simulation snapshot.

        Returns the created snapshot so other modules can use it immediately.
        """

        snapshot = SimulationSnapshot(
            step=step,
            population=population,
            resources=resources,
            cooperation_rate=cooperation_rate,
            survival_time=survival_time,
            metadata=metadata or {},
        )
        self.snapshots.append(snapshot)
        return snapshot

    def get_summary(self) -> Dict[str, Any]:
        """
        Build a simple summary from the collected snapshots.
        """

        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "latest_population": 0,
                "average_population": 0,
                "average_cooperation_rate": 0,
                "latest_survival_time": 0,
            }

        total_population = sum(snapshot.population for snapshot in self.snapshots)
        total_cooperation = sum(snapshot.cooperation_rate for snapshot in self.snapshots)
        latest_snapshot = self.snapshots[-1]

        return {
            "total_snapshots": len(self.snapshots),
            "latest_population": latest_snapshot.population,
            "average_population": total_population / len(self.snapshots),
            "average_cooperation_rate": total_cooperation / len(self.snapshots),
            "latest_survival_time": latest_snapshot.survival_time,
        }

    def export_to_json(self, file_path: str) -> Path:
        """
        Export all snapshots to a JSON file.
        """

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(snapshot) for snapshot in self.snapshots]

        with output_path.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2)

        return output_path

    def export_to_csv(self, file_path: str) -> Path:
        """
        Export all snapshots to a CSV file.

        Resource and metadata dictionaries are stored as JSON strings so the CSV
        stays simple while still keeping nested data.
        """

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "timestamp",
            "step",
            "population",
            "resources",
            "cooperation_rate",
            "survival_time",
            "metadata",
        ]

        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for snapshot in self.snapshots:
                writer.writerow(
                    {
                        "timestamp": snapshot.timestamp,
                        "step": snapshot.step,
                        "population": snapshot.population,
                        "resources": json.dumps(snapshot.resources),
                        "cooperation_rate": snapshot.cooperation_rate,
                        "survival_time": snapshot.survival_time,
                        "metadata": json.dumps(snapshot.metadata or {}),
                    }
                )

        return output_path


simulation_statistics_collector = SimulationStatisticsCollector()