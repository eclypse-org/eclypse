"""MPI workflow for social-network identifier generation."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UniqueIdService(Service):
    """Assign post identifiers for compose-post requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the identifier counter."""
        super().__init__(service_id, store_step=store_step)
        self.next_post_id = 5000

    async def step(self):
        """Handle the next compose-post request from the workflow."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Assign a post id and forward the workflow to the text service."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.next_post_id += 1
        return "TextService", {
            **body,
            "post_id": self.next_post_id,
        }
