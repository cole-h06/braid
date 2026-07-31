from datetime import datetime, timezone

from ..extraction.schema import AgentResult, Assertion, Evidence


def sql_agent():

    assertions = [

        Assertion(
            assertion_id="sql.refund_window",
            source_id="sql_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            assertion_id="sql.warranty",
            source_id="sql_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),

        Assertion(
            assertion_id="sql.customer_tier",
            source_id="sql_agent",
            entity="customer",
            attribute="tier",
            value="gold",
        ),
    ]

    evidence = [
        Evidence(
            assertion_id="sql.refund_window",
            observed_at=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
            provenance_ids=(),
        ),
        Evidence(
            assertion_id="sql.warranty",
            observed_at=datetime(2026, 1, 1, 10, 5, tzinfo=timezone.utc),
            provenance_ids=(),
        ),
        Evidence(
            assertion_id="sql.customer_tier",
            observed_at=datetime(2026, 1, 1, 10, 10, tzinfo=timezone.utc),
            provenance_ids=(),
        ),
    ]

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )
