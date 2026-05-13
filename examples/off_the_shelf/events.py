"""Trivial scheduled events used by the off-the-shelf example."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.workflow import (
    after,
    every,
    once_at,
)

if TYPE_CHECKING:
    from eclypse.workflow.event import EclypseEvent


@every(steps=10, verbose=True)
def log_periodic_progress(triggering_event: EclypseEvent):
    """Log progress every ten simulation steps."""
    triggering_event.logger.success(
        f"Off-the-shelf periodic progress at step {triggering_event.n_calls}."
    )


@after(step=15, verbose=True)
def log_warmup_complete(triggering_event: EclypseEvent):
    """Log once the warmup portion has passed."""
    triggering_event.logger.success(
        f"Off-the-shelf warmup complete at step {triggering_event.n_calls}."
    )


@once_at(step=40, verbose=True)
def log_final_checkpoint(triggering_event: EclypseEvent):
    """Log a final checkpoint near the end of the run."""
    triggering_event.logger.success(
        f"Off-the-shelf final checkpoint at step {triggering_event.n_calls}."
    )


def get_events():
    """Return the scheduled events used by the example."""
    return [
        log_periodic_progress,
        log_warmup_complete,
        log_final_checkpoint,
    ]
