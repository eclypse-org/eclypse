"""MPI workflow for text parsing and enrichment."""

import re

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv

_MENTION_RE = re.compile(r"@([a-zA-Z0-9_]+)")
_URL_RE = re.compile(r"https?://[^\\s]+")


class TextService(Service):
    """Extract mentions and URLs from post text."""

    async def step(self):
        """Handle the next text-enrichment request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Parse post text and forward the workflow to mention resolution."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "UserMentionService", {
            **body,
            "mentions": _MENTION_RE.findall(body["text"]),
            "urls": _URL_RE.findall(body["text"]),
        }
