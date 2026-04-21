from __future__ import annotations

import pytest

from eclypse.builders.application.crud_api import mpi_services as crud_mpi
from eclypse.builders.application.crud_api import rest_services as crud_rest
from eclypse.remote.communication.rest.codes import HTTPStatusCode
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_crud_api_services(monkeypatch):
    auth = attach_service_logger(crud_rest.AuthService("AuthService"))
    audit = attach_service_logger(crud_rest.AuditService("AuditService"))
    item = attach_service_logger(crud_rest.ItemService("ItemService"))
    gateway = attach_service_logger(crud_rest.GatewayService("GatewayService"))

    code, body = auth.auth("demo-key")
    assert code == 200
    assert body["token"] == "token:demo-key"

    code, body = audit.record_event("token:demo", "item-1", "create")
    assert code == 200
    assert body["message"] == "token:demo:create:item-1"

    item_rest = FakeRESTInterface(
        {("POST", "AuditService/events"): {"status": "recorded"}}
    )
    monkeypatch.setattr(type(item), "rest", property(lambda self: item_rest))
    code, body = await item.create_item(
        token="token:demo",
        item={"id": "item-1", "name": "demo", "status": "active"},
    )
    assert code is HTTPStatusCode.CREATED
    assert body["items"][0]["id"] == "item-1"

    gateway_rest = FakeRESTInterface(
        {
            ("POST", "AuthService/auth"): {"token": "token:demo-key"},
            ("POST", "ItemService/items"): {
                "status": "recorded",
                "items": [{"id": "item-1"}],
            },
        }
    )
    monkeypatch.setattr(type(gateway), "rest", property(lambda self: gateway_rest))
    response = await gateway.step()
    assert response.body["status"] == "recorded"

    mpi_auth = attach_service_logger(crud_mpi.AuthService("AuthService"))
    mpi_audit = attach_service_logger(crud_mpi.AuditService("AuditService"))
    mpi_item = attach_service_logger(crud_mpi.ItemService("ItemService"))
    mpi_gateway = attach_service_logger(crud_mpi.GatewayService("GatewayService"))

    auth_comm = set_mpi(
        mpi_auth,
        [
            {
                "sender_id": "GatewayService",
                "request_type": "authenticate",
                "api_key": "demo-key",
            }
        ],
    )
    await mpi_auth.step()
    assert auth_comm.sent[0][1]["token"] == "token:demo-key"

    audit_comm = set_mpi(
        mpi_audit,
        [
            {
                "sender_id": "ItemService",
                "request_type": "record_event",
                "item_id": "item-1",
                "action": "create",
            }
        ],
    )
    await mpi_audit.step()
    assert audit_comm.sent[0][1]["status"] == "recorded"

    item_comm = set_mpi(
        mpi_item,
        [
            {
                "sender_id": "GatewayService",
                "request_type": "create_item",
                "token": "token:demo",
                "item": {"id": "item-1", "name": "demo", "status": "active"},
            },
            {"sender_id": "AuditService", "status": "recorded"},
        ],
    )
    await mpi_item.step()
    assert item_comm.sent[0][0] == "AuditService"
    assert item_comm.sent[1][0] == "GatewayService"
    assert item_comm.sent[1][1]["items"][0]["id"] == "item-1"

    gateway_comm = set_mpi(
        mpi_gateway,
        [
            {"token": "token:demo-key"},
            {"status": "recorded", "items": [{"id": "item-1"}]},
        ],
    )
    response = await mpi_gateway.step()
    assert gateway_comm.sent[0][0] == "AuthService"
    assert gateway_comm.sent[1][0] == "ItemService"
    assert response["status"] == "recorded"
