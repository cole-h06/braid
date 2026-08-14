import math

import pytest

from braid.engine import evaluate

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

                expected = 1.0 - (
                    dependency_sum
                    / (len(source_ids) - 1)
                )

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

    experiment = run_experiment(debug=True)
    graph = experiment["graph"]

    hybrid_support = experiment["evaluation"]["claim_support"]

    source_ids = graph.source_to_claims.keys()

    graph.dependency_matrix = {
        source_id: {
            other_id: 0.0
            for other_id in source_ids
        }
        for source_id in source_ids
    }

    independent_support = evaluate(graph)["claim_support"]

    shared_claims = (
        ("refund_policy", "window_days", "30"),
        ("warranty", "length_years", "2"),
        ("shipping", "cost", "free"),
    )

    for claim_id in shared_claims:
        assert hybrid_support[claim_id] < independent_support[claim_id]