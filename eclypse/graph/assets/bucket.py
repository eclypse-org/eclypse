"""Module for the AssetBucket class.

It is a dictionary-like class that stores assets of nodes and service and provides
methods to aggregate, check consistency, and initialize them.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Union,
)

from eclypse.graph.assets import Additive

from .asset import Asset

if TYPE_CHECKING:
    from random import Random


class AssetBucket(Dict[str, Asset]):
    """Class to store a set of nodes/services assets."""

    def __init__(self, **assets):
        """Create a new asset bucket.

        Args:
            **assets (Dict[str, Asset]): The assets to store in the bucket.
        """
        super().__init__(assets)

    def __setitem__(self, key: str, value: Asset):
        """Set an asset in the bucket.

        Args:
            key (str): The key of the asset.
            value (Asset): The asset to store.
        """
        if not isinstance(value, Asset):
            raise ValueError(f"Asset {key} is not an instance of Asset.")
        super().__setitem__(key, value)

    def aggregate(self, *assets: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate the assets into a single asset.

        Args:
            assets (Iterable[Dict[str, Any]]): The assets to aggregate.

        Returns:
            Dict[str, Any]: The aggregated asset.
        """
        return {
            key: self[key].aggregate(*[asset[key] for asset in assets if key in asset])
            for key in self
        }

    def satisfies(
        self,
        assets: Dict[str, Any],
        constraints: Dict[str, Any],
        violations: bool = False,
    ) -> Union[bool, Dict[str, Dict[str, Any]]]:
        """Checks whether the given asset satisfies the provided constraints.

        Only functional assets that exist in both buckets are considered.
        If any key fails its individual `satisfies` check, it is treated as a violation.

        Args:
            assets (Dict[str, Any]): The dictionary of asset values to evaluate.
            constraints (Dict[str, Any]): The constraint values to satisfy.
            violations (bool, optional): If True, return a dictionary containing
                only the violated keys and their asset/constraint values.
                If False (default), return a boolean indicating overall satisfaction.

        Returns:
            Union[bool, Dict[str, Dict[str, Any]]]:
                - If `violations=False`: True if all constraints are satisfied,
                    False otherwise.
                - If `violations=True`: A dictionary of violations,
                    empty if all constraints pass.
        """
        violated = {
            key: {
                "featured": assets[key],
                "required": constraints[key],
            }
            for key in self
            if self[key].functional
            and key in constraints
            and not self[key].satisfies(assets[key], constraints[key])
        }
        return violated if violations else not violated

    def consume(
        self, assets: Dict[str, Any], amounts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consume the `amount` of the asset from the `asset`.

        Args:
            assets (Dict[str, Any]): The asset to consume from.
            amounts (Dict[str, Any]): The amount to consume.

        Returns:
            Dict[str, Any]: The remaining assets after the consumption.
        """
        return {
            key: (
                assets[key] - amounts[key]
                if isinstance(self[key], Additive) and key in amounts
                else assets[key]
            )
            for key in self
        }

    def is_consistent(
        self, assets: Dict[str, Any], violations: bool = False
    ) -> Union[bool, Dict[str, Any]]:
        """Check if the asset belongs to the interval [lower_bound, upper_bound].

        Args:
            assets (Dict[str, Any]): The assets to be checked.
            violations (bool, optional): If True, return a dictionary containing
                only the violated keys and their asset/constraint values.
                If False (default), return a boolean indicating overall satisfaction.

        Returns:
            Union[bool, Dict[str, Any]]:
                - If `violations=False`: True if all constraints are satisfied,
                    False otherwise.
                - If `violations=True`: A dictionary of violations,
                    empty if all assets are consistent.
        """
        violated = {
            key: v
            for key, v in assets.items()
            if key in self and not self[key].is_consistent(v)
        }

        return violated if violations else not violated

    def _init(self, random: Random) -> Dict[str, Any]:
        """Initialize the assets of the bucket.

        This is done by calling the `init_fn` function of each asset.

        Args:
            random (Random): The random number generator to use.

        Returns:
            Dict[str, Any]: The initialized asset.
        """
        return {
            k: self[k]._init(random)  # pylint: disable=protected-access
            for k in self
            if self[k].init_fn is not None
        }

    def flip(self):
        """Flip the assets of the bucket.

        It moves from node capabilities to service requirements.

        Returns:
            AssetBucket: The flipped asset bucket.
        """
        req_bucket = AssetBucket()
        for k, v in self.items():
            req_bucket[k] = v.flip()
        return req_bucket

    @property
    def lower_bound(self) -> Dict[str, Any]:
        """Return the lower bound of the asset bucket.

        i.e., the lower bound of each asset in the bucket.

        Returns:
            Dict[str, Any]: The lower bound of the asset bucket.
        """
        return {k: v.lower_bound for k, v in self.items()}

    @property
    def upper_bound(self) -> Dict[str, Any]:
        """Return the upper bound of the asset bucket.

        i.e., the upper bound of each asset in the bucket.

        Returns:
            Dict[str, Any]: The upper bound of the asset bucket.
        """
        return {k: v.upper_bound for k, v in self.items()}
