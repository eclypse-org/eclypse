"""MPI workflow for media attachment composition."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class MediaService(Service):
    """Attach media metadata to a social-network post."""

    async def step(self):
        """Handle the next media-composition request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Build media descriptors and forward the workflow to user lookup."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "UserService", {
            **body,
            "media": [
                {"media_id": media_id, "media_type": media_type}
                for media_id, media_type in zip(
                    body["media_ids"],
                    body["media_types"],
                    strict=False,
                )
            ],
        }
