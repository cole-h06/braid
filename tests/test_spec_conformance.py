import json
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace

import pytest

from braid.dependency import SIGNAL_NAMES, claim_telemetry, cluster_members, combine_signals, compute_hybrid_dependency, normalize_weights
from braid.engine import ALGORITHM_VERSION, InferenceError, evaluate, normalize, update_sources
from braid.graph import from_assertions

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
    # Decode the frozen records without depending on an applied experiment's schema.
    sources = [SimpleNamespace(owner_id=None, **item) if "owner_id" not in item
               else SimpleNamespace(**item) for item in case["sources"]]
    assertions = [SimpleNamespace(**item) for item in case["assertions"]]
    evidence = []
    for item in case["evidence"]:
        values = dict(source_modified_at=None, upstream_source_ids=None,
                      cited_source_ids=None, parent_assertion_ids=None, retrievals=())
        values.update(item)
        for field in ("observed_at", "source_modified_at"):
            if values.get(field) is not None:
                values[field] = datetime.fromisoformat(values[field])
        values["retrievals"] = tuple(SimpleNamespace(**r) for r in values["retrievals"])
        evidence.append(SimpleNamespace(**values))
    return sources, assertions, evidence


@pytest.mark.parametrize("case", RECORDS["records"], ids=lambda case: case["name"])
def test_frozen_estimator(case):
    sources, assertions, evidence = records(case)
    graph = from_assertions(
        (a.source_id, (a.entity, a.attribute), (a.entity, a.attribute, a.value))
        for a in assertions
    )
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
    manifest = json.loads((FIXTURES.parents[1] / "spec" / "algorithm.json").read_text())
    assert manifest["algorithm_version"] == ALGORITHM_VERSION == VECTORS["algorithm_version"]
    assert RECORDS["algorithm_version"] == ALGORITHM_VERSION
    assert manifest["fixture_revision"] == VECTORS["fixture_revision"] == RECORDS["fixture_revision"]

