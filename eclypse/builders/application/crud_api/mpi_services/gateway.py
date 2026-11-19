"""MPI workflow for the CRUD gateway."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.remote.utils import ResponseCode
from eclypse.utils import format_log_kv


class GatewayService(Service):
    """Drive a create-and-list workflow."""

    async def step(self):
        """Authenticate the client and create a demo item."""
        request = await self.auth_request()
        if request.response.code != ResponseCode.OK:
            self.logger.warning(str(request.response))
            return
        auth_response = (await self.mpi.recv()).data
        self.logger.info("Received response | " + format_log_kv(response=auth_response))
        request = await self.item_request(auth_response["token"])
        if request.response.code != ResponseCode.OK:
            self.logger.warning(str(request.response))
            return
        item_response = (await self.mpi.recv()).data
        self.logger.info("Received response | " + format_log_kv(response=item_response))
        return item_response

    @mpi.exchange(send=True)
    def auth_request(self):
        """Send a synthetic authentication request to the auth service."""
        return "AuthService", {
            "request_type": "authenticate",
            "api_key": "demo-key",
        }

    @mpi.exchange(send=True)
    def item_request(self, token: str):
        """Submit a create-item request with the authorised token."""
        return "ItemService", {
            "request_type": "create_item",
            "token": token,
            "item": {"id": "item-1", "name": "demo", "status": "active"},
        }
