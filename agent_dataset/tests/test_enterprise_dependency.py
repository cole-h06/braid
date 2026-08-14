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
    "upstream": (0, 1, 0, 1, 0, 0, 0, 0, 0, 1),
    "citation": (0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    "assertion_lineage": (0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
    "ownership": (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "temporal": (0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
    "graph": (
        5 / 18,
        5 / 18,
        0,
        1 / 6,
        5 / 18,
        0,
        1 / 6,
        0,
        1 / 6,
        1 / 6,
    ),
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

    for matrix in hybrid["observability"].values():
        for source_id in ORDER:
            assert matrix[source_id][source_id] == 0.0

            for other_id in ORDER:
                if source_id != other_id:
                    assert matrix[source_id][other_id] == 1.0

    confidence = hybrid["confidence_matrix"]

    for source_id in ORDER:
        assert confidence[source_id][source_id] == 0.0

        for other_id in ORDER:
            if source_id != other_id:
                assert confidence[source_id][other_id] == 1.0


def test_dependencies():

    matrix = run_enterprise()["hybrid"]["dependency_matrix"]

    assert pair_values(matrix) == pytest.approx((
        0.14166666666666666,
        0.39166666666666666,
        0.0,
        0.675,
        0.04166666666666666,
        0.0,
        0.024999999999999998,
        0.0,
        0.024999999999999998,
        0.775,
    ))

    ranking = sorted(
        PAIRS,
        key=lambda pair: matrix[pair[0]][pair[1]],
        reverse=True,
    )

    assert ranking[:3] == [
        ("vendor", "research"),
        ("handbook", "research"),
        ("handbook", "sql"),
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

    assert temporal["sql"]["handbook"] == 1.0
    assert temporal["handbook"]["sql"] == 0.0
    assert temporal["research"]["vendor"] == 1.0


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
            2.4242424242424243,
        ),
        ("northstar_returns", "shipping_fee", "USD 5"): (
            2,
            1.1267605633802817,
        ),
        ("northstar_returns", "shipping_fee", "customer pays"): (
            3,
            2.1686746987951806,
        ),
        ("northstar_returns", "warranty", "2 years"): (
            4,
            2.4242424242424243,
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
            }
        else:
            count, independent_count = expected[claim_id]

            assert record["supporting_source_count"] == count
            assert record["estimated_independent_support_count"] == (
                pytest.approx(independent_count)
            )
            assert record["dependency_confidence"] == 1.0


def test_clusters():

    result = run_enterprise()
    thresholds = (0.15, 0.25, 0.30, 0.45, 0.60)
    expected = {
        ("northstar_returns", "return_window", "30 days"): (
            2,
            2,
            2,
            3,
            3,
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
            3,
            3,
        ),
        ("northstar_returns", "warranty", "2 years"): (
            2,
            2,
            2,
            3,
            3,
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
