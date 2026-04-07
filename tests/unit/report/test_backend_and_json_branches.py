from __future__ import annotations

from datetime import datetime

import pytest

from eclypse.report.backends import get_backend
from eclypse.report.report import Report
from eclypse.report.reporters.json import (
    _normalize_for_json,
    _normalize_key_for_json,
    _SafeJSONEncoder,
)


def test_backend_factory_accepts_instances_and_frame_backend_routes(
    list_frame_backend,
    monkeypatch,
    tmp_path,
):
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        list_frame_backend,
        "_read_csv",
        lambda source: calls.append(("csv", source)) or [],
    )
    monkeypatch.setattr(
        list_frame_backend,
        "_read_json",
        lambda source, report_type: calls.append(("json", (source, report_type))) or [],
    )
    monkeypatch.setattr(
        list_frame_backend,
        "_read_parquet",
        lambda source: calls.append(("parquet", source)) or [],
    )

    assert get_backend(list_frame_backend) is list_frame_backend
    assert list_frame_backend.read_frame(tmp_path, "service", "csv") == []
    assert list_frame_backend.read_frame(tmp_path, "service", "json") == []
    assert list_frame_backend.read_frame(tmp_path, "service", "parquet") == []

    with pytest.raises(TypeError, match="not an instance of FrameBackend"):
        get_backend(object())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Unsupported report format"):
        list_frame_backend.read_frame(tmp_path, "service", "yaml")

    assert [kind for kind, _ in calls] == ["csv", "json", "parquet"]


def test_report_supports_simulation_filters_and_frame_errors(
    csv_report_dir,
    list_frame_backend,
):
    report = Report(csv_report_dir, backend=list_frame_backend)

    assert report.simulation(event_ids="stop") == [
        {
            "timestamp": "2026-01-01T00:00:02",
            "event_id": "stop",
            "n_event": 2,
            "callback_id": "step_number",
            "value": 2,
        }
    ]

    report.stats["service"] = None

    with pytest.raises(RuntimeError, match="could not be loaded"):
        report.frame("service")

    with pytest.raises(FileNotFoundError, match="No csv report files found"):
        Report(csv_report_dir.parent / "missing", backend=list_frame_backend)


def test_json_normalisers_support_nested_payloads_and_non_scalar_keys():
    timestamp = datetime(2026, 1, 1)
    payload = {(1, 2): {"when": timestamp, "values": {3, 1}}}

    normalized = _normalize_for_json(payload)

    assert normalized["[1,2]"]["when"] == "2026-01-01T00:00:00"
    assert sorted(normalized["[1,2]"]["values"]) == [1, 3]
    assert _normalize_key_for_json(None) is None
    assert _SafeJSONEncoder().default(timestamp) == "2026-01-01T00:00:00"
