from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import polars as pl
import pytest

from eclypse.report.backends import (
    PandasBackend,
    PolarsBackend,
    PolarsLazyBackend,
    get_backend,
)


def _write_service_jsonl(path: Path):
    path.write_text(
        json.dumps(
            {
                "timestamp": "2026-01-01T00:00:00",
                "event_name": "step",
                "event_idx": 1,
                "callback_name": "metric",
                "data": [["shop", "gateway", "4.5"]],
            }
        )
        + "\n",
        encoding="utf-8",
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


def test_named_backends_resolve_and_pandas_backend_filters(tmp_path: Path, monkeypatch):
    csv_path = tmp_path / "service.csv"
    csv_path.write_text(
        "timestamp,event_id,n_event,callback_id,application_id,service_id,value\n"
        "2026-01-01T00:00:00,step,1,metric,shop,gateway,1.5\n"
        "2026-01-01T00:00:01,step,2,metric,shop,worker,3.0\n"
        "2026-01-01T00:00:02,stop,3,metric,shop,worker,5.0\n",
        encoding="utf-8",
    )
    json_path = tmp_path / "service.jsonl"
    _write_service_jsonl(json_path)

    backend = get_backend(" pandas ")

    assert isinstance(backend, PandasBackend)

    df = backend._read_csv(csv_path)
    json_df = backend._read_json(json_path, "service")

    assert backend.columns(df) >= {"event_id", "n_event", "service_id", "value"}
    assert backend.max(df, "n_event") == 3
    assert backend.filter_events(df, "n_event", [1, 3])["n_event"].tolist() == [1, 3]
    assert backend.filter_range_step(df, "n_event", 1, 3, 2)["n_event"].tolist() == [
        1,
        3,
    ]
    assert backend.filter_eq(df, "service_id", "worker")["service_id"].tolist() == [
        "worker",
        "worker",
    ]
    assert backend.filter_in(df, "service_id", ["gateway"])["service_id"].tolist() == [
        "gateway"
    ]
    assert backend.is_empty(df.iloc[0:0]) is True
    assert json_df["value"].tolist() == ["4.5"]

    part_rows = {
        "part-000000.parquet": pd.DataFrame([{"n_event": 1, "value": 1.0}]),
        "part-000001.parquet": pd.DataFrame([{"n_event": 2, "value": 2.0}]),
    }
    parquet_dir = tmp_path / "service"
    parquet_dir.mkdir()
    for part_name in part_rows:
        (parquet_dir / part_name).write_text("stub", encoding="utf-8")

    original_read_parquet = backend._pd.read_parquet

    def fake_read_parquet(path: Path):
        return part_rows[Path(path).name]

    monkeypatch.setattr(backend._pd, "read_parquet", fake_read_parquet)
    combined = backend._read_parquet(parquet_dir)
    monkeypatch.setattr(backend._pd, "read_parquet", original_read_parquet)

    assert combined["n_event"].tolist() == [1, 2]


def test_polars_backends_read_filter_and_collect(tmp_path: Path):
    csv_path = tmp_path / "service.csv"
    csv_path.write_text(
        "timestamp,event_id,n_event,callback_id,application_id,service_id,value\n"
        "2026-01-01T00:00:00,step,1,metric,shop,gateway,1.0\n"
        "2026-01-01T00:00:01,step,2,metric,shop,worker,4.0\n"
        "2026-01-01T00:00:02,stop,3,metric,shop,worker,7.0\n",
        encoding="utf-8",
    )
    json_path = tmp_path / "service.jsonl"
    _write_service_jsonl(json_path)

    parquet_dir = tmp_path / "service"
    parquet_dir.mkdir()
    pl.DataFrame(
        [
            {
                "timestamp": "2026-01-01T00:00:00",
                "event_id": "step",
                "n_event": 1,
                "callback_id": "metric",
                "application_id": "shop",
                "service_id": "gateway",
                "value": "1.5",
            },
            {
                "timestamp": "2026-01-01T00:00:01",
                "event_id": "stop",
                "n_event": 2,
                "callback_id": "metric",
                "application_id": "shop",
                "service_id": "worker",
                "value": "2.5",
            },
        ]
    ).write_parquet(parquet_dir / "part-000000.parquet")

    eager = get_backend("polars")
    lazy = get_backend("polars_lazy")

    assert isinstance(eager, PolarsBackend)
    assert isinstance(lazy, PolarsLazyBackend)

    eager_csv = eager._read_csv(csv_path)
    eager_json = eager._read_json(json_path, "service")
    eager_parquet = eager._read_parquet(parquet_dir)
    eager_no_value = eager._coerce_value_column(pl.DataFrame({"other": [1]}))

    assert eager.columns(eager_csv) >= {"event_id", "n_event", "service_id", "value"}
    assert eager.max(eager_csv, "n_event") == 3
    assert eager.filter_events(eager_csv, "n_event", [1, 3])["n_event"].to_list() == [
        1,
        3,
    ]
    assert eager.filter_range_step(eager_csv, "n_event", 1, 3, 2)[
        "n_event"
    ].to_list() == [1, 3]
    assert eager.filter_eq(eager_csv, "service_id", "worker")[
        "service_id"
    ].to_list() == [
        "worker",
        "worker",
    ]
    assert eager.filter_in(eager_csv, "service_id", ["gateway"])[
        "service_id"
    ].to_list() == ["gateway"]
    assert eager.is_empty(eager_csv.clear()) is True
    assert eager_json["value"].to_list() == [4.5]
    assert eager_parquet["value"].to_list() == [1.5, 2.5]
    assert eager_no_value.columns == ["other"]

    lazy_csv = lazy._read_csv(csv_path)
    lazy_json = lazy._read_json(json_path, "service")
    lazy_parquet = lazy._read_parquet(parquet_dir)
    lazy_no_value = lazy._coerce_value_column(pl.DataFrame({"other": [1]}).lazy())

    assert lazy.columns(lazy_csv) >= {"event_id", "n_event", "service_id", "value"}
    assert lazy.max(lazy_csv, "n_event") == 3
    assert lazy.filter_events(lazy_csv, "n_event", [2, 3]).collect()[
        "n_event"
    ].to_list() == [
        2,
        3,
    ]
    assert lazy.filter_range_step(lazy_csv, "n_event", 1, 3, 2).collect()[
        "n_event"
    ].to_list() == [
        1,
        3,
    ]
    assert lazy.filter_eq(lazy_csv, "service_id", "worker").collect()[
        "service_id"
    ].to_list() == [
        "worker",
        "worker",
    ]
    assert lazy.filter_in(lazy_csv, "service_id", ["gateway"]).collect()[
        "service_id"
    ].to_list() == ["gateway"]
    assert lazy.is_empty(lazy_csv.limit(0)) is True
    assert lazy_json.collect()["value"].to_list() == [4.5]
    assert lazy_parquet.collect()["value"].to_list() == [1.5, 2.5]
    assert lazy_no_value.collect_schema().names() == ["other"]
