"""MPI workflow for item management."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ItemService(Service):
    """Create an item and emit an audit event."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the item store used by the CRUD workflow."""
        super().__init__(service_id, store_step=store_step)
        self.items: dict[str, dict[str, str]] = {}

    async def step(self):
        """Create the item, then wait for the audit confirmation."""
        await self.gateway_request()
        return await self.audit_request()

    @mpi.exchange(receive=True, send=True)
    def gateway_request(self, _sender_id, body):
        """Store the item and forward an audit event."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        item = body["item"]
        self.items[item["id"]] = item
        return "AuditService", {
            "request_type": "record_event",
            "item_id": item["id"],
            "action": "create",
        }

    @mpi.exchange(receive=True, send=True)
    def audit_request(self, _sender_id, body):
        """Return the updated item list after the audit succeeds."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "GatewayService", {
            "response_type": "crud_response",
            "status": body["status"],
            "items": list(self.items.values()),
        }
