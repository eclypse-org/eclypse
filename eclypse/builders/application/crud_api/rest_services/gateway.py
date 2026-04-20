"""REST workflow for the CRUD gateway."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class GatewayService(Service):
    """Drive a create-and-list workflow."""

    async def step(self):
        """Authenticate the client and create a demo item via REST."""
        auth_r = await self.rest.post("AuthService/auth", api_key="demo-key")
        self.logger.info(
            "Received response | "
            + format_log_kv(source="AuthService", body=auth_r.body)
        )
        item_r = await self.rest.post(
            "ItemService/items",
            token=auth_r.body["token"],
            item={"id": "item-1", "name": "demo", "status": "active"},
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="ItemService", body=item_r.body)
        )
        return item_r

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the gateway with REST communication enabled."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
