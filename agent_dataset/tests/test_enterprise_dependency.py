import pytest

from agent_dataset.enterprise.data import ORDER
from agent_dataset.enterprise.workflow import run_enterprise


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
    "provenance": (1, 0, 0, 0.5, 0, 0, 0.5, 0, 0, 0.5),
    "lineage": (0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
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


def test_dependencies():

    matrix = run_enterprise()["hybrid"]["dependency_matrix"]

    assert pair_values(matrix) == pytest.approx((
        0.44166666666666665,
        0.19166666666666665,
        0.0,
        0.45,
        0.04166666666666666,
        0.0,
        0.15,
        0.0,
        0.024999999999999998,
        0.6,
    ))

    ranking = sorted(
        PAIRS,
        key=lambda pair: matrix[pair[0]][pair[1]],
        reverse=True,
    )

    assert ranking[:3] == [
        ("vendor", "research"),
        ("handbook", "research"),
        ("handbook", "faq"),
    ]


def test_directions():

    diagnostics = run_enterprise()["hybrid"]["diagnostics"]
    lineage = diagnostics["lineage_directions"]
    temporal = diagnostics["temporal_directions"]

    assert lineage["research"]["handbook"] == 1.0
    assert lineage["handbook"]["research"] == 0.0
    assert lineage["research"]["vendor"] == 1.0
    assert temporal["sql"]["handbook"] == 1.0
    assert temporal["handbook"]["sql"] == 0.0
    assert temporal["research"]["vendor"] == 1.0
