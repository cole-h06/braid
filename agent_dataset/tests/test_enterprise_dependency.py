import pytest

from agent_dataset.enterprise.data import ORDER
from agent_dataset.enterprise.workflow import run_enterprise
from agent_dataset.workflow.hybrid_dependency import claim_telemetry


PAIRS = (
    ("handbook", "faq"),
    ("handbook", "sql"),
    ("handbook", "vendor"),
    ("handbook", "research"),
    ("faq", "sql"),
    ("faq", "vendor"),
    ("faq", "research"),
    ("sql", "vendor"),
    ("sql", "research"),
    ("vendor", "research"),
)


EXPECTED = {
    "upstream": (0, 1, 0, 1, 0, 0, 0, 0, 1, 1),
    "citation": (0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    "assertion_lineage": (0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    "ownership": (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "temporal": (0, 3 / 4, 0, 0, 0, 0, 0, 0, 0, 29 / 30),
    "graph": (0,) * 10,
    "retrieval": (0,) * 10,
}


def pair_values(matrix):

    return tuple(
        matrix[source_a][source_b]
        for source_a, source_b in PAIRS
    )


def test_signals():

    signals = run_enterprise()["hybrid"]["signals"]

    for name, expected in EXPECTED.items():
        assert pair_values(signals[name]) == pytest.approx(expected)


def test_matrix():

    hybrid = run_enterprise()["hybrid"]
    matrices = [
        *hybrid["signals"].values(),
        hybrid["dependency_matrix"],
    ]

    for matrix in matrices:
        for source_id in ORDER:
            assert matrix[source_id][source_id] == 0.0

            for other_id in ORDER:
                assert 0.0 <= matrix[source_id][other_id] <= 1.0
                assert matrix[source_id][other_id] == (
                    matrix[other_id][source_id]
                )


def test_observability():

    hybrid = run_enterprise()["hybrid"]

    matching = (1, 1, 0, 1, 1, 0, 1, 0, 1, 1)
    for name, matrix in hybrid["observability"].items():
        expected = (
            (0,) * 10 if name == "graph"
            else matching if name in ("temporal", "retrieval")
            else (1,) * 10
        )
        assert pair_values(matrix) == expected
        assert all(matrix[source][source] == 0.0 for source in ORDER)

    assert pair_values(hybrid["confidence_matrix"]) == pytest.approx(
        tuple(0.75 + 0.1 * matched for matched in matching)
    )


def test_dependencies():

    matrix = run_enterprise()["hybrid"]["dependency_matrix"]

    assert pair_values(matrix) == pytest.approx((
        0.1, 1, 0, 1, 0, 0, 0, 0, 1, 1,
    ))

    ranking = sorted(
        PAIRS,
        key=lambda pair: matrix[pair[0]][pair[1]],
        reverse=True,
    )

    assert ranking[:4] == [
        ("handbook", "sql"),
        ("handbook", "research"),
        ("sql", "research"),
        ("vendor", "research"),
    ]


def test_directions():

    diagnostics = run_enterprise()["hybrid"]["diagnostics"]

    upstream = diagnostics["upstream_directions"]
    citation = diagnostics["citation_directions"]
    assertion_lineage = diagnostics["assertion_lineage_directions"]
    temporal = diagnostics["temporal_directions"]

    assert upstream["sql"]["handbook"] == 1.0
    assert upstream["handbook"]["sql"] == 0.0
    assert upstream["research"]["handbook"] == 1.0
    assert upstream["research"]["vendor"] == 1.0

    assert citation["research"]["handbook"] == 1.0
    assert citation["research"]["vendor"] == 1.0
    assert citation["handbook"]["research"] == 0.0

    assert assertion_lineage["research"]["handbook"] == 1.0
    assert assertion_lineage["research"]["vendor"] == 1.0
    assert assertion_lineage["handbook"]["research"] == 0.0

    assert temporal["sql"]["handbook"] == 3 / 4
    assert temporal["handbook"]["sql"] == 3 / 4
    assert temporal["research"]["vendor"] == pytest.approx(29 / 30)


def test_telemetry():

    result = run_enterprise()
    claims = claim_telemetry(
        result["graph"],
        result["hybrid"],
        0.15,
    )["claims"]
    expected = {
        ("northstar_returns", "return_window", "30 days"): (
            4,
            80 / 51,
        ),
        ("northstar_returns", "shipping_fee", "USD 5"): (
            2,
            1.0,
        ),
        ("northstar_returns", "shipping_fee", "customer pays"): (
            3,
            45 / 26,
        ),
        ("northstar_returns", "warranty", "2 years"): (
            4,
            80 / 51,
        ),
    }

    for claim_id, record in claims.items():
        source_count = len(result["graph"].claim_to_sources[claim_id])

        if source_count == 1:
            assert record == {
                "supporting_source_count": 1,
                "estimated_independent_support_count": 1.0,
                "dependency_clusters": 1,
                "dependency_confidence": None,
                "dependency_signal_coverage": None,
                "cluster_members": (tuple(sorted(result["graph"].claim_to_sources[claim_id])),),
            }
        else:
            count, independent_count = expected[claim_id]

            assert record["supporting_source_count"] == count
            assert record["estimated_independent_support_count"] == (
                pytest.approx(independent_count)
            )
            assert record["dependency_confidence"] == pytest.approx(0.85)


def test_clusters():

    result = run_enterprise()
    thresholds = (0.15, 0.25, 0.30, 0.45, 0.60)
    expected = {
        ("northstar_returns", "return_window", "30 days"): (
            2,
            2,
            2,
            2,
            2,
        ),
        ("northstar_returns", "shipping_fee", "USD 5"): (
            1,
            1,
            1,
            1,
            1,
        ),
        ("northstar_returns", "shipping_fee", "customer pays"): (
            2,
            2,
            2,
            2,
            2,
        ),
        ("northstar_returns", "warranty", "2 years"): (
            2,
            2,
            2,
            2,
            2,
        ),
    }

    for index, threshold in enumerate(thresholds):
        claims = claim_telemetry(
            result["graph"],
            result["hybrid"],
            threshold,
        )["claims"]

        for claim_id, clusters in expected.items():
            assert claims[claim_id]["dependency_clusters"] == clusters[index]
