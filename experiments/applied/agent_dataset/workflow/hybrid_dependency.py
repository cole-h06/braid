from datetime import timedelta

from braid.dependency import (
    SIGNAL_NAMES,
    claim_telemetry,
    compute_hybrid_dependency as _compute_hybrid_dependency,
    normalize_weights,
)

__all__ = [
    "SIGNAL_NAMES",
    "claim_telemetry",
    "compute_hybrid_dependency",
    "normalize_weights",
]


def compute_hybrid_dependency(
    graph, sources, observations, weights,
    temporal_window=timedelta(hours=2),
):
    """Adapt observations to BRAID's claim and provenance input slots.

    Both slots receive the same records; provenance stays on each observation.
    """
    return _compute_hybrid_dependency(
        graph, sources, observations, observations, weights,
        temporal_window=temporal_window,
    )
