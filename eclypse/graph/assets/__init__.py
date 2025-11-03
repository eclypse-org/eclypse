"""Package for defining asset classes.

Available classes are:

- `Asset`: The base and extendable class for all assets.
- `Additive`: Represents a numeric asset where the aggregation is additive.
- `Multiplicative`: Represents a numeric asset where the aggregation is multiplicative.
- `Concave`: Represents a numeric asset where the aggregation is concave.
- `Convex`: Represents a numeric asset where the aggregation is convex.
- `Symbolic`: Represents a symbolic asset (set of values with no order relation).
- `AssetBucket`: Represents a collection of assets.
"""

from .asset import Asset
from .additive import Additive
from .multiplicative import Multiplicative
from .concave import Concave
from .convex import Convex
from .symbolic import Symbolic
from .bucket import AssetBucket
from .space import AssetSpace

__all__ = [
    "Additive",
    "Asset",
    "AssetBucket",
    "AssetSpace",
    "Concave",
    "Convex",
    "Multiplicative",
    "Symbolic",
]
