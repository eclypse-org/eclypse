"""MPI workflow for keyword inference."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv

KEYWORD_THRESHOLD = 5


class InferenceService(Service):
    """Infer a keyword from preprocessed features."""

    async def step(self):
        """Handle the next preprocessed audio feature vector."""
        await self.preprocess_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def preprocess_request(self, _sender_id, body):
        """Infer the most likely keyword from the extracted features."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        keyword = (
            "eclypse" if sum(body["features"]) > KEYWORD_THRESHOLD else "background"
        )
        return "ActionService", {
            "request_type": "dispatch_action",
            "window_id": body["window_id"],
            "keyword": keyword,
        }
