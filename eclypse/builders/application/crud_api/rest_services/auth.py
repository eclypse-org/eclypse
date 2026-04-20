"""REST endpoints for authentication."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class AuthService(RESTService):
    """Validate an API key."""

    @rest.endpoint("/auth", "POST")
    def auth(self, api_key: str, **_):
        """Authorise the request and return a synthetic token."""
        self.logger.info("Received request | " + format_log_kv(api_key=api_key))
        return 200, {"token": f"token:{api_key}", "status": "authorized"}
