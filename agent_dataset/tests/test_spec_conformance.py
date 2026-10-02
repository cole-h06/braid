import json
from pathlib import Path

import pytest

from agent_dataset.extraction.schema import Assertion, Evidence, SourceMetadata
from agent_dataset.workflow.graph import build_graph
from braid.dependency import (
    SIGNAL_NAMES, claim_telemetry, cluster_members, combine_signals,
    compute_hybrid_dependency, normalize_weights,
)
from braid.engine import ALGORITHM_VERSION, InferenceError, evaluate, normalize, update_sources
from braid.graph import from_assertions
from braid.loader import load_from_csv

FIXTURES = Path(__file__).parent / "fixtures"
VECTORS = json.loads((FIXTURES / "braid_sync_v1.json").read_text())
RECORDS = json.loads((FIXTURES / "braid_dependency_v1.json").read_text())
RELATIVE = VECTORS["relative_tolerance"]
ABSOLUTE = VECTORS["absolute_tolerance"]


def approx(value):
    return pytest.approx(value, rel=RELATIVE, abs=ABSOLUTE)


@pytest.mark.parametrize("case", VECTORS["propagation"], ids=lambda case: case["name"])
def test_frozen_propagation(case):
    graph = from_assertions(case["assertions"], case["dependency"], case["coverage"])
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(InferenceError, match="did not converge"):
            evaluate(graph)
        return
    result = evaluate(graph, debug=True)
    assert result["reliability"] == approx(expected["reliability"])
    assert result["iterations"] == expected["iterations"]
    assert result["metadata"]["algorithm_version"] == VECTORS["algorithm_version"]
    assert result["metadata"]["convergence_delta"] == approx(expected["delta"])
    assert result["metadata"]["convergence_delta"] < 1e-8
    telemetry = claim_telemetry(graph, {
        "dependency_matrix": graph.dependency_matrix,
        "confidence_matrix": graph.confidence_matrix,
    })
    for claim, record in expected["claims"].items():
        assert result["claim_support"][claim] == approx(record["support"])
        assert result["independence"][claim] == approx(record["independence"])
        assert result["contributions"][claim] == approx(record["contributions"])
        assert sum(result["contributions"][claim].values()) == approx(record["support"])
        assert result["attribute_maxima"][claim] == record["is_maximum"]
        assert list(result["conflicting_claims"][claim]) == record["conflicts"]
        for source in graph.claim_to_sources[claim]:
            assert graph.agreement_weights[source, claim] == approx(record["agreement"])
        values = telemetry["claims"][claim]
        assert values["estimated_independent_support_count"] == approx(record["effective_count"])
        assert values["dependency_signal_coverage"] == (
            None if record["coverage"] is None else approx(record["coverage"])
        )
        assert values["dependency_clusters"] is None
        assert values["cluster_members"] is None
    assert evaluate(from_assertions(
        reversed(case["assertions"]), case["dependency"], case["coverage"]
    )) == evaluate(graph)


@pytest.mark.parametrize("case", VECTORS["fusion"], ids=lambda case: case["name"])
def test_frozen_fusion(case):
    assert combine_signals(
        case["signals"], case["observable"], case["weights"], case["excluded"]
    ) == approx(case["expected"])


@pytest.mark.parametrize("case", VECTORS["clusters"], ids=lambda case: case["name"])
def test_frozen_clusters(case):
    assert cluster_members(case["sources"], case["dependency"], case["threshold"]) == tuple(
        tuple(component) for component in case["expected"]
    )


def records(case):
    sources = [SourceMetadata(display_name=item["source_id"], **item) for item in case["sources"]]
    assertions = [Assertion(**item) for item in case["assertions"]]
    evidence = [Evidence(**item) for item in case["evidence"]]
    return sources, assertions, evidence


@pytest.mark.parametrize("case", RECORDS["records"], ids=lambda case: case["name"])
def test_frozen_estimator(case):
    sources, assertions, evidence = records(case)
    graph = build_graph(sources, assertions)
    actual = compute_hybrid_dependency(graph, sources, assertions, evidence, case["weights"])
    expected = case["expected"]
    for name in SIGNAL_NAMES:
        assert actual["signals"][name]["a"]["b"] == approx(expected["signals"][name])
        assert actual["observability"][name]["a"]["b"] == expected["observable"][name]
    assert actual["dependency_matrix"]["a"]["b"] == approx(expected["dependency"])
    assert actual["confidence_matrix"]["a"]["b"] == approx(expected["coverage"])
    assert actual["excluded_signals"] == tuple(expected["excluded"])
    assert actual == compute_hybrid_dependency(
        graph, list(reversed(sources)), list(reversed(assertions)),
        list(reversed(evidence)), case["weights"],
    )


@pytest.mark.parametrize("assertions", [
    [], [("a", "x", "c"), ("a", "x", "c")],
    [("a", "x", "c"), ("a", "x", "d")],
    [("a", "x", "c"), ("b", "y", "c")],
])
def test_invalid_graph(assertions):
    with pytest.raises(ValueError):
        from_assertions(assertions)


@pytest.mark.parametrize("matrix", [
    {"a": {"a": 0}},
    {"a": {"a": 0, "b": 0}, "b": {"b": 0}},
    {"a": {"a": 0, "b": 0.2}, "b": {"a": 0.1, "b": 0}},
    {"a": {"a": 1, "b": 0}, "b": {"a": 0, "b": 0}},
    {"a": {"a": 0, "b": float("nan")}, "b": {"a": float("nan"), "b": 0}},
])
def test_invalid_matrix(matrix):
    with pytest.raises(ValueError):
        from_assertions([("a", "x", "c"), ("b", "x", "c")], matrix)


@pytest.mark.parametrize("bad", [-1, float("inf"), float("nan"), True])
def test_invalid_weight(bad):
    weights = dict(RECORDS["records"][0]["weights"], upstream=bad)
    with pytest.raises(ValueError):
        normalize_weights(weights)


def test_reverse_zero_attribute_and_numeric_failure():
    assert update_sources(
        {"c": 0.0, "d": 1.0}, {"a": ("c",), "b": ("d",)}, {"c": "x", "d": "y"},
    ) == {"a": 0.0, "b": 1.0}
    for vector in ({"a": 0.0}, {"a": float("inf")}):
        with pytest.raises(InferenceError):
            normalize(vector)


def test_manifest_and_fixture_version():
    manifest = json.loads((FIXTURES.parents[2] / "research" / "algorithm.json").read_text())
    assert manifest["algorithm_version"] == ALGORITHM_VERSION == VECTORS["algorithm_version"]
    assert RECORDS["algorithm_version"] == ALGORITHM_VERSION
    assert manifest["fixture_revision"] == VECTORS["fixture_revision"] == RECORDS["fixture_revision"]


def test_csv_adapter_uses_distinct_sources(tmp_path):
    (tmp_path / "sources.csv").write_text("source_id,name\n1,first\n2,second\n")
    (tmp_path / "claims.csv").write_text(
        "claim_id,product_id,attribute\n1,item,color\n2,item,color\n"
    )
    (tmp_path / "assertions.csv").write_text(
        "source_id,claim_id,value_string,value_numeric\n"
        "1,1,red,\n1,1,red,\n2,2,blue,\n"
    )
    source_claims, claim_sources, _, agreement, _, _ = load_from_csv(tmp_path)
    assert source_claims == {1: {1}, 2: {2}}
    assert claim_sources == {1: {1}, 2: {2}}
    assert agreement == {(1, 1): 0.5, (2, 2): 0.5}
