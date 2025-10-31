"""Package for every functionality related to a remote simulation.

It includes Remote nodes, services, communicaiton interfaces, and some utilities.
"""

from .utils.ray_interface import ray_backend

__all__ = ["ray_backend"]
