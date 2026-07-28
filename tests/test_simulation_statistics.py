from core.simulation_statistics import SimulationStatisticsCollector


def test_record_snapshot_adds_snapshot():
    collector = SimulationStatisticsCollector()

    snapshot = collector.record_snapshot(
        step=1,
        population=5,
        resources={"energy": 80.0, "food": 120.0},
        cooperation_rate=0.75,
        survival_time=10.5,
    )

    assert snapshot.step == 1
    assert snapshot.population == 5
    assert len(collector.snapshots) == 1


def test_get_summary_returns_average_values():
    collector = SimulationStatisticsCollector()

    collector.record_snapshot(
        step=1,
        population=5,
        resources={"energy": 80.0},
        cooperation_rate=0.6,
        survival_time=10.0,
    )
    collector.record_snapshot(
        step=2,
        population=7,
        resources={"energy": 90.0},
        cooperation_rate=0.8,
        survival_time=20.0,
    )

    summary = collector.get_summary()

    assert summary["total_snapshots"] == 2
    assert summary["latest_population"] == 7
    assert summary["average_population"] == 6
    assert summary["average_cooperation_rate"] == 0.7
    assert summary["latest_survival_time"] == 20.0


def test_export_to_json_creates_file(tmp_path):
    collector = SimulationStatisticsCollector()
    collector.record_snapshot(
        step=1,
        population=3,
        resources={"energy": 50.0},
        cooperation_rate=0.5,
        survival_time=5.0,
    )

    output_file = collector.export_to_json(tmp_path / "stats.json")

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8")


def test_export_to_csv_creates_file(tmp_path):
    collector = SimulationStatisticsCollector()
    collector.record_snapshot(
        step=1,
        population=3,
        resources={"energy": 50.0},
        cooperation_rate=0.5,
        survival_time=5.0,
    )

    output_file = collector.export_to_csv(tmp_path / "stats.csv")

    assert output_file.exists()
    assert "population" in output_file.read_text(encoding="utf-8")