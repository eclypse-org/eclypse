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
    await parquet_reporter.write("service", [])
    assert parquet_reporter._partitions == {}
    assert not parquet_reporter.report_path.exists()

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

    for part in (first_part, second_part):
        frame = pl.read_parquet(part)
        assert frame.columns == list(rows[0])
        assert frame.to_dicts() == rows

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
    assert list(parquet_reporter.report("step", 1, empty_callback)) == []
    empty_callback.type = "service"
    assert list(tensorboard_reporter.report("step", 1, empty_callback)) == []

    metric_rows = list(tensorboard_reporter.report("step", 4, metric_callback))
    await tensorboard_reporter.write("service", metric_rows)

    assert tensorboard_reporter.writer.log_dir == tmp_path / TENSORBOARD_REPORT_DIR
    assert calls == [("service/latency", {"shop/gateway": 2.5}, 4)]

    writer = tensorboard_reporter.writer
    await tensorboard_reporter.close()
    await tensorboard_reporter.close()
    assert writer.closed
    with pytest.raises(RuntimeError, match="not initialised"):
        tensorboard_reporter.writer

    reporter_map = get_default_reporters([PARQUET_REPORT_DIR, TENSORBOARD_REPORT_DIR])

    assert set(reporter_map) == {PARQUET_REPORT_DIR, TENSORBOARD_REPORT_DIR}
    assert get_default_reporters(None) == {}
