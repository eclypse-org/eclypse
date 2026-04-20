"""REST endpoints for anomaly alerting."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv

ANOMALY_THRESHOLD = 2.5


class AlertService(RESTService):
    """Turn anomaly scores into responses."""

    @rest.endpoint("/alert", "POST")
    def alert(self, window_id: int, score: float, **_):
        """Translate the anomaly score into a compact alert response."""
        self.logger.info(
            "Received request | " + format_log_kv(window_id=window_id, score=score)
        )
        return 200, {
            "window_id": window_id,
            "score": score,
            "status": "alert" if score >= ANOMALY_THRESHOLD else "normal",
        }
