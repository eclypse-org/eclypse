"""REST endpoints for item management."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class ItemService(RESTService):
    """Create an item and emit an audit event."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the item store used by the CRUD workflow."""
        super().__init__(service_id, store_step=store_step)
        self.items: dict[str, dict[str, str]] = {}

    @rest.endpoint("/items", "POST")
    async def create_item(self, token: str, item: dict, **_):
        """Store the item, emit an audit event, and return all items."""
        self.logger.info("Received request | " + format_log_kv(token=token, item=item))
        self.items[item["id"]] = item
        audit_r = await self.rest.post(
            "AuditService/events",
            token=token,
            item_id=item["id"],
            action="create",
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="AuditService", body=audit_r.body)
        )
        return HTTPStatusCode.CREATED, {
            "status": audit_r.body["status"],
            "items": list(self.items.values()),
        }
