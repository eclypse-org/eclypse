from __future__ import annotations

import pytest

from eclypse.builders.application import get_crud_api
from eclypse.remote.service.service import Service


def test_crud_api_builder():
    plain_app = get_crud_api(include_default_assets=True)
    mpi_app = get_crud_api(
        include_default_assets=True,
        communication_interface="mpi",
    )
    rest_app = get_crud_api(
        include_default_assets=True,
        communication_interface="rest",
    )

    assert plain_app.has_service_implementations is False
    assert mpi_app.has_service_implementations is True
    assert rest_app.has_service_implementations is True
    assert all(isinstance(service, Service) for service in mpi_app.services.values())
    assert all(isinstance(service, Service) for service in rest_app.services.values())
    assert plain_app.has_edge("GatewayService", "AuthService")
    assert len(plain_app.flows) == 2


def test_crud_api_rejects_unknown_interfaces():
    with pytest.raises(ValueError, match="Unknown communication interface"):
        get_crud_api(communication_interface="grpc")  # type: ignore[arg-type]
