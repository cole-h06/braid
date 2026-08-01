from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Assertion, Evidence


def search_agent():

    assertions = [

        Assertion(
            assertion_id="search.refund_window",
            source_id="search_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            assertion_id="search.shipping_cost",
            source_id="search_agent",
            entity="shipping",
            attribute="cost",
            value="free",
        ),

        Assertion(
            assertion_id="search.warranty",
            source_id="search_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),
    ]

    evidence = [
        Evidence(
            assertion_id="search.refund_window",
            observed_at=datetime(2026, 1, 3, 9, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=("research_agent",),
            parent_assertion_ids=("research.refund_window",),
        ),
        Evidence(
            assertion_id="search.shipping_cost",
            observed_at=datetime(2026, 1, 3, 9, 5, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="search.warranty",
            observed_at=datetime(2026, 1, 3, 9, 10, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=("research_agent",),
            parent_assertion_ids=("research.warranty",),
        ),
    ]

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )
