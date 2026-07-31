from datetime import datetime

import pytest

from pydantic import ValidationError

from agent_dataset.dataset import (
    AGENTS,
    SIMULATED_RELATIONSHIPS,
    load_dataset,
    validate_dataset,
)
from agent_dataset.extraction.schema import AgentResult, Evidence


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


def test_timestamps():

    # reject evidence without a valid timezone
    with pytest.raises(ValidationError):
        Evidence(
            assertion_id="example",
            observed_at="not-a-datetime",
            provenance_ids=(),
        )

    with pytest.raises(ValidationError):
        Evidence(
            assertion_id="example",
            observed_at=datetime(2026, 1, 1, 9),
            provenance_ids=(),
        )

    sources, assertions, evidence = load_dataset()

    # model_copy bypasses field validation so dataset validation sees bad data
    bad_time = evidence[0].model_copy(
        update={"observed_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        validate_dataset(
            sources,
            assertions,
            [bad_time, *evidence[1:]],
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
