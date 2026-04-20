"""REST endpoints for auditing."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class AuditService(RESTService):
    """Record a simple audit event."""

    @rest.endpoint("/events", "POST")
    def record_event(self, token: str, item_id: str, action: str, **_):
        """Record an audit event for the authenticated item operation."""
        self.logger.info(
            "Received request | "
            + format_log_kv(token=token, item_id=item_id, action=action)
        )
        return 200, {
            "status": "recorded",
            "message": f"{token}:{action}:{item_id}",
        }
