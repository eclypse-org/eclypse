"""Module for the Multiplicative Asset class.

It represents a numeric asset where the aggregation is the multiplication of the provided assets.
It provides the interface for the basic algebraic functions between assets:

- `aggregate`: Aggregate the assets into a single asset via product.
- `satisfies`: Check if the asset contains another asset and is positive.
- `is_consistent`: Check if the asset belongs to the interval [lower_bound, upper_bound].
"""

from __future__ import annotations

from functools import reduce
from operator import mul
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Union,
)

from .asset import Asset

if TYPE_CHECKING:
    from eclypse.utils.types import PrimitiveType

    from .space import AssetSpace


class Multiplicative(Asset):
    """Multiplicative represents a numeric asset where the aggregation is multiplicative."""

    def __init__(
        self,
        lower_bound: float,
        upper_bound: float,
        init_fn_or_value: Optional[
            Union[PrimitiveType, AssetSpace, Callable[[], Any]]
        ] = None,
        functional: bool = True,
    ):
        """Create a new Multiplicative asset.

        Args:
            lower_bound (float): The lower bound of the asset.
            upper_bound (float): The upper bound of the asset.
            init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
                The function to initialize the asset. It can be a primitive type, a
                callable with no arguments or an `AssetSpace` object. If it is not
                provided, the asset will be initialized with the lower bound.
                Defaults to None.
            functional (bool, optional): If True, the asset is functional. Defaults to
                True.

        Raises:
            ValueError: If $lower_bound > upper_bound$.
        """
        super().__init__(
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            init_fn_or_value=init_fn_or_value,
            functional=functional,
        )

    def aggregate(self, *assets: float) -> float:
        """Aggregate the assets into a single asset via product.

        Args:
            assets (Iterable[float]): The assets to aggregate.

        Returns:
            float: The aggregated asset.
        """
        if not assets:
            return self.lower_bound
        return reduce(mul, assets, 1.0)

    def satisfies(self, asset: float, constraint: float) -> bool:
        """Check `asset` contains `constraint`.

        In an multiplicative asset, the higher value contains the lower value.

        Args:
            asset (float): The "container" asset.
            constraint (float): The "contained" asset.

        Returns:
            True if asset >= constraint, False otherwise.
        """
        return asset >= constraint  #  and asset > 0.0

    def is_consistent(self, asset: float) -> bool:
        """Check if the asset belongs to the interval [lower_bound, upper_bound].

        Args:
            asset (float): The asset to be checked.

        Returns:
            True if lower_bound <= asset <= upper_bound, False otherwise.
        """
        return self.lower_bound <= asset <= self.upper_bound

    def flip(self):
        """Flip the multiplicative asset into a multiplicative concave asset.

        Returns:
            Concave: The flipped concave asset.
        """
        from .concave import Concave  # pylint: disable=import-outside-toplevel

        return Concave(
            self.upper_bound,
            self.lower_bound,
            self.init_fn,
            self.functional,
        )
