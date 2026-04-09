from __future__ import annotations

from datetime import datetime

from eclypse.report.reporters.json import (
    _normalize_for_json,
    _normalize_key_for_json,
    _SafeJSONEncoder,
)


def test_json_normalisers_support_nested_payloads_and_non_scalar_keys():
    timestamp = datetime(2026, 1, 1)
    payload = {(1, 2): {"when": timestamp, "values": {3, 1}}}

    normalized = _normalize_for_json(payload)

    assert normalized["[1,2]"]["when"] == "2026-01-01T00:00:00"
    assert sorted(normalized["[1,2]"]["values"]) == [1, 3]
    assert _normalize_key_for_json(None) is None
    assert _SafeJSONEncoder().default(timestamp) == "2026-01-01T00:00:00"
