"""MPI workflow for anomaly alerting."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv

ANOMALY_THRESHOLD = 2.5


class AlertService(Service):
    """Turn anomaly scores into responses."""

    async def step(self):
        """Handle the next inference result emitted by the pipeline."""
        await self.inference_request()

    @mpi.exchange(receive=True, send=True)
    def inference_request(self, _sender_id, body):
        """Map the anomaly score to a status and respond to the sensor."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "SensorService", {
            "response_type": "anomaly_response",
            "window_id": body["window_id"],
            "score": body["score"],
            "status": "alert" if body["score"] >= ANOMALY_THRESHOLD else "normal",
        }
