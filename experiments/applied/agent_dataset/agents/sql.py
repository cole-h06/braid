from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Observation


def sql_agent():

    return AgentResult(observations=(
        Observation(
            assertion_id="sql.refund_window",
            source_id="sql_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
            observed_at=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="sql.warranty",
            source_id="sql_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
            observed_at=datetime(2026, 1, 1, 10, 5, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Observation(
            assertion_id="sql.customer_tier",
            source_id="sql_agent",
            entity="customer",
            attribute="tier",
            value="gold",
            observed_at=datetime(2026, 1, 1, 10, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ))
