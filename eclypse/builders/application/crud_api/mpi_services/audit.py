"""MPI workflow for auditing."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class AuditService(Service):
    """Record a simple audit event."""

    async def step(self):
        """Handle the next item event emitted by the CRUD pipeline."""
        await self.item_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def item_request(self, sender_id, body):
        """Record an audit message and respond to the calling service."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "audit_response",
            "status": "recorded",
            "message": f"{body['action']}:{body['item_id']}",
        }
