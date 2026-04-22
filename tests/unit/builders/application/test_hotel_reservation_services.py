from __future__ import annotations

import pytest

from eclypse.builders.application.deathstarbench.hotel_reservation import (
    mpi_services as hotel_mpi,
)
from eclypse.builders.application.deathstarbench.hotel_reservation import (
    rest_services as hotel_rest,
)
from eclypse.remote.communication.rest.codes import HTTPStatusCode
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_hotel_reservation_services(monkeypatch):
    search = attach_service_logger(hotel_rest.SearchService("SearchService"))
    profile = attach_service_logger(hotel_rest.ProfileService("ProfileService"))
    payment = attach_service_logger(hotel_rest.PaymentService("PaymentService"))
    reservation = attach_service_logger(
        hotel_rest.ReservationService("ReservationService")
    )
    frontend = attach_service_logger(hotel_rest.FrontendService("FrontendService"))

    code, body = search.search("Pisa", 2)
    assert code == 200
    assert body["hotels"][0]["id"] == "h1"

    code, body = profile.profile(101)
    assert code == 200
    assert body["user"]["name"] == "Ada Lovelace"

    monkeypatch.setattr(
        "eclypse.builders.application.deathstarbench.hotel_reservation.rest_services.payment.rnd.randint",
        lambda _low, _high: 1234,
    )
    code, body = payment.pay("rsv-2001", 129.0)
    assert code == 200
    assert body["transaction_id"] == "txn-1234"

    reservation_rest = FakeRESTInterface(
        {
            ("POST", "PaymentService/pay"): {
                "transaction_id": "txn-1234",
                "status": "confirmed",
            }
        }
    )
    monkeypatch.setattr(
        type(reservation), "rest", property(lambda self: reservation_rest)
    )
    code, body = await reservation.reserve(
        hotel={"name": "Arno View", "price": 129.0},
        user={"name": "Ada Lovelace"},
    )
    assert code is HTTPStatusCode.CREATED
    assert body["transaction_id"] == "txn-1234"

    frontend_rest = FakeRESTInterface(
        {
            ("GET", "SearchService/search"): {
                "hotels": [{"id": "h1", "name": "Arno View", "price": 129.0}]
            },
            ("GET", "ProfileService/profile"): {
                "user": {"user_id": 101, "name": "Ada Lovelace"}
            },
            ("POST", "ReservationService/reserve"): {
                "reservation_id": "rsv-2001",
                "status": "confirmed",
            },
        }
    )
    monkeypatch.setattr(type(frontend), "rest", property(lambda self: frontend_rest))
    response = await frontend.step()
    assert response.body["reservation_id"] == "rsv-2001"

    mpi_search = attach_service_logger(hotel_mpi.SearchService("SearchService"))
    mpi_profile = attach_service_logger(hotel_mpi.ProfileService("ProfileService"))
    mpi_payment = attach_service_logger(hotel_mpi.PaymentService("PaymentService"))
    mpi_reservation = attach_service_logger(
        hotel_mpi.ReservationService("ReservationService")
    )
    mpi_frontend = attach_service_logger(hotel_mpi.FrontendService("FrontendService"))

    search_comm = set_mpi(
        mpi_search,
        [
            {
                "sender_id": "FrontendService",
                "request_type": "search_hotels",
                "city": "Pisa",
                "nights": 2,
            }
        ],
    )
    await mpi_search.step()
    assert search_comm.sent[0][0] == "FrontendService"
    assert search_comm.sent[0][1]["response_type"] == "search_results"

    profile_comm = set_mpi(
        mpi_profile,
        [
            {
                "sender_id": "FrontendService",
                "request_type": "get_profile",
                "user_id": 101,
            }
        ],
    )
    await mpi_profile.step()
    assert profile_comm.sent[0][1]["user"]["name"] == "Ada Lovelace"

    monkeypatch.setattr(
        "eclypse.builders.application.deathstarbench.hotel_reservation.mpi_services.payment.rnd.randint",
        lambda _low, _high: 1234,
    )
    payment_comm = set_mpi(
        mpi_payment,
        [
            {
                "sender_id": "ReservationService",
                "request_type": "charge_card",
                "reservation_id": "rsv-2001",
                "amount": 129.0,
            }
        ],
    )
    await mpi_payment.step()
    assert payment_comm.sent == [
        (
            "ReservationService",
            {
                "response_type": "payment_response",
                "reservation_id": "rsv-2001",
                "transaction_id": "txn-1234",
                "status": "confirmed",
            },
        )
    ]

    reservation_comm = set_mpi(
        mpi_reservation,
        [
            {
                "sender_id": "FrontendService",
                "request_type": "create_reservation",
                "hotel": {"name": "Arno View", "price": 129.0},
                "user": {"name": "Ada Lovelace"},
            },
            {
                "sender_id": "PaymentService",
                "transaction_id": "txn-1234",
                "status": "confirmed",
            },
        ],
    )
    await mpi_reservation.step()
    assert reservation_comm.sent[0][0] == "PaymentService"
    assert reservation_comm.sent[1][0] == "FrontendService"

    frontend_comm = set_mpi(
        mpi_frontend,
        [
            {"hotels": [{"id": "h1", "name": "Arno View", "price": 129.0}]},
            {"user": {"user_id": 101, "name": "Ada Lovelace"}},
            {"reservation_id": "rsv-2001", "status": "confirmed"},
        ],
    )
    frontend_response = await mpi_frontend.step()
    assert frontend_comm.sent[0][0] == "SearchService"
    assert frontend_comm.sent[1][0] == "ProfileService"
    assert frontend_comm.sent[2][0] == "ReservationService"
    assert frontend_response["reservation_id"] == "rsv-2001"
