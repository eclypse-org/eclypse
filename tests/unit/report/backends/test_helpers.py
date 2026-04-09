from __future__ import annotations

import json

import pytest

from eclypse.report.backend import (
    _iter_json_payload_rows,
    get_report_columns,
    get_report_source,
    list_parquet_parts,
    load_jsonl_rows,
)
from eclypse.report.backends import get_backend


def test_backend_helpers_resolve_columns_and_sources(tmp_path):
    stats_path = tmp_path / "csv"

    assert "service_id" in get_report_columns("service")
    assert get_report_source(stats_path, "service", "csv") == stats_path / "service.csv"
    assert get_report_source(stats_path, "node", "json") == stats_path / "node.jsonl"


def test_list_parquet_parts_and_jsonl_loading(tmp_path):
    parquet_dir = tmp_path / "parquet" / "service"
    parquet_dir.mkdir(parents=True)
    first_part = parquet_dir / "part-000001.parquet"
    second_part = parquet_dir / "part-000002.parquet"
    first_part.write_text("x", encoding="utf-8")
    second_part.write_text("y", encoding="utf-8")

    jsonl_path = tmp_path / "service.jsonl"
    jsonl_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-01-01T00:00:00",
                "event_name": "step",
                "event_idx": 3,
                "callback_name": "placement",
                "data": [["shop", "gateway", "edge-a"]],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert list_parquet_parts(parquet_dir) == [first_part, second_part]
    assert load_jsonl_rows(jsonl_path, "service") == [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_id": "step",
            "n_event": 3,
            "callback_id": "placement",
            "application_id": "shop",
            "service_id": "gateway",
            "value": "edge-a",
        }
    ]


def test_iter_json_payload_rows_and_backend_factory_errors():
    assert list(_iter_json_payload_rows({"foo": "bar"})) == [[{"foo": "bar"}]]
    assert list(_iter_json_payload_rows((1, 2))) == [[(1, 2)]]

    with pytest.raises(ValueError, match="Unknown backend"):
        get_backend("missing-backend")
