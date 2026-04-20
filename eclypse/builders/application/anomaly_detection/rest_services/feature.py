"""REST endpoints for feature extraction."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class FeatureService(RESTService):
    """Extract simple features from telemetry."""

    @rest.endpoint("/features", "POST")
    def features(self, window_id: int, samples: list[float], **_):
        """Compute compact statistics for a telemetry window."""
        self.logger.info(
            "Received request | " + format_log_kv(window_id=window_id, samples=samples)
        )
        max_sample = max(samples)
        mean_sample = sum(samples) / len(samples)
        return 200, {
            "window_id": window_id,
            "features": {"max": max_sample, "mean": mean_sample},
        }
