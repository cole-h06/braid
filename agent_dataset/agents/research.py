from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Assertion, Evidence


def research_agent():

    assertions = [

        Assertion(
            assertion_id="research.refund_window",
            source_id="research_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            assertion_id="research.warranty",
            source_id="research_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),

        Assertion(
            assertion_id="research.return_shipping",
            source_id="research_agent",
            entity="return_shipping",
            attribute="customer_pays",
            value="yes",
        ),
    ]

    evidence = [
        Evidence(
            assertion_id="research.refund_window",
            observed_at=datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="research.warranty",
            observed_at=datetime(2026, 1, 1, 9, 5, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="research.return_shipping",
            observed_at=datetime(2026, 1, 1, 9, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ]

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )