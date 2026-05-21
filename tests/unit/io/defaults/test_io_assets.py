from __future__ import annotations

import pytest

from eclypse.graph import Infrastructure
from eclypse.graph.assets import (
    Additive,
    Asset,
)
from eclypse.graph.assets.space import (
    Choice,
    IntUniform,
    Sample,
    Uniform,
)
from eclypse.io.assets import (
    dump_asset,
    dump_init,
    dump_space,
    load_asset,
    load_init,
    load_space,
)


def test_asset_and_space_serialisation_branches():
    for space in (
        Choice(["a", "b"]),
        Uniform(0.0, 1.0),
        IntUniform(1, 5, step=2),
        Sample(["a", "b"], [1, 2], counts=[1, 1]),
    ):
        loaded = load_space(dump_space(space))
        assert type(loaded) is type(space)

    asset = Additive(0, 10, init_fn_or_value=Choice([1, 2]), functional=False)
    loaded_asset = load_asset(dump_asset(asset))
    assert isinstance(loaded_asset, Additive)
    assert loaded_asset.functional is False

    value_asset = load_asset(dump_asset(Additive(0, 10, init_fn_or_value=3)))
    assert value_asset._init(Infrastructure().rnd) == 3  # pylint: disable=protected-access
    assert dump_init(None) == {"type": "none"}
    assert load_init({"type": "none"}) is None
    assert load_space(
        {"type": "sample", "population": ["a", "b"], "k": 1, "counts": None}
    ).k == 1

    with pytest.raises(ValueError):
        load_asset({"type": "missing", "lower_bound": 0, "upper_bound": 1})
    with pytest.raises(ValueError):
        load_space({"type": "missing"})
    with pytest.raises(ValueError):
        dump_asset(UnknownAsset(0, 1))
    with pytest.raises(ValueError):
        dump_space(UnknownSpace())
    with pytest.raises(ValueError):
        dump_asset(Additive(0, 10, init_fn_or_value=lambda: 1))


class UnknownAsset(Asset):
    def aggregate(self, *assets):
        return assets

    def satisfies(self, asset, constraint):
        return True

    def is_consistent(self, asset):
        return True


class UnknownSpace:
    pass
