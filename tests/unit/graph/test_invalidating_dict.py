from __future__ import annotations

import pickle

import pytest

from eclypse.graph.invalidating_dict import InvalidatingDict


@pytest.mark.parametrize("watched_keys", [None, ["cpu"]])
def test_mutations_notify_only_changed_watched_keys(watched_keys):
    changes = []
    data = InvalidatingDict(
        cpu=1, label="old", on_change=changes.append, watched_keys=watched_keys
    )
    data["cpu"] = 1
    data.update(cpu=1)
    assert data.setdefault("cpu", 99) == 1
    assert changes == []

    data.update(cpu=2, label="new")
    assert changes == [("cpu", "label") if watched_keys is None else ("cpu",)]
    changes.clear()
    del data["label"]
    assert changes == ([("label",)] if watched_keys is None else [])

    changes.clear()
    assert data.setdefault("extra", 3) == 3
    assert data.pop("extra") == 3
    assert changes == ([("extra",), ("extra",)] if watched_keys is None else [])

    changes.clear()
    assert data.popitem() == ("cpu", 2)
    assert changes == [("cpu",)]
    changes.clear()
    assert data.pop("missing", 42) == 42
    with pytest.raises(KeyError, match="missing"):
        data.pop("missing")
    with pytest.raises(KeyError):
        data.popitem()
    with pytest.raises(KeyError):
        del data["missing"]
    data.clear()
    assert changes == []

    data.update(cpu=4, label="last")
    changes.clear()
    data.clear()
    assert data == {}
    assert changes == [("cpu", "label") if watched_keys is None else ("cpu",)]


def test_pickle_restores_dictionary_before_invalidation_hook():
    changes = []
    data = InvalidatingDict(cpu=1, on_change=changes.append, watched_keys=["cpu"])

    restored = pickle.loads(pickle.dumps(data))

    assert restored == {"cpu": 1}
    assert restored._watched_keys == {"cpu"}
    restored["cpu"] = 2
    assert restored._on_change.__self__ == [("cpu",)]
    assert changes == []
