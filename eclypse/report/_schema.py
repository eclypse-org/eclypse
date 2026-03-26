"""Shared tabular schema definitions for report readers and writers."""

DEFAULT_IDX_HEADER = ["timestamp", "event_id", "n_event", "callback_id"]

DEFAULT_REPORT_HEADERS = {
    "simulation": [*DEFAULT_IDX_HEADER, "value"],
    "application": [*DEFAULT_IDX_HEADER, "application_id", "value"],
    "service": [*DEFAULT_IDX_HEADER, "application_id", "service_id", "value"],
    "interaction": [*DEFAULT_IDX_HEADER, "application_id", "source", "target", "value"],
    "infrastructure": [*DEFAULT_IDX_HEADER, "value"],
    "node": [*DEFAULT_IDX_HEADER, "node_id", "value"],
    "link": [*DEFAULT_IDX_HEADER, "source", "target", "value"],
}
