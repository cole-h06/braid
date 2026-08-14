from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Assertion, Evidence


def api_agent():

    assertions = [

        Assertion(
            assertion_id="api.refund_window",
            source_id="api_agent",
            entity="refund_policy",
            attribute="window_days",
            value="14",
        ),

        Assertion(
            assertion_id="api.warranty",
            source_id="api_agent",
            entity="warranty",
            attribute="length_years",
            value="1",
        ),

        Assertion(
            assertion_id="api.shipping_cost",
            source_id="api_agent",
            entity="shipping",
            attribute="cost",
            value="5",
        ),
    ]

    evidence = [
        Evidence(
            assertion_id="api.refund_window",
            observed_at=datetime(2026, 1, 8, 9, tzinfo=timezone.utc),
            source_modified_at=datetime(
                2026, 1, 8, 8, tzinfo=timezone.utc
            ),
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="api.warranty",
            observed_at=datetime(2026, 1, 8, 9, 5, tzinfo=timezone.utc),
            source_modified_at=datetime(
                2026, 1, 8, 8, 5, tzinfo=timezone.utc
            ),
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="api.shipping_cost",
            observed_at=datetime(2026, 1, 8, 9, 10, tzinfo=timezone.utc),
            source_modified_at=datetime(
                2026, 1, 8, 8, 10, tzinfo=timezone.utc
            ),
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ]

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )