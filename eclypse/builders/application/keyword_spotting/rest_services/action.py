"""REST endpoints for acting on a detected keyword."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class ActionService(RESTService):
    """Convert a keyword into a final command response."""

    @rest.endpoint("/action", "POST")
    def action(self, window_id: int, keyword: str, **_):
        """Return the command associated with the detected keyword."""
        self.logger.info(
            "Received request | " + format_log_kv(window_id=window_id, keyword=keyword)
        )
        return 200, {
            "window_id": window_id,
            "command": "wake" if keyword == "eclypse" else "idle",
        }
