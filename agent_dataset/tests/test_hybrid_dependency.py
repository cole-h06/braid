import math

from datetime import timedelta
from unittest.mock import Mock

import pytest

from agent_dataset.dataset import DEPENDENCY_WEIGHTS, load_dataset
from agent_dataset.workflow.graph import build_graph
from agent_dataset.workflow.hybrid_dependency import (
    SIGNAL_NAMES,
    claim_telemetry,
    compute_hybrid_dependency,
    normalize_weights,
)


def load_hybrid():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    return sources, hybrid


def test_signals():

    _, hybrid = load_hybrid()
    signals = hybrid["signals"]

    assert signals["citation"]["research_agent"]["search_agent"] == 1.0
    assert (
        signals["assertion_lineage"]["research_agent"]["search_agent"]
        == 1.0
    )
    assert signals["ownership"]["sql_agent"]["api_agent"] == 1.0

    for name in SIGNAL_NAMES:
        assert signals[name]["research_agent"]["api_agent"] == 0.0


def test_structure():

    _, hybrid = load_hybrid()
    graph = hybrid["signals"]["graph"]

    expected = {
        ("research_agent", "search_agent"): 7 / 36,
        ("research_agent", "sql_agent"): 7 / 36,
        ("research_agent", "document_agent"): 1 / 12,
        ("research_agent", "api_agent"): 0.0,
        ("search_agent", "sql_agent"): 7 / 36,
        ("search_agent", "document_agent"): 0.25,
        ("search_agent", "api_agent"): 0.0,
        ("sql_agent", "document_agent"): 1 / 12,
        ("sql_agent", "api_agent"): 0.0,
        ("document_agent", "api_agent"): 0.0,
    }

    for pair, value in expected.items():

        source_a, source_b = pair

        assert graph[source_a][source_b] == pytest.approx(value)


def test_directions():

    _, hybrid = load_hybrid()
    diagnostics = hybrid["diagnostics"]

    citation = diagnostics["citation_directions"]
    assertion_lineage = diagnostics["assertion_lineage_directions"]
    upstream = diagnostics["upstream_directions"]
    temporal = diagnostics["temporal_directions"]

    assert citation["search_agent"]["research_agent"] == 1.0
    assert citation["research_agent"]["search_agent"] == 0.0

    assert assertion_lineage["search_agent"]["research_agent"] == 1.0
    assert assertion_lineage["research_agent"]["search_agent"] == 0.0

    assert upstream["search_agent"]["research_agent"] == 0.0
    assert upstream["research_agent"]["search_agent"] == 0.0

    assert temporal["sql_agent"]["research_agent"] == 0.0
    assert temporal["research_agent"]["sql_agent"] == 0.0


def test_dependencies():

    _, hybrid = load_hybrid()
    matrix = hybrid["dependency_matrix"]

    selected = [
        matrix["research_agent"]["search_agent"],
        matrix["sql_agent"]["api_agent"],
        matrix["search_agent"]["document_agent"],
        matrix["research_agent"]["sql_agent"],
        matrix["research_agent"]["api_agent"],
    ]

    expected = [
        0.4291666666666667,
        0.1,
        0.0375,
        0.02916666666666666,
        0.0,
    ]

    assert selected == pytest.approx(expected)
    assert selected == sorted(selected, reverse=True)


def test_matrix():

    sources, hybrid = load_hybrid()

    matrices = list(hybrid["signals"].values())
    matrices.append(hybrid["dependency_matrix"])

    source_ids = [
        source.source_id
        for source in sources
    ]

    for matrix in matrices:

        for source_id in source_ids:

            assert matrix[source_id][source_id] == 0.0

            for other_id in source_ids:

                value = matrix[source_id][other_id]

                assert 0.0 <= value <= 1.0
                assert value == matrix[other_id][source_id]


def test_observability():

    sources, hybrid = load_hybrid()

    source_ids = [
        source.source_id
        for source in sources
    ]

    for name, matrix in hybrid["observability"].items():

        for source_id in source_ids:

            assert matrix[source_id][source_id] == 0.0

            for other_id in source_ids:

                if source_id == other_id:
                    continue

                if name == "temporal":
                    assert matrix[source_id][other_id] == 0.0
                else:
                    assert matrix[source_id][other_id] == 1.0

    confidence = hybrid["confidence_matrix"]

    for source_id in source_ids:

        assert confidence[source_id][source_id] == 0.0

        for other_id in source_ids:

            if source_id != other_id:
                assert confidence[source_id][other_id] == pytest.approx(0.9)


def test_missing_metadata():

    sources, assertions, evidence = load_dataset()

    evidence[0] = evidence[0].model_copy(update={
        "upstream_source_ids": None,
        "cited_source_ids": None,
        "parent_assertion_ids": None,
    })

    graph = build_graph(
        sources,
        assertions,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    observability = hybrid["observability"]

    assert (
        observability["upstream"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert (
        observability["citation"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert (
        observability["assertion_lineage"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert (
        hybrid["signals"]["upstream"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert (
        hybrid["signals"]["citation"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert (
        hybrid["signals"]["assertion_lineage"]["research_agent"]["api_agent"]
        == 0.0
    )

    assert hybrid["confidence_matrix"]["research_agent"]["api_agent"] == (
        pytest.approx(0.25)
    )

    # Positive relationships remain observable even when capture
    # is unavailable on the reverse side.
    assert (
        observability["citation"]["research_agent"]["search_agent"]
        == 1.0
    )

    assert (
        observability[
            "assertion_lineage"
        ]["research_agent"]["search_agent"]
        == 1.0
    )


def test_weights():

    weights = {
        name: value * 10
        for name, value in DEPENDENCY_WEIGHTS.items()
    }

    original = weights.copy()
    normalized = normalize_weights(weights)

    assert weights == original
    assert normalized == DEPENDENCY_WEIGHTS


def test_bad_weights():

    invalid = (
        {},
        {
            name: 0.0
            for name in SIGNAL_NAMES
        },
        {
            **DEPENDENCY_WEIGHTS,
            "graph": -1.0,
        },
        {
            **DEPENDENCY_WEIGHTS,
            "graph": math.inf,
        },
        {
            **DEPENDENCY_WEIGHTS,
            "graph": math.nan,
        },
        {
            "upstream": 1.0,
            "citation": 1.0,
        },
        {
            **DEPENDENCY_WEIGHTS,
            "extra": 1.0,
        },
    )

    for weights in invalid:

        with pytest.raises(ValueError):
            normalize_weights(weights)


def test_window():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    for window in (
        timedelta(0),
        timedelta(seconds=-1),
        Mock(total_seconds=lambda: math.inf),
    ):

        with pytest.raises(ValueError):
            compute_hybrid_dependency(
                graph,
                sources,
                assertions,
                evidence,
                DEPENDENCY_WEIGHTS,
                temporal_window=window,
            )


def test_alphas():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    source_values = [
        source.model_dump()
        for source in sources
    ]

    assertion_values = [
        assertion.model_dump()
        for assertion in assertions
    ]

    evidence_values = [
        item.model_dump()
        for item in evidence
    ]

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    citation_only = {
        name: float(name == "citation")
        for name in SIGNAL_NAMES
    }

    alternative = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        citation_only,
    )

    assert (
        hybrid["dependency_matrix"]
        != alternative["dependency_matrix"]
    )

    assert source_values == [
        source.model_dump()
        for source in sources
    ]

    assert assertion_values == [
        assertion.model_dump()
        for assertion in assertions
    ]

    assert evidence_values == [
        item.model_dump()
        for item in evidence
    ]


def test_alpha_confidence():

    sources, assertions, evidence = load_dataset()

    evidence[0] = evidence[0].model_copy(update={
        "upstream_source_ids": None,
        "cited_source_ids": None,
        "parent_assertion_ids": None,
    })

    graph = build_graph(
        sources,
        assertions,
    )

    source_values = [
        source.model_dump()
        for source in sources
    ]

    assertion_values = [
        assertion.model_dump()
        for assertion in assertions
    ]

    evidence_values = [
        item.model_dump()
        for item in evidence
    ]

    baseline = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    ownership_only = {
        name: float(name == "ownership")
        for name in SIGNAL_NAMES
    }

    alternative = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        ownership_only,
    )

    assert (
        baseline["dependency_matrix"]
        != alternative["dependency_matrix"]
    )

    assert (
        baseline["confidence_matrix"]
        != alternative["confidence_matrix"]
    )

    assert source_values == [
        source.model_dump()
        for source in sources
    ]

    assert assertion_values == [
        assertion.model_dump()
        for assertion in assertions
    ]

    assert evidence_values == [
        item.model_dump()
        for item in evidence
    ]


def test_telemetry():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    telemetry = claim_telemetry(
        graph,
        hybrid,
        0.15,
    )

    claims = telemetry["claims"]

    expected = {
        (
            "refund_policy",
            "window_days",
            "30",
        ): (
            4,
            3.1372549019607847,
        ),
        (
            "shipping",
            "cost",
            "free",
        ): (
            2,
            1.9277108433734937,
        ),
        (
            "warranty",
            "length_years",
            "2",
        ): (
            3,
            2.2641509433962264,
        ),
    }

    for claim_id, record in claims.items():

        source_count = len(
            graph.claim_to_sources[claim_id]
        )

        assert record["supporting_source_count"] == source_count

        if source_count == 1:

            assert record == {
                "supporting_source_count": 1,
                "estimated_independent_support_count": 1.0,
                "dependency_clusters": 1,
                "dependency_confidence": None,
            }

        else:

            count, independent_count = expected[claim_id]

            assert record["supporting_source_count"] == count

            assert record["estimated_independent_support_count"] == (
                pytest.approx(independent_count)
            )

            assert record["dependency_confidence"] == pytest.approx(0.9)


def test_clusters():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    thresholds = (
        0.15,
        0.25,
        0.30,
        0.45,
        0.60,
    )

    expected = {
        (
            "refund_policy",
            "window_days",
            "30",
        ): (
            3,
            3,
            3,
            4,
            4,
        ),
        (
            "shipping",
            "cost",
            "free",
        ): (
            2,
            2,
            2,
            2,
            2,
        ),
        (
            "warranty",
            "length_years",
            "2",
        ): (
            2,
            2,
            2,
            3,
            3,
        ),
    }

    for index, threshold in enumerate(thresholds):

        claims = claim_telemetry(
            graph,
            hybrid,
            threshold,
        )["claims"]

        for claim_id, clusters in expected.items():

            assert (
                claims[claim_id]["dependency_clusters"]
                == clusters[index]
            )

    refund = (
        "refund_policy",
        "window_days",
        "30",
    )

    matrix = hybrid["dependency_matrix"]

    assert matrix["research_agent"]["document_agent"] < 0.15
    assert matrix["document_agent"]["sql_agent"] < 0.15

    assert (
        claim_telemetry(
            graph,
            hybrid,
            0.15,
        )["claims"][refund]["dependency_clusters"]
        == 3
    )


def test_bad_threshold():

    sources, assertions, evidence = load_dataset()

    graph = build_graph(
        sources,
        assertions,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        DEPENDENCY_WEIGHTS,
    )

    for threshold in (
        -0.1,
        1.1,
        math.inf,
        math.nan,
    ):

        with pytest.raises(ValueError):
            claim_telemetry(
                graph,
                hybrid,
                threshold,
            )