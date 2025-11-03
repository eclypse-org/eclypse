"""Module for the AdditiveAsset class.

It represents a numeric asset where the aggregation is the sum of the assets.
It provides the interface for the basic algebraic functions between assets:

- `aggregate`: Aggregate the assets into a single asset via summation.
- `satisfies`: Check if the asset contains another asset.
- `is_consistent`: Check if the asset belongs to the interval [lower_bound, upper_bound].
"""

from __future__ import annotations

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


class Additive(Asset):
    """AdditiveAsset represents a numeric asset where the aggregation is additive."""

    def __init__(
        self,
        lower_bound: float,
        upper_bound: float,
        init_fn_or_value: Optional[
            Union[PrimitiveType, AssetSpace, Callable[[], Any]]
        ] = None,
        functional: bool = True,
    ):
        """Create a new Additive asset.

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
        """Aggregate the assets into a single asset via summation.

        Args:
            assets (Iterable[float]): The assets to aggregate.

        Returns:
            float: The aggregated asset.
        """
        return sum(assets, start=self.lower_bound)

    def satisfies(self, asset: float, constraint: float) -> bool:
        """Check `asset` contains `constraint`.

        In an additive asset, the higher value contains the lower value.

        Args:
            asset (float): The "container" asset.
            constraint (float): The "contained" asset.

        Returns:
            True if asset >= constraint, False otherwise.
        """
        return asset >= constraint

    def is_consistent(self, asset: float) -> bool:
        """Check if the asset belongs to the interval [lower_bound, upper_bound].

        Args:
            asset (float): The asset to be checked.

        Returns:
            True if lower_bound <= asset <= upper_bound, False otherwise.
        """
        return self.lower_bound <= asset <= self.upper_bound
