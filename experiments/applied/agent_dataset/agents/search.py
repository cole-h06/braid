from datetime import datetime, timezone

from ..extraction.schema import (
    AgentResult,
    Observation,
    Retrieval,
)


def search_agent():

    return AgentResult(observations=(
        Observation(
            assertion_id="search.refund_window",
            source_id="search_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
            observed_at=datetime(2026, 1, 3, 9, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=("research_agent",),
            parent_assertion_ids=("research.refund_window",),
            retrievals=(
                Retrieval(
                    retrieval_id="search.refund_window.retrieval",
                    kind="document",
                    resource_id="policy_snapshot_A",
                    retrieved_at=datetime(
                        2026, 1, 3, 9, tzinfo=timezone.utc
                    ),
                ),
            ),
        ),
        Observation(
            assertion_id="search.shipping_cost",
            source_id="search_agent",
            entity="shipping",
            attribute="cost",
            value="free",
            observed_at=datetime(2026, 1, 3, 9, 5, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=(),
            parent_assertion_ids=(),
            retrievals=(
                Retrieval(
                    retrieval_id="search.shipping_cost.retrieval",
                    kind="document",
                    resource_id="policy_snapshot_A",
                    retrieved_at=datetime(
                        2026, 1, 3, 9, 5, tzinfo=timezone.utc
                    ),
                ),
            ),
        ),
        Observation(
            assertion_id="search.warranty",
            source_id="search_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
            observed_at=datetime(2026, 1, 3, 9, 10, tzinfo=timezone.utc),
            source_modified_at=None,
            upstream_source_ids=(),
            cited_source_ids=("research_agent",),
            parent_assertion_ids=("research.warranty",),
            retrievals=(
                Retrieval(
                    retrieval_id="search.warranty.retrieval",
                    kind="document",
                    resource_id="policy_snapshot_A",
                    retrieved_at=datetime(
                        2026, 1, 3, 9, 10, tzinfo=timezone.utc
                    ),
                ),
            ),
        ),
    ))
