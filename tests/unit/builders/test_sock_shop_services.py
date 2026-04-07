from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.builders.application.sock_shop import (
    mpi_services,
    rest_services,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    CartService as MPICartService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    CatalogService as MPICatalogService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    FrontendService as MPIFrontendService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    OrderService as MPIOrderService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    PaymentService as MPIPaymentService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    ShippingService as MPIShippingService,
)
from eclypse.builders.application.sock_shop.mpi_services import (
    UserService as MPIUserService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    CartService as RESTCartService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    CatalogService as RESTCatalogService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    FrontendService as RESTFrontendService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    OrderService as RESTOrderService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    PaymentService as RESTPaymentService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    ShippingService as RESTShippingService,
)
from eclypse.builders.application.sock_shop.rest_services import (
    UserService as RESTUserService,
)
from eclypse.remote.communication.rest.codes import HTTPStatusCode


class FakeRestResponse:
    def __init__(self, body):
        self.body = body
        self.data = body


class AwaitableResult:
    def __init__(self, result):
        self.result = result

    def __await__(self):
        async def _resolve():
            return self.result

        return _resolve().__await__()


class FakeRESTInterface:
    def __init__(self):
        self.calls: list[tuple[str, str, dict[str, object]]] = []

    async def get(self, url: str, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if url == "CatalogService/catalog":
            return FakeRestResponse(
                {"products": [{"id": "1", "price": 19.99}, {"id": "2", "price": 29.99}]}
            )
        if url == "UserService/user":
            return FakeRestResponse({"user_id": kwargs["user_id"], "name": "Jane"})
        if url == "ShippingService/details":
            return FakeRestResponse({"shipping_details": {"carrier": "UPS"}})
        return FakeRestResponse(
            {
                "items": [
                    {"id": "1", "quantity": 2},
                    {"id": "2", "quantity": 1},
                ]
            }
        )

    async def post(self, url: str, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return FakeRestResponse({"status": "ok", "items": kwargs.get("items", [])})


class FakeMPIInterface:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent: list[tuple[str, dict[str, object]]] = []
        self.broadcasts: list[dict[str, object]] = []

    async def recv(self):
        return self.messages.pop(0)

    def send(self, recipient_id: str, body: dict[str, object]):
        self.sent.append((recipient_id, body))
        return AwaitableResult((recipient_id, body))

    def bcast(self, body: dict[str, object]):
        self.broadcasts.append(body)
        return AwaitableResult(("broadcast", body))


def _attach_service_logger(service):
    service.attach_node(
        SimpleNamespace(
            _logger=SimpleNamespace(
                bind=lambda **_: SimpleNamespace(info=lambda *_args: None)
            )
        )
    )
    return service


def test_rest_service_exports_and_endpoint_payloads():
    assert rest_services.CartService is RESTCartService
    assert rest_services.CatalogService is RESTCatalogService
    assert rest_services.UserService is RESTUserService

    cart_service = RESTCartService("CartService")
    catalog_service = RESTCatalogService("CatalogService")
    payment_service = RESTPaymentService("PaymentService")
    shipping_service = RESTShippingService("ShippingService")
    user_service = RESTUserService("UserService")

    cart_code, cart_body = cart_service.get_cart()
    catalog_code, catalog_body = catalog_service.get_catalog()
    payment_service.rnd = SimpleNamespace(randint=lambda low, high: low + high)
    payment_code, payment_body = payment_service.execute_payment(
        order_id=5, amount=20.0
    )
    shipping_code, shipping_body = shipping_service.get_shipping_detils(order_id=11)
    user_code, user_body = user_service.get_catalog(user_id=12345)

    assert cart_code == 200
    assert cart_body["items"][0]["id"] == "1"
    assert catalog_code == 200
    assert catalog_body["products"][1]["price"] == 29.99
    assert payment_code == 200
    assert payment_body["order_id"] == 5
    assert payment_body["status"] == "success"
    assert shipping_code == 200
    assert shipping_body["shipping_details"]["carrier"] == "UPS"
    assert user_code == 200
    assert user_body["user_id"] == 12345


@pytest.mark.asyncio
async def test_rest_frontend_and_order_workflows(monkeypatch):
    frontend = _attach_service_logger(RESTFrontendService("FrontendService"))
    order_service = _attach_service_logger(RESTOrderService("OrderService"))
    frontend_rest = FakeRESTInterface()
    order_rest = FakeRESTInterface()

    monkeypatch.setattr(type(frontend), "rest", property(lambda self: frontend_rest))
    monkeypatch.setattr(type(order_service), "rest", property(lambda self: order_rest))

    await frontend.step()

    post_call = next(call for call in frontend_rest.calls if call[0] == "POST")
    assert post_call[1] == "OrderService/order"
    assert post_call[2]["items"] == [
        {"id": "1", "amount": 39.98},
        {"id": "2", "amount": 29.99},
    ]

    response_code, response_body = await order_service.create_order(
        items=[{"id": "1", "amount": 39.98}, {"id": "2", "amount": 29.99}]
    )

    assert response_code is HTTPStatusCode.CREATED
    assert response_body["order_id"] == 54321
    assert response_body["shipping_details"]["carrier"] == "UPS"
    assert response_body["status"] == "success"


@pytest.mark.asyncio
async def test_mpi_service_exports_and_workflows(monkeypatch):
    assert mpi_services.CartService is MPICartService
    assert mpi_services.CatalogService is MPICatalogService
    assert mpi_services.UserService is MPIUserService

    catalog_service = _attach_service_logger(MPICatalogService("CatalogService"))
    cart_service = _attach_service_logger(MPICartService("CartService"))
    user_service = _attach_service_logger(MPIUserService("UserService"))
    shipping_service = _attach_service_logger(MPIShippingService("ShippingService"))
    payment_service = _attach_service_logger(MPIPaymentService("PaymentService"))
    order_service = _attach_service_logger(MPIOrderService("OrderService"))
    frontend_service = _attach_service_logger(MPIFrontendService("FrontendService"))

    catalog_mpi = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "catalog_data"}]
    )
    cart_mpi = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "cart_data"}]
    )
    user_mpi = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "user_data"}]
    )
    shipping_mpi = FakeMPIInterface(
        [
            {
                "sender_id": "OrderService",
                "request_type": "shipping_request",
                "order_id": 54321,
            }
        ]
    )
    payment_mpi = FakeMPIInterface(
        [
            {
                "sender_id": "OrderService",
                "request_type": "payment_request",
                "order_id": 54321,
            }
        ]
    )

    monkeypatch.setattr(
        type(catalog_service), "mpi", property(lambda self: catalog_mpi)
    )
    monkeypatch.setattr(type(cart_service), "mpi", property(lambda self: cart_mpi))
    monkeypatch.setattr(type(user_service), "mpi", property(lambda self: user_mpi))
    monkeypatch.setattr(
        type(shipping_service),
        "mpi",
        property(lambda self: shipping_mpi),
    )
    monkeypatch.setattr(
        type(payment_service),
        "mpi",
        property(lambda self: payment_mpi),
    )

    catalog_recipient, catalog_body = await catalog_service.frontend_request()
    cart_recipient, cart_body = await cart_service.frontend_request()
    user_recipient, user_body = await user_service.frontend_request()
    shipping_recipient, shipping_body = await shipping_service.order_request()
    payment_recipient, payment_body = await payment_service.order_request()

    assert catalog_recipient == "FrontendService"
    assert catalog_body["response_type"] == "catalog_response"
    assert cart_recipient == "FrontendService"
    assert cart_body["items"][0]["product_id"] == "1"
    assert user_recipient == "FrontendService"
    assert user_body["name"] == "John Doe"
    assert shipping_recipient == "OrderService"
    assert shipping_body["shipping_details"]["carrier"] == "UPS"
    assert payment_recipient == "OrderService"
    assert payment_body["response_type"] == "payment_response"

    frontend_mpi = FakeMPIInterface(
        [
            {"products": [{"id": "1", "price": 19.99}]},
            {"name": "Jane"},
            {"items": [{"product_id": "1", "quantity": 2}]},
            {"status": "success"},
        ]
    )
    monkeypatch.setattr(
        type(frontend_service), "mpi", property(lambda self: frontend_mpi)
    )

    await frontend_service.step()

    assert frontend_mpi.sent == [
        ("CatalogService", {"request_type": "catalog_data"}),
        ("UserService", {"request_type": "user_data", "user_id": 12345}),
        ("CartService", {"request_type": "cart_data", "user_id": 12345}),
        (
            "OrderService",
            {
                "request_type": "order_request",
                "user_id": 12345,
                "items": [{"product_id": "1", "quantity": 2}],
            },
        ),
    ]

    order_mpi = FakeMPIInterface(
        [
            {"sender_id": "FrontendService", "items": [{"id": "1"}, {"id": "2"}]},
            {"sender_id": "PaymentService", "transaction_id": 7777},
            {"sender_id": "ShippingService", "details": {"carrier": "UPS"}},
        ]
    )
    monkeypatch.setattr(type(order_service), "mpi", property(lambda self: order_mpi))
    monkeypatch.setattr(
        "eclypse.builders.application.sock_shop.mpi_services.order.rnd.randint",
        lambda low, high: 25,
    )

    await order_service.step()

    assert order_service.transaction_id == 7777
    assert order_service.shipping_details == {"carrier": "UPS"}
    assert order_mpi.sent == [
        (
            "PaymentService",
            {"request_type": "payment_request", "order_id": 54321, "amount": 50},
        ),
        ("ShippingService", {"request_type": "shipping_request", "order_id": 54321}),
        (
            "FrontendService",
            {
                "response_type": "order_response",
                "status": "success",
                "shipping_details": {"carrier": "UPS"},
                "transaction_id": 7777,
            },
        ),
    ]


@pytest.mark.asyncio
async def test_mpi_services_handle_invalid_requests_and_step_entrypoints(monkeypatch):
    catalog_service = _attach_service_logger(MPICatalogService("CatalogService"))
    cart_service = _attach_service_logger(MPICartService("CartService"))
    user_service = _attach_service_logger(MPIUserService("UserService"))
    shipping_service = _attach_service_logger(MPIShippingService("ShippingService"))
    payment_service = _attach_service_logger(MPIPaymentService("PaymentService"))
    order_service = _attach_service_logger(MPIOrderService("OrderService"))

    catalog_service._comm = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "unexpected"}]
    )
    cart_service._comm = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "unexpected"}]
    )
    user_service._comm = FakeMPIInterface(
        [{"sender_id": "FrontendService", "request_type": "unexpected"}]
    )
    shipping_service._comm = FakeMPIInterface(
        [{"sender_id": "OrderService", "request_type": "unexpected"}]
    )
    payment_service._comm = FakeMPIInterface(
        [{"sender_id": "OrderService", "request_type": "unexpected"}]
    )

    monkeypatch.setattr(
        "eclypse.builders.application.sock_shop.mpi_services.payment.rnd.choice",
        lambda options: options[0],
    )

    await catalog_service.step()
    await cart_service.step()
    await user_service.step()
    await shipping_service.step()
    await payment_service.step()

    assert catalog_service._comm.sent == [
        (
            "FrontendService",
            {"response_type": "catalog_response", "status": "Invalid request"},
        )
    ]
    assert cart_service._comm.sent == [
        (
            "FrontendService",
            {"response_type": "cart_response", "status": "Invalid request"},
        )
    ]
    assert user_service._comm.sent == [
        (
            "FrontendService",
            {"response_type": "user_response", "status": "Invalid request"},
        )
    ]
    assert shipping_service._comm.sent == [
        (
            "OrderService",
            {"response_type": "shipping_response", "status": "Invalid request"},
        )
    ]
    assert payment_service._comm.sent == [
        (
            "OrderService",
            {"response_type": "payment_response", "status": "Invalid request"},
        )
    ]

    order_service._comm = FakeMPIInterface(
        [{"sender_id": "ShippingService", "details": {"carrier": "UPS"}}]
    )
    order_service.transaction_id = None

    recipient, body = await order_service.shipping_request()

    assert recipient == "FrontendService"
    assert body == {"response_type": "order_response", "status": "failure"}
