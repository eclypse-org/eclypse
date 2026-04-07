from __future__ import annotations

import json
from pathlib import Path

import pytest

from eclypse.utils.defaults import SIMULATION_CONFIG_FILENAME


@pytest.fixture
def report_dir(tmp_path: Path) -> Path:
    path = tmp_path / "report-run"
    path.mkdir()
    (path / "csv").mkdir()
    with open(path / SIMULATION_CONFIG_FILENAME, "w", encoding="utf-8") as handle:
        json.dump({"report_format": "csv"}, handle)
    return path


@pytest.fixture
def csv_report_dir(report_dir: Path) -> Path:
    csv_dir = report_dir / "csv"
    (csv_dir / "service.csv").write_text(
        "timestamp,event_id,n_event,callback_id,application_id,service_id,value\n"
        "2026-01-01T00:00:00,step,0,placement,shop,gateway,edge-a\n"
        "2026-01-01T00:00:01,step,1,placement,shop,worker,edge-b\n"
        "2026-01-01T00:00:02,stop,2,placement,shop,worker,edge-b\n",
        encoding="utf-8",
    )
    (csv_dir / "simulation.csv").write_text(
        "timestamp,event_id,n_event,callback_id,value\n"
        "2026-01-01T00:00:00,step,0,step_number,1\n"
        "2026-01-01T00:00:02,stop,2,step_number,2\n",
        encoding="utf-8",
    )
    (csv_dir / "application.csv").write_text(
        "timestamp,event_id,n_event,callback_id,application_id,value\n"
        "2026-01-01T00:00:00,stop,2,response_time,shop,10.0\n",
        encoding="utf-8",
    )
    return report_dir
