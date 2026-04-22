"""MPI workflow for review identifier generation."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UniqueIdService(Service):
    """Assign review identifiers for compose-review requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the review identifier counter."""
        super().__init__(service_id, store_step=store_step)
        self.next_review_id = 7000

    async def step(self):
        """Handle the next compose-review request from the workflow."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Assign a review id and forward the request to movie lookup."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.next_review_id += 1
        return "MovieIdService", {
            **body,
            "review_id": self.next_review_id,
        }
