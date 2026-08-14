from datetime import datetime

import pytest

from pydantic import ValidationError

from agent_dataset.dataset import (
    AGENTS,
    load_dataset,
    validate_dataset,
)
from agent_dataset.extraction.schema import AgentResult, Evidence


SIMULATED_RELATIONSHIPS = {
    ("research_agent", "search_agent"): "citation and assertion lineage",
    ("search_agent", "document_agent"): "shared upstream source",
    ("sql_agent", "api_agent"): "shared ownership",
    ("research_agent", "sql_agent"): "temporal dependency",
    ("research_agent", "api_agent"): "independent conflict",
}


def test_counts():

    sources, assertions, evidence = load_dataset()

    assert len(sources) == 5
    assert len(assertions) == 15
    assert len(evidence) == 15
    assert len(SIMULATED_RELATIONSHIPS) == 5


def test_repeatability():

    # make sure the mock agents return the same data every run
    for agent in AGENTS:

        result = agent()

        assert isinstance(result, AgentResult)
        assert result == agent()


def test_evidence():

    sources, assertions, evidence = load_dataset()

    # each assertion should have one evidence record
    with pytest.raises(
        ValueError,
        match="exactly one evidence record",
    ):
        validate_dataset(
            sources,
            assertions,
            evidence + [evidence[0]],
        )


def test_missingness():

    missing = Evidence(
        assertion_id="missing",
        observed_at="2026-01-01T09:00:00Z",
        upstream_source_ids=None,
        cited_source_ids=None,
        parent_assertion_ids=None,
        source_modified_at=None,
    )

    observed = Evidence(
        assertion_id="observed",
        observed_at="2026-01-01T09:00:00Z",
        upstream_source_ids=(),
        cited_source_ids=(),
        parent_assertion_ids=(),
        source_modified_at="2026-01-01T08:00:00Z",
    )

    assert missing.upstream_source_ids is None
    assert missing.cited_source_ids is None
    assert missing.parent_assertion_ids is None
    assert missing.source_modified_at is None

    assert observed.upstream_source_ids == ()
    assert observed.cited_source_ids == ()
    assert observed.parent_assertion_ids == ()
    assert observed.source_modified_at is not None


def test_timestamps():

    # reject evidence without valid timezone aware timestamps
    with pytest.raises(ValidationError):
        Evidence(
            assertion_id="example",
            observed_at="not-a-datetime",
            upstream_source_ids=(),
        )

    with pytest.raises(ValidationError):
        Evidence(
            assertion_id="example",
            observed_at=datetime(2026, 1, 1, 9),
            upstream_source_ids=(),
        )

    with pytest.raises(ValidationError):
        Evidence(
            assertion_id="example",
            observed_at="2026-01-01T09:00:00Z",
            upstream_source_ids=(),
            source_modified_at=datetime(2026, 1, 1, 8),
        )

    sources, assertions, evidence = load_dataset()

    # model_copy bypasses field validation so dataset validation sees bad data
    bad_time = evidence[0].model_copy(
        update={"observed_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="observed_at must be timezone-aware",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_time, *evidence[1:]],
        )

    bad_modified_time = evidence[0].model_copy(
        update={"source_modified_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="source modification timestamps must be timezone-aware",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_modified_time, *evidence[1:]],
        )


def test_sources():

    sources, assertions, evidence = load_dataset()

    bad_source = assertions[0].model_copy(
        update={"source_id": "unknown"}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            [bad_source, *assertions[1:]],
            evidence,
        )

    bad_upstream = evidence[0].model_copy(
        update={"upstream_source_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown upstream source",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_upstream, *evidence[1:]],
        )

    bad_citation = evidence[0].model_copy(
        update={"cited_source_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_citation, *evidence[1:]],
        )


def test_assertions():

    sources, assertions, evidence = load_dataset()

    bad_assertion = evidence[0].model_copy(
        update={"assertion_id": "unknown"}
    )

    with pytest.raises(
        ValueError,
        match="unknown assertion",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_assertion, *evidence[1:]],
        )

    bad_parent = evidence[0].model_copy(
        update={"parent_assertion_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown parent",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_parent, *evidence[1:]],
        )


def test_ids():

    sources, assertions, evidence = load_dataset()

    duplicate_source = [
        *sources,
        sources[0],
    ]

    with pytest.raises(
        ValueError,
        match="source IDs",
    ):
        validate_dataset(
            duplicate_source,
            assertions,
            evidence,
        )

    duplicate_assertion = assertions[1].model_copy(
        update={"assertion_id": assertions[0].assertion_id}
    )

    with pytest.raises(
        ValueError,
        match="assertion IDs",
    ):
        validate_dataset(
            sources,
            [assertions[0], duplicate_assertion, *assertions[2:]],
            evidence,
        )


def test_values():

    sources, assertions, evidence = load_dataset()

    # conflicts can exist across sources, but not within one source
    duplicate_value = assertions[1].model_copy(
        update={
            "entity": assertions[0].entity,
            "attribute": assertions[0].attribute,
        }
    )

    with pytest.raises(
        ValueError,
        match="multiple values",
    ):
        validate_dataset(
            sources,
            [assertions[0], duplicate_value, *assertions[2:]],
            evidence,
        )