"""REST endpoints for keyword inference."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv

KEYWORD_THRESHOLD = 5


class InferenceService(RESTService):
    """Infer a keyword from preprocessed features."""

    @rest.endpoint("/infer", "POST")
    def infer(self, window_id: int, features: list[float], **_):
        """Infer the most likely keyword from the extracted features."""
        self.logger.info(
            "Received request | "
            + format_log_kv(window_id=window_id, features=features)
        )
        keyword = "eclypse" if sum(features) > KEYWORD_THRESHOLD else "background"
        return 200, {"window_id": window_id, "keyword": keyword}
