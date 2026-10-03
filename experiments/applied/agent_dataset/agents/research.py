from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Observation


def research_agent():

    return AgentResult(observations=(
        Observation(
            assertion_id="research.refund_window",
            source_id="research_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
            observed_at=datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="research.warranty",
            source_id="research_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
            observed_at=datetime(2026, 1, 1, 9, 5, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="research.return_shipping",
            source_id="research_agent",
            entity="return_shipping",
            attribute="customer_pays",
            value="yes",
            observed_at=datetime(2026, 1, 1, 9, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ))
