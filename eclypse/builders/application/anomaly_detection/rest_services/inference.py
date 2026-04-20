"""REST endpoints for anomaly inference."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class InferenceService(RESTService):
    """Compute a simple anomaly score."""

    @rest.endpoint("/score", "POST")
    def score(self, window_id: int, features: dict, **_):
        """Estimate an anomaly score from extracted telemetry features."""
        self.logger.info(
            "Received request | "
            + format_log_kv(window_id=window_id, features=features)
        )
        score = features["max"] / max(features["mean"], 0.1)
        return 200, {"window_id": window_id, "score": round(score, 2)}
