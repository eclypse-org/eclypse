from __future__ import annotations

import random

from eclypse.graph.assets.space import (
    Choice,
    IntUniform,
    Sample,
    Uniform,
)


def test_choice_returns_member_from_population():
    value = Choice(["a", "b", "c"])(random.Random(3))

    assert value in {"a", "b", "c"}


def test_uniform_returns_value_in_expected_interval():
    value = Uniform(1.5, 2.5)(random.Random(5))

    assert 1.5 <= value <= 2.5


def test_int_uniform_honours_bounds_and_step():
    value = IntUniform(2, 10, step=2)(random.Random(7))

    assert value in {2, 4, 6, 8, 10}


def test_sample_supports_fixed_and_random_k():
    rnd = random.Random(11)

    fixed = Sample([1, 2, 3, 4], 2)(rnd)
    variable = Sample([1, 2, 3, 4], (1, 3))(rnd)

    assert len(fixed) == 2
    assert 1 <= len(variable) <= 3
    assert set(fixed).issubset({1, 2, 3, 4})
    assert set(variable).issubset({1, 2, 3, 4})
