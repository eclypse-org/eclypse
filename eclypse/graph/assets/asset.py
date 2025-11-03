"""Module for the Asset class.

It represents a node resource or a service requirement, such as CPU, GPU, RAM or node availability.

It provides the inteface for the basic algebraic functions between assets:
- aggregate: aggregate the assets into a single asset.
- satisfies: check if the asset satisfies a constraint based on the total ordering of the asset.
- is_consistent: check if the asset has a feasible value, i.e., it is within the bounds.
"""

from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Union,
)

from .space import AssetSpace

if TYPE_CHECKING:
    from random import Random

    from eclypse.utils.types import PrimitiveType


class Asset:
    """The Asset class.

    An Asset represents a resource of the infrastructure, such as CPU, GPU, RAM or
    node availability.

    It provides the inteface for the basic algebraic functions between assets.
    """

    def __init__(
        self,
        lower_bound: Any,
        upper_bound: Any,
        init_fn_or_value: Optional[
            Union[PrimitiveType, AssetSpace, Callable[[], Any]]
        ] = None,
        functional: bool = True,
    ):
        """Initialize the asset with the lower and upper bounds.

        The lower and the upper bounds represent the element which is always contained in
        and the element the always contains the asset, respectively. Thus, they must
        respect the total ordering of the asset.

        The `init_fn_or_value` parameter is the function to initialize the asset. It can
        be a primitive type, a callable with no arguments or an `AssetSpace` object.
        If it is not provided, the asset will be initialized with the lower bound.

        The `functional` parameter indicates if the asset is functional or not, thus if
        it must be checked during the validation of a placement or not.

        Args:
            lower_bound (Any): The lower bound of the asset.
            upper_bound (Any): The upper bound of the asset.
            init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
                The function to initialize the asset. It can be a primitive type, a
                callable with no arguments or an `AssetSpace` object. If it is not
                provided, the asset will be initialized with the lower bound.
                Defaults to None.
            functional (bool, optional): If True, the asset is functional. Defaults to
                True.

        Raises:
            ValueError: If the lower bound is not contained in the upper bound.
            TypeError: If the init_fn is not a callable or an AssetSpace object.
        """
        if not self.satisfies(upper_bound, lower_bound):
            raise ValueError(
                "The lower bound must be contained in the upper bound. See the ",
                f"behaviour of the `contains` method of {self.__class__.__name__}.",
            )

        _init_fn = None
        if isinstance(init_fn_or_value, AssetSpace) or callable(init_fn_or_value):
            _init_fn = init_fn_or_value
        elif isinstance(
            init_fn_or_value, (int, float, str, list, tuple, dict, bool, set)
        ):

            def _tmp_init_fn() -> Any:
                return init_fn_or_value

            _init_fn = _tmp_init_fn

        elif init_fn_or_value is None:
            _init_fn = None
        else:
            raise TypeError(
                f"Unsupported type for `init_fn` function. Must be a callable or \
                an AssetSpace object. Got {type(init_fn_or_value)}."
            )

        self.init_fn = _init_fn
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.functional = functional

    def _init(self, rnd: Random) -> Any:
        """Initialise the asset according to the `init_fn` function.

        Args:
            rnd (Random): The random number generator to use.

        Returns:
            Any: The initialised asset.
        """
        if isinstance(self.init_fn, AssetSpace):
            return self.init_fn(rnd)
        if callable(self.init_fn):
            return self.init_fn()

        raise ValueError(
            "The `init_fn` function must be a callable or an AssetSpace object."
        )

    @abstractmethod
    def aggregate(self, *assets) -> Any:
        """Aggregate the assets into a single asset.

        Args:
            assets (Any): The assets to aggregate.
        """

    @abstractmethod
    def satisfies(self, asset: Any, constraint: Any) -> bool:
        """Check if the asset satisfies the constraint.

        Args:
            asset (Any): The asset to check.
            constraint (Any): The constraint to check.

        Returns:
            bool: True if the asset satisfies the constraint, False otherwise.
        """

    @abstractmethod
    def is_consistent(self, asset: Any) -> bool:
        """Check if the asset has a feasible value."""

    def flip(self) -> Asset:
        """Flip the asset.

        Move the perspective from being a "capability" to be a "requirement" and vice versa.
        By default, the asset is left unchanged, thus the method returns a copy of the asset.

        Returns:
            Asset: The flipped asset.
        """
        return deepcopy(self)

    def __str__(self):
        """Return the string representation of the asset."""
        return "".join(
            [
                f"Type: {self.__class__.__name__}\n",
                f"Lower Bound: {self.lower_bound}\n",
                f"Upper Bound: {self.upper_bound}\n",
                f"Functional: {self.functional}\n",
            ]
        )
