import math

from datetime import timedelta
from unittest.mock import Mock

import pytest

from agent_dataset.dataset import BASELINE_WEIGHTS, load_dataset
from agent_dataset.workflow.graph import build_graph
from agent_dataset.workflow.hybrid_dependency import (
    SIGNAL_NAMES,
    compute_hybrid_dependency,
    normalize_weights,
)


def build_hybrid():

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
        BASELINE_WEIGHTS,
    )

    return sources, hybrid


def test_signals():

    _, hybrid = build_hybrid()
    signals = hybrid["signals"]

    assert signals["lineage"]["research_agent"]["search_agent"] == 1.0
    assert signals["provenance"]["search_agent"]["document_agent"] == 1.0
    assert signals["ownership"]["sql_agent"]["api_agent"] == 1.0
    assert signals["temporal"]["research_agent"]["sql_agent"] == 1.0

    for name in SIGNAL_NAMES:
        assert signals[name]["research_agent"]["api_agent"] == 0.0


def test_graph_signals():

    _, hybrid = build_hybrid()
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

    _, hybrid = build_hybrid()
    diagnostics = hybrid["diagnostics"]

    lineage = diagnostics["lineage_directions"]
    temporal = diagnostics["temporal_directions"]

    assert lineage["search_agent"]["research_agent"] == 1.0
    assert lineage["research_agent"]["search_agent"] == 0.0
    assert temporal["sql_agent"]["research_agent"] == 1.0
    assert temporal["research_agent"]["sql_agent"] == 0.0


def test_dependencies():

    _, hybrid = build_hybrid()
    matrix = hybrid["dependency_matrix"]

    selected = [
        matrix["research_agent"]["search_agent"],
        matrix["search_agent"]["document_agent"],
        matrix["research_agent"]["sql_agent"],
        matrix["sql_agent"]["api_agent"],
        matrix["research_agent"]["api_agent"],
    ]

    expected = [
        0.32916666666666666,
        0.2875,
        0.17916666666666667,
        0.15,
        0.0,
    ]

    assert selected == pytest.approx(expected)
    assert selected == sorted(selected, reverse=True)


def test_matrix_bounds():

    sources, hybrid = build_hybrid()

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


def test_weight_normalization():

    weights = {
        name: value * 10
        for name, value in BASELINE_WEIGHTS.items()
    }

    original = weights.copy()
    normalized = normalize_weights(weights)

    assert weights == original
    assert normalized == BASELINE_WEIGHTS


def test_invalid_weights():

    invalid = (
        {},
        {name: 0.0 for name in SIGNAL_NAMES},
        {**BASELINE_WEIGHTS, "graph": -1.0},
        {**BASELINE_WEIGHTS, "graph": math.inf},
        {**BASELINE_WEIGHTS, "graph": math.nan},
        {"provenance": 1.0, "lineage": 1.0},
        {**BASELINE_WEIGHTS, "extra": 1.0},
    )

    for weights in invalid:
        with pytest.raises(ValueError):
            normalize_weights(weights)


def test_temporal_window():

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
                BASELINE_WEIGHTS,
                temporal_window=window,
            )


def test_alternative_weights():

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
        BASELINE_WEIGHTS,
    )

    provenance_only = {
        name: float(name == "provenance")
        for name in SIGNAL_NAMES
    }

    alternative = compute_hybrid_dependency(
        graph,
        sources,
        assertions,
        evidence,
        provenance_only,
    )

    assert (
        hybrid["dependency_matrix"]
        != alternative["dependency_matrix"]
    )

    assert source_values == [source.model_dump() for source in sources]
    assert assertion_values == [
        assertion.model_dump()
        for assertion in assertions
    ]
    assert evidence_values == [item.model_dump() for item in evidence]
