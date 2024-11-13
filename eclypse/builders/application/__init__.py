"""Module for the application builders. It has the following builders:

- SockShop: A microservice-based application that simulates an e-commerce platform, made of 7 microservices.
"""

from .sock_shop.application import get_sock_shop

__all__ = ["get_sock_shop"]
