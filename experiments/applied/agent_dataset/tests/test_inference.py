import math

import pytest

from agent_dataset.run import run_experiment


def test_repeatability():

    first = run_experiment(debug=True)
    second = run_experiment(debug=True)

    assert first["hybrid"] == second["hybrid"]
    assert first["evaluation"] == second["evaluation"]


def test_evaluation():

    experiment = run_experiment(debug=True)
    result = experiment["evaluation"]

    assert result["iterations"] < 1000
    assert sum(result["reliability"].values()) == pytest.approx(1.0)

    for score in result["reliability"].values():
        assert math.isfinite(score)
        assert score >= 0.0

    for score in result["claim_support"].values():
        assert math.isfinite(score)
        assert score >= 0.0

    assert (
        result["dependency_matrix"]
        == experiment["hybrid"]["dependency_matrix"]
    )


def test_independence():

    experiment = run_experiment(debug=True)

    graph = experiment["graph"]
    dependency = experiment["hybrid"]["dependency_matrix"]
    independence = experiment["evaluation"]["independence"]

    for claim_id, source_ids in graph.claim_to_sources.items():

        source_ids = tuple(source_ids)

        for source_id in source_ids:

            if len(source_ids) == 1:
                expected = 1.0
            else:
                dependency_sum = sum(
                    dependency[source_id][other_id]
                    for other_id in source_ids
                    if other_id != source_id
                )

                expected = 1.0 / (1.0 + dependency_sum)

            assert independence[claim_id][source_id] == pytest.approx(
                expected
            )


def test_singletons():

    experiment = run_experiment(debug=True)
    graph = experiment["graph"]
    independence = experiment["evaluation"]["independence"]

    for claim_id, source_ids in graph.claim_to_sources.items():

        if len(source_ids) == 1:

            source_id = next(iter(source_ids))

            assert independence[claim_id][source_id] == 1.0


def test_discount():

    from braid.engine import compute_degrees, score_claims

    experiment = run_experiment(debug=True)
    graph = experiment["graph"]
    result = experiment["evaluation"]
    degrees = compute_degrees(graph.source_to_claims)

    # Compare forward support at fixed reliability. Converged scores can
    # increase after feedback and normalization, even with discounts.
    def support(independence):
        return score_claims(
            result["reliability"],
            graph.claim_to_sources,
            graph.agreement_weights,
            independence,
            degrees,
        )

    discounted = support(result["independence"])
    independent = support({
        claim: {source: 1.0 for source in sources}
        for claim, sources in graph.claim_to_sources.items()
    })

    for claim in (
        ("refund_policy", "window_days", "30"),
        ("warranty", "length_years", "2"),
    ):
        assert discounted[claim] < independent[claim]

    shipping = ("shipping", "cost", "free")
    assert discounted[shipping] == independent[shipping]


def test_dependent_group():

    from braid.engine import compute_independence

    sources = ("a", "b", "c", "d")

    dependency = {
        source: {
            other: 0.0 if source == other else 1.0
            for other in sources
        }
        for source in sources
    }

    independence = compute_independence(
        {"claim": sources},
        dependency,
    )

    assert sum(independence["claim"].values()) == pytest.approx(1.0)


def test_partial_dependency():

    from braid.engine import compute_independence

    sources = ("a", "b", "c")

    dependency = {
        "a": {"a": 0.0, "b": 1.0, "c": 0.0},
        "b": {"a": 1.0, "b": 0.0, "c": 0.0},
        "c": {"a": 0.0, "b": 0.0, "c": 0.0},
    }

    independence = compute_independence(
        {"claim": sources},
        dependency,
    )

    assert independence["claim"]["a"] == pytest.approx(0.5)
    assert independence["claim"]["b"] == pytest.approx(0.5)
    assert independence["claim"]["c"] == pytest.approx(1.0)
    assert sum(independence["claim"].values()) == pytest.approx(2.0)


def test_partial_discount():

    from braid.engine import compute_independence

    dependency = {
        "a": {"a": 0.0, "b": 0.5},
        "b": {"a": 0.5, "b": 0.0},
    }

    independence = compute_independence(
        {"claim": ("a", "b")},
        dependency,
    )

    assert independence["claim"]["a"] == pytest.approx(2.0 / 3.0)
    assert independence["claim"]["b"] == pytest.approx(2.0 / 3.0)
    assert sum(independence["claim"].values()) == pytest.approx(4.0 / 3.0)
