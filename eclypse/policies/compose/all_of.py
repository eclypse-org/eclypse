"""Composition policy that applies all children."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.compose.chain import chain

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def all_of(*policies: UpdatePolicy) -> UpdatePolicy:
    """Run all policies in order.

    Args:
        policies (UpdatePolicy): Policies to call in order.

    Returns:
        Composed policy.
    """
    return chain(*policies)
