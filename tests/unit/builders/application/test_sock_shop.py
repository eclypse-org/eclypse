from __future__ import annotations

import pytest

from eclypse.builders.application import get_sock_shop
from eclypse.remote.service.service import Service


def test_sock_shop_builder_configures_supported_interfaces_and_flows():
    sock_shop = get_sock_shop(include_default_assets=True)
    remote_sock_shop = get_sock_shop(
        include_default_assets=True,
        communication_interface="mpi",
    )
    rest_sock_shop = get_sock_shop(
        include_default_assets=True,
        communication_interface="rest",
        flows=[["FrontendService", "CatalogService"]],
    )

    assert sock_shop.has_logic is False
    assert remote_sock_shop.has_logic is True
    assert rest_sock_shop.has_logic is True
    assert all(
        isinstance(service, Service) for service in remote_sock_shop.services.values()
    )
    assert all(
        isinstance(service, Service) for service in rest_sock_shop.services.values()
    )
    assert sock_shop.has_edge("FrontendService", "CatalogService")
    assert sock_shop.has_edge("CatalogService", "FrontendService")
    assert len(sock_shop.flows) == 5
    assert rest_sock_shop.flows == [["FrontendService", "CatalogService"]]

    with pytest.raises(ValueError, match="Unknown communication interface"):
        get_sock_shop(communication_interface="grpc")  # type: ignore[arg-type]
