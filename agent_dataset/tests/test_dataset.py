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


def test_dataset_shape():

    sources, assertions, evidence = load_dataset()

    assert len(sources) == 5
    assert len(assertions) == 15
    assert len(evidence) == 15
    assert len(SIMULATED_RELATIONSHIPS) == 5


def test_agents_are_deterministic():

    for agent in AGENTS:

        result = agent()

        assert isinstance(result, AgentResult)
        assert result == agent()


def test_one_evidence_per_assertion():

    sources, assertions, evidence = load_dataset()

    with pytest.raises(
        ValueError,
        match="exactly one evidence record",
    ):
        validate_dataset(
            sources,
            assertions,
            evidence + [evidence[0]],
        )


def test_evidence_timestamps():

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

    naive = evidence[0].model_copy(
        update={"observed_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        validate_dataset(
            sources,
            assertions,
            [naive, *evidence[1:]],
        )


def test_source_references():

    sources, assertions, evidence = load_dataset()

    unknown = assertions[0].model_copy(
        update={"source_id": "unknown"}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            [unknown, *assertions[1:]],
            evidence,
        )

    unknown = evidence[0].model_copy(
        update={"cited_source_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            assertions,
            [unknown, *evidence[1:]],
        )


def test_assertion_references():

    sources, assertions, evidence = load_dataset()

    unknown = evidence[0].model_copy(
        update={"assertion_id": "unknown"}
    )

    with pytest.raises(
        ValueError,
        match="unknown assertion",
    ):
        validate_dataset(
            sources,
            assertions,
            [unknown, *evidence[1:]],
        )

    unknown = evidence[0].model_copy(
        update={"parent_assertion_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown parent",
    ):
        validate_dataset(
            sources,
            assertions,
            [unknown, *evidence[1:]],
        )


def test_unique_ids():

    sources, assertions, evidence = load_dataset()

    with pytest.raises(
        ValueError,
        match="source IDs",
    ):
        validate_dataset(
            [*sources, sources[0]],
            assertions,
            evidence,
        )

    duplicate = assertions[1].model_copy(
        update={"assertion_id": assertions[0].assertion_id}
    )

    with pytest.raises(
        ValueError,
        match="assertion IDs",
    ):
        validate_dataset(
            sources,
            [assertions[0], duplicate, *assertions[2:]],
            evidence,
        )


def test_one_value_per_property():

    sources, assertions, evidence = load_dataset()

    duplicate = assertions[1].model_copy(
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
            [assertions[0], duplicate, *assertions[2:]],
            evidence,
        )
