"""Module containing off-the-shelf asset spaces, together with the class to customise
them.

For the complete documentation, refer to the :py:mod:`~eclypse_core.graph.assets.space`
core package.
"""

from eclypse_core.graph.assets.space import (
    AssetSpace,
    Choice,
    IntUniform,
    Sample,
    Uniform,
)

__all__ = [
    "AssetSpace",
    "Choice",
    "Sample",
    "Uniform",
    "IntUniform",
]
