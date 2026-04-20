"""REST endpoints for audio preprocessing."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class PreprocessService(RESTService):
    """Turn raw samples into simple features."""

    @rest.endpoint("/preprocess", "POST")
    def preprocess(self, window_id: int, samples: list[float], **_):
        """Convert raw audio samples into a simple feature vector."""
        self.logger.info(
            "Received request | " + format_log_kv(window_id=window_id, samples=samples)
        )
        return 200, {
            "window_id": window_id,
            "features": [sample * 10 for sample in samples],
        }
