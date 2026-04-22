from __future__ import annotations

import random

import pytest

from eclypse.graph.assets import (
    Additive,
    AssetBucket,
    Concave,
    Convex,
    Multiplicative,
    Symbolic,
)
from eclypse.graph.assets.defaults import (
    bandwidth,
    cpu,
    get_default_edge_assets,
    get_default_node_assets,
    get_default_path_aggregators,
)
from eclypse.graph.assets.space import Choice


def test_asset_init_rejects_inverted_bounds():
    with pytest.raises(ValueError):
        Additive(10, 1)


def test_asset_init_supports_primitive_callable_and_asset_space():
    const_asset = Additive(0, 10, 5)
    callable_asset = Additive(0, 10, lambda: 7)
    choice_asset = Additive(0, 10, Choice([3, 4]))

    rnd = random.Random(1)

    assert const_asset._init(rnd) == 5  # pylint: disable=protected-access
    assert callable_asset._init(rnd) == 7  # pylint: disable=protected-access
    assert choice_asset._init(rnd) in {3, 4}  # pylint: disable=protected-access


def test_asset_init_rejects_unsupported_init_type():
    with pytest.raises(TypeError, match="Unsupported type for `init_fn`"):
        Additive(0, 10, object())


@pytest.mark.parametrize(
    ("asset", "values", "expected"),
    [
        (Additive(0, 10), (1, 2, 3), 6),
        (Multiplicative(0, 10), (2, 3), 6.0),
        (Convex(0, 10), (6, 3, 9), 3),
        (Concave(10, 0), (6, 3, 9), 9),
    ],
)
def test_numeric_asset_aggregation(asset, values, expected):
    assert asset.aggregate(*values) == expected


def test_multiplicative_asset_aggregation_without_values_returns_lower_bound():
    asset = Multiplicative(0.5, 10)

    assert asset.aggregate() == 0.5


@pytest.mark.parametrize(
    ("asset", "featured", "required", "consistent", "inconsistent"),
    [
        (Additive(0, 10), 5, 4, 6, 11),
        (Multiplicative(0, 10), 5, 4, 6, 11),
        (Convex(0, 10), 6, 4, 7, 11),
        (Concave(10, 0), 4, 5, 3, -1),
    ],
)
def test_numeric_asset_satisfaction_and_consistency(
    asset,
    featured,
    required,
    consistent,
    inconsistent,
):
    assert asset.satisfies(featured, required)
    assert asset.is_consistent(consistent)
    assert not asset.is_consistent(inconsistent)


def test_concave_and_convex_flip_into_each_other():
    concave = Concave(10, 0)
    convex = Convex(0, 10)

    flipped_concave = concave.flip()
    flipped_convex = convex.flip()

    assert isinstance(flipped_concave, Convex)
    assert isinstance(flipped_convex, Concave)
    assert flipped_concave.lower_bound == 0
    assert flipped_convex.upper_bound == 0


def test_symbolic_asset_handles_strings_and_lists():
    symbolic = Symbolic([], ["edge", "cloud", "gpu"], ["edge"])

    assert set(symbolic.aggregate("edge", ["cloud", "gpu"])) == {
        "edge",
        "cloud",
        "gpu",
    }
    assert symbolic.satisfies(["edge", "cloud"], ["edge"])
    assert symbolic.is_consistent(["edge", "gpu"])
    assert not symbolic.is_consistent(["unknown"])


def test_asset_bucket_aggregates_validates_consumes_and_flips():
    bucket = AssetBucket(
        cpu=Additive(0, 10),
        latency=Concave(10, 0, functional=False),
    )
    aggregate = bucket.aggregate({"cpu": 1, "latency": 5}, {"cpu": 2, "latency": 3})

    assert aggregate == {"cpu": 3, "latency": 5}
    assert bucket.satisfies({"cpu": 4, "latency": 2}, {"cpu": 3})
    assert bucket.satisfies(
        {"cpu": 1, "latency": 2},
        {"cpu": 3},
        violations=True,
    ) == {"cpu": {"featured": 1, "required": 3}}
    assert bucket.consume({"cpu": 4, "latency": 2}, {"cpu": 1}) == {
        "cpu": 3,
        "latency": 2,
    }
    assert bucket.is_consistent({"cpu": 5, "latency": 2})
    assert bucket.lower_bound == {"cpu": 0, "latency": 10}
    assert bucket.upper_bound == {"cpu": 10, "latency": 0}
    assert isinstance(bucket.flip()["latency"], Convex)


def test_asset_bucket_rejects_non_asset_values():
    bucket = AssetBucket()

    with pytest.raises(ValueError, match="Asset cpu is not an instance of Asset"):
        bucket["cpu"] = 3


def test_default_asset_factories_expose_expected_keys():
    node_assets = get_default_node_assets()
    edge_assets = get_default_edge_assets()
    path_aggregators = get_default_path_aggregators()

    assert {"cpu", "ram", "storage", "gpu", "availability", "processing_time"} <= set(
        node_assets
    )
    assert {"latency", "bandwidth"} == set(edge_assets)
    assert path_aggregators["latency"]([1, 2, 3]) == 6
    assert path_aggregators["bandwidth"]([8, 3, 5]) == 3


def test_default_asset_getters_define_default_initialisers():
    rnd = random.Random(1)
    node_assets = get_default_node_assets()
    edge_assets = get_default_edge_assets()

    assert node_assets["cpu"]._init(rnd) in {2**i for i in range(1, 9)}  # pylint: disable=protected-access
    assert 0.99 <= node_assets["availability"]._init(rnd) <= 1.0  # pylint: disable=protected-access
    assert 1 <= edge_assets["latency"]._init(rnd) <= 40  # pylint: disable=protected-access
    assert 50 <= edge_assets["bandwidth"]._init(rnd) <= 1500  # pylint: disable=protected-access


def test_default_asset_getters_can_return_bare_assets_without_initialisers():
    node_assets = get_default_node_assets(with_init=False)
    edge_assets = get_default_edge_assets(with_init=False)

    assert all(asset.init_fn is None for asset in node_assets.values())
    assert all(asset.init_fn is None for asset in edge_assets.values())


def test_asset_factories_without_init_use_asset_defaults():
    rnd = random.Random(1)

    assert cpu().init_fn is None
    assert bandwidth().init_fn is None
    with pytest.raises(ValueError, match="init_fn"):
        cpu()._init(rnd)  # pylint: disable=protected-access


def test_asset_string_representation_includes_main_fields():
    rendered = str(Additive(0, 10, 5))

    assert "Type: Additive" in rendered
    assert "Lower Bound: 0" in rendered
    assert "Upper Bound: 10" in rendered
    assert "Functional: True" in rendered
