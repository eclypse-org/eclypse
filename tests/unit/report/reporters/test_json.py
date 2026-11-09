from __future__ import annotations

import json
from datetime import datetime

import numpy as np
import pytest

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


def test_json_encoder_supports_numpy_values_and_keys():
    payload = {
        np.int64(7): {
            "scalar": np.float32(0.5),
            "bool": np.bool_(True),
            "array": np.array([[1, 2], [3, 4]], dtype=np.int64),
        }
    }
    assert json.loads(
        json.dumps(_normalize_for_json(payload), cls=_SafeJSONEncoder)
    ) == {"7": {"scalar": 0.5, "bool": True, "array": [[1, 2], [3, 4]]}}
    with pytest.raises(TypeError, match="not JSON serializable"):
        json.dumps(object(), cls=_SafeJSONEncoder)
