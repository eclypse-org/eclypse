from __future__ import annotations

from pathlib import Path

from eclypse.utils._logging import (
    _is_eclypse,
    _is_not_eclypse,
    config_logger,
    log_assets_violations,
    log_placement_violations,
    print_exception,
)
from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
)


def test_logging_helpers_configure_and_format_messages(
    monkeypatch,
    capsys,
    tmp_path: Path,
    dummy_logger,
    sample_infrastructure,
):
    configured: dict[str, object] = {}

    monkeypatch.setenv(LOG_LEVEL, "DEBUG")
    monkeypatch.setenv(LOG_FILE, str(tmp_path / "simulation.log"))
    monkeypatch.setattr(
        "eclypse.utils._logging.logger.configure",
        lambda **kwargs: configured.update(kwargs),
    )

    config_logger()

    handlers = configured["handlers"]
    assert isinstance(handlers, list)
    assert len(handlers) == 3
    assert _is_eclypse({"level": type("Level", (), {"name": "ECLYPSE"})()}) is True
    assert _is_not_eclypse({"level": type("Level", (), {"name": "INFO"})()}) is True

    try:
        raise ValueError("broken")
    except ValueError as exc:
        print_exception(exc, "worker")

    output = capsys.readouterr().out
    assert "Traceback (most recent call last):" in output
    assert "ValueError in worker: broken" in output

    log_placement_violations(
        dummy_logger,
        {"cpu": {"featured": 1, "required": 2}},
    )
    log_assets_violations(
        dummy_logger,
        sample_infrastructure.node_assets,
        {"cpu": {"featured": 1, "required": 2}},
    )

    warning_messages = [
        args[0] for level, args in dummy_logger.records if level == "warning"
    ]
    trace_messages = [
        args[0] for level, args in dummy_logger.records if level == "trace"
    ]

    assert not warning_messages
    assert any("available=1 | required=2" in message for message in trace_messages)
    assert any("lower_bound=" in message for message in trace_messages)
    assert any("upper_bound=" in message for message in trace_messages)
