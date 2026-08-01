from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Assertion, Evidence


def document_agent():

    assertions = [

        Assertion(
            assertion_id="document.refund_window",
            source_id="document_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            assertion_id="document.shipping_cost",
            source_id="document_agent",
            entity="shipping",
            attribute="cost",
            value="free",
        ),

        Assertion(
            assertion_id="document.support_hours",
            source_id="document_agent",
            entity="support",
            attribute="hours",
            value="24/7",
        ),
    ]

    evidence = [
        Evidence(
            assertion_id="document.refund_window",
            observed_at=datetime(2026, 1, 4, 9, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="document.shipping_cost",
            observed_at=datetime(2026, 1, 4, 9, 5, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
        Evidence(
            assertion_id="document.support_hours",
            observed_at=datetime(2026, 1, 4, 9, 10, tzinfo=timezone.utc),
            provenance_ids=("policy_snapshot_A",),
            cited_source_ids=(),
            parent_assertion_ids=(),
        ),
    ]

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )
