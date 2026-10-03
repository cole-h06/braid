from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Observation


def document_agent():

    return AgentResult(observations=(
        Observation(
            assertion_id="document.refund_window",
            source_id="document_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
            observed_at=datetime(2026, 1, 4, 9, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="document.shipping_cost",
            source_id="document_agent",
            entity="shipping",
            attribute="cost",
            value="free",
            observed_at=datetime(2026, 1, 4, 9, 5, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="document.support_hours",
            source_id="document_agent",
            entity="support",
            attribute="hours",
            value="24/7",
            observed_at=datetime(2026, 1, 4, 9, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ))
