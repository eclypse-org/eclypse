"""MPI workflow for anomaly inference."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class InferenceService(Service):
    """Compute a simple anomaly score."""

    async def step(self):
        """Handle the next feature payload emitted by the extractor."""
        await self.feature_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def feature_request(self, _sender_id, body):
        """Estimate an anomaly score from the extracted features."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        score = body["features"]["max"] / max(body["features"]["mean"], 0.1)
        return "AlertService", {
            "request_type": "emit_alert",
            "window_id": body["window_id"],
            "score": round(score, 2),
        }
