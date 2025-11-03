"""Module for defining asset spaces.

An asset space is a set of possible values for an asset. Possible asset spaces include:

- `Choice`: a value is chosen from a list of possible values.
- `Uniform`: a value is chosen from a uniform distribution.
- `Sample`: a sample of values is chosen from a population.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Optional,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    from random import Random


class AssetSpace:
    """Base class for asset spaces."""

    def __call__(self, random: Random):
        """Return a value from the asset space.

        Args:
            random (Random): The random number generator.

        Returns:
            Any: A value from the asset space.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


class Choice(AssetSpace):
    """Class to represent a choice between a set of values."""

    def __init__(self, choices: List[Any]):
        """Create a new Choice asset space.

        Args:
            choices (List[Any]): The possible values to choose from.
        """
        self.choices = choices

    def __call__(self, random: Random):
        """Return a value from the choices.

        Args:
            random (Random): The random number generator.

        Returns:
            Any: A value from the choices.
        """
        return random.choice(self.choices)


class Uniform(AssetSpace):
    """Class to represent a uniform distribution of values."""

    def __init__(self, low: float, high: float):
        """Create a new Uniform asset space.

        Args:
            low (float): The lower bound of the distribution.
            high (float): The upper bound of the distribution.
        """
        self.low = low
        self.high = high

    def __call__(self, random: Random):
        """Return a value from the uniform distribution.

        Args:
            random (Random): The random number generator.

        Returns:
            float: A value from the uniform distribution.
        """
        return random.uniform(self.low, self.high)


class IntUniform(AssetSpace):
    """Class to represent a uniform distribution of integer values."""

    def __init__(self, low: int, high: int, step: int = 1):
        """Create a new IntUniform asset space.

        Args:
            low (int): The lower bound of the distribution.
            high (int): The upper bound of the distribution.
            step (int): The step size for the distribution.
                Default is 1.
        """
        self.low = low
        self.high = high
        self.step = step

    def __call__(self, random: Random):
        """Return a value from the uniform distribution.

        Args:
            random (Random): The random number generator.

        Returns:
            int: A value from the uniform distribution.
        """
        return random.randrange(self.low, self.high + 1, self.step)


class Sample(AssetSpace):
    """Class to represent a sample of values from a population."""

    def __init__(
        self,
        population: List[Any],
        k: Union[int, Tuple[int, int]],
        counts: Optional[List[int]] = None,
    ):
        """Create a new Sample asset space.

        The sample is drawn from the population. The
        parameter `k` can be either an integer or a pair of integers representing the
        range from which to draw the sample size.

        Args:
            population (List[Any]): The population to sample from.
            k (Union[int, Tuple[int, int]]): The number of values to sample.
            counts (Optional[List[int]]): The counts for each element in the population.
        """
        self.population = population
        self.k = k
        self.counts = counts

    def __call__(self, random: Random):
        """Return a sample of values from the population.

        Args:
            random (Random): The random number generator.

        Returns:
            List[Any]: A sample of values from the population.
        """
        _k = self.k if isinstance(self.k, int) else random.randint(*self.k)
        return random.sample(self.population, _k, counts=self.counts)


__all__ = [
    "AssetSpace",
    "Choice",
    "Sample",
    "Uniform",
]
