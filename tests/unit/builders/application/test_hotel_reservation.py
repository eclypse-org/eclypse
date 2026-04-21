from __future__ import annotations

import pytest

from eclypse.builders.application import get_hotel_reservation
from eclypse.remote.service.service import Service


def test_hotel_reservation_builder():
    plain_app = get_hotel_reservation(include_default_assets=True)
    mpi_app = get_hotel_reservation(
        include_default_assets=True,
        communication_interface="mpi",
    )
    rest_app = get_hotel_reservation(
        include_default_assets=True,
        communication_interface="rest",
    )

    assert plain_app.has_logic is False
    assert mpi_app.has_logic is True
    assert rest_app.has_logic is True
    assert all(isinstance(service, Service) for service in mpi_app.services.values())
    assert all(isinstance(service, Service) for service in rest_app.services.values())
    assert plain_app.has_edge("FrontendService", "SearchService")
    assert len(plain_app.flows) == 3


def test_hotel_reservation_rejects_unknown_interfaces():
    with pytest.raises(ValueError, match="Unknown communication interface"):
        get_hotel_reservation(communication_interface="grpc")  # type: ignore[arg-type]
