from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    cast,
)

import polars as pl
import pytest

from eclypse.report.reporters import (
    ParquetReporter,
    TensorBoardReporter,
    get_default_reporters,
)
from eclypse.report.reporters.parquet import _write_parquet
from eclypse.utils.defaults import (
    PARQUET_REPORT_DIR,
    TENSORBOARD_REPORT_DIR,
)

if TYPE_CHECKING:
    from eclypse.workflow.event.event import EclypseEvent


@pytest.mark.asyncio
async def test_parquet_and_tensorboard_reporters_cover_runtime_paths(
    tmp_path: Path, monkeypatch
):
    parquet_reporter = ParquetReporter(tmp_path)

    with pytest.raises(RuntimeError, match="not initialised"):
        await parquet_reporter.write("service", [{"value": 1}])

    await parquet_reporter.init()
    callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", 3.5), ("shop", "ignored", None)),
            type="service",
            name="latency",
        ),
    )
    rows = list(parquet_reporter.report("step", 2, callback))

    assert len(rows) == 1
    assert rows[0]["event_id"] == "step"
    assert rows[0]["service_id"] == "gateway"

    await parquet_reporter.write("service", rows)
    await parquet_reporter.write("service", rows)

    first_part = tmp_path / PARQUET_REPORT_DIR / "service" / "part-000000.parquet"
    second_part = tmp_path / PARQUET_REPORT_DIR / "service" / "part-000001.parquet"

    assert first_part.exists()
    assert second_part.exists()

    direct_part = tmp_path / "direct.parquet"
    _write_parquet(
        pl,
        [
            {
                "timestamp": "2026-01-01T00:00:00",
                "event_id": "step",
                "n_event": 1,
                "callback_id": "metric",
                "application_id": "shop",
                "service_id": "gateway",
                "value": 1.0,
            }
        ],
        [
            "timestamp",
            "event_id",
            "n_event",
            "callback_id",
            "application_id",
            "service_id",
            "value",
        ],
        direct_part,
    )
    assert direct_part.exists()

    calls: list[tuple[str, dict[str, float], int]] = []

    class FakeSummaryWriter:
        def __init__(self, log_dir: Path):
            self.log_dir = log_dir
            self.closed = False

        def add_scalars(self, tag: str, metric_dict: dict[str, float], step: int):
            calls.append((tag, metric_dict, step))

        def close(self):
            self.closed = True

    monkeypatch.setattr("tensorboardX.SummaryWriter", FakeSummaryWriter)

    tensorboard_reporter = TensorBoardReporter(tmp_path)
    with pytest.raises(RuntimeError, match="not initialised"):
        tensorboard_reporter.writer

    await tensorboard_reporter.init()

    metric_callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", 2.5),),
            type="service",
            name="latency",
        ),
    )
    empty_callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", None),),
            type=None,
            name="noop",
        ),
    )

    assert list(tensorboard_reporter.report("step", 1, empty_callback)) == []

    metric_rows = list(tensorboard_reporter.report("step", 4, metric_callback))
    await tensorboard_reporter.write("service", metric_rows)

    assert tensorboard_reporter.writer.log_dir == tmp_path / TENSORBOARD_REPORT_DIR
    assert calls == [("service/latency", {"shop/gateway": 2.5}, 4)]

    await tensorboard_reporter.close()
    with pytest.raises(RuntimeError, match="not initialised"):
        tensorboard_reporter.writer

    reporter_map = get_default_reporters([PARQUET_REPORT_DIR, TENSORBOARD_REPORT_DIR])

    assert set(reporter_map) == {PARQUET_REPORT_DIR, TENSORBOARD_REPORT_DIR}
    assert get_default_reporters(None) == {}
