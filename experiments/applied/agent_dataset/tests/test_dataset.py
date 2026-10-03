from datetime import datetime

import pytest

from pydantic import ValidationError

from agent_dataset.dataset import (
    AGENTS,
    load_dataset,
    validate_dataset,
)
from agent_dataset.extraction.schema import AgentResult, Observation


SIMULATED_RELATIONSHIPS = {
    ("research_agent", "search_agent"): "citation and assertion lineage",
    ("search_agent", "document_agent"): "shared upstream source",
    ("sql_agent", "api_agent"): "shared ownership",
    ("research_agent", "sql_agent"): "temporal dependency",
    ("research_agent", "api_agent"): "independent conflict",
}


def test_counts():

    sources, observations = load_dataset()

    assert len(sources) == 5
    assert len(observations) == 15
    assert len(SIMULATED_RELATIONSHIPS) == 5


def test_repeatability():

    # make sure the mock agents return the same data every run
    for agent in AGENTS:

        result = agent()

        assert isinstance(result, AgentResult)
        assert result == agent()


def test_duplicate_observations():

    sources, observations = load_dataset()

    # Observation assertion IDs must be unique.
    with pytest.raises(
        ValueError,
        match="assertion IDs must be unique",
    ):
        validate_dataset(
            sources,
            observations + [observations[0]],
        )


def test_missingness():

    missing = Observation(
        source_id="example_source",
        entity="example_entity",
        attribute="example_attribute",
        value="example_value",
        assertion_id="missing",
        observed_at="2026-01-01T09:00:00Z",
        upstream_source_ids=None,
        cited_source_ids=None,
        parent_assertion_ids=None,
        source_modified_at=None,
    )

    observed = Observation(
        source_id="example_source",
        entity="example_entity",
        attribute="example_attribute",
        value="example_value",
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

    # reject observations without valid timezone aware timestamps
    with pytest.raises(ValidationError):
        Observation(
            source_id="example_source",
            entity="example_entity",
            attribute="example_attribute",
            value="example_value",
            assertion_id="example",
            observed_at="not-a-datetime",
            upstream_source_ids=(),
        )

    with pytest.raises(ValidationError):
        Observation(
            source_id="example_source",
            entity="example_entity",
            attribute="example_attribute",
            value="example_value",
            assertion_id="example",
            observed_at=datetime(2026, 1, 1, 9),
            upstream_source_ids=(),
        )

    with pytest.raises(ValidationError):
        Observation(
            source_id="example_source",
            entity="example_entity",
            attribute="example_attribute",
            value="example_value",
            assertion_id="example",
            observed_at="2026-01-01T09:00:00Z",
            upstream_source_ids=(),
            source_modified_at=datetime(2026, 1, 1, 8),
        )

    sources, observations = load_dataset()

    # model_copy bypasses field validation so dataset validation sees bad data
    bad_time = observations[0].model_copy(
        update={"observed_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="observed_at must be timezone-aware",
    ):
        validate_dataset(
            sources,
            [bad_time, *observations[1:]],
        )

    bad_modified_time = observations[0].model_copy(
        update={"source_modified_at": datetime(2026, 1, 1, 9)}
    )

    with pytest.raises(
        ValueError,
        match="source modification timestamps must be timezone-aware",
    ):
        validate_dataset(
            sources,
            [bad_modified_time, *observations[1:]],
        )


def test_sources():

    sources, observations = load_dataset()

    bad_source = observations[0].model_copy(
        update={"source_id": "unknown"}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            [bad_source, *observations[1:]],
        )

    external_upstream = observations[0].model_copy(
        update={"upstream_source_ids": ("unknown",)}
    )

    validate_dataset(sources, [external_upstream, *observations[1:]])
    bad_upstream = observations[0].model_copy(
        update={"upstream_source_ids": (observations[0].source_id,)}
    )

    with pytest.raises(
        ValueError,
        match="itself as upstream",
    ):
        validate_dataset(
            sources,
            [bad_upstream, *observations[1:]],
        )

    bad_citation = observations[0].model_copy(
        update={"cited_source_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown source",
    ):
        validate_dataset(
            sources,
            [bad_citation, *observations[1:]],
        )


def test_observations():

    sources, observations = load_dataset()

    bad_parent = observations[0].model_copy(
        update={"parent_assertion_ids": ("unknown",)}
    )

    with pytest.raises(
        ValueError,
        match="unknown parent",
    ):
        validate_dataset(
            sources,
            [bad_parent, *observations[1:]],
        )


def test_ids():

    sources, observations = load_dataset()

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
            observations,
        )

    duplicate_assertion = observations[1].model_copy(
        update={"assertion_id": observations[0].assertion_id}
    )

    with pytest.raises(
        ValueError,
        match="assertion IDs",
    ):
        validate_dataset(
            sources,
            [observations[0], duplicate_assertion, *observations[2:]],
        )


def test_values():

    sources, observations = load_dataset()

    # conflicts can exist across sources, but not within one source
    duplicate_value = observations[1].model_copy(
        update={
            "entity": observations[0].entity,
            "attribute": observations[0].attribute,
        }
    )

    with pytest.raises(
        ValueError,
        match="multiple values",
    ):
        validate_dataset(
            sources,
            [observations[0], duplicate_value, *observations[2:]],
        )


def test_observation_boundary():

    _, observations = load_dataset()
    original = observations[0]
    payload = original.model_dump()
    payload.update(
        entity_namespace="policies",
        metadata={"extractor": {"version": 1}},
        dependency_signals={"citation": {"captured": True}},
    )
    observation = Observation.model_validate(payload)
    result = AgentResult(observations=(observation,))

    assert set(result.model_dump()) == {"observations"}
    assert AgentResult.model_validate_json(result.model_dump_json()) == result
    assert observation.entity_namespace == "policies"
    assert observation.metadata == {"extractor": {"version": 1}}
    assert observation.dependency_signals == {"citation": {"captured": True}}
    assert original.metadata == {}
    assert original.dependency_signals == {}

    observation.metadata["extra"] = True
    observation.dependency_signals["extra"] = True
    assert observations[1].metadata == {}
    assert observations[1].dependency_signals == {}
