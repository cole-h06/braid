from braid.engine import PROPAGATION_WEIGHT, evaluate
from braid.graph import from_assertions


def test_conflict_reliability():
    graph = from_assertions([
        ("source-a", "attribute-a", "claim-a1"),
        ("source-b", "attribute-a", "claim-a1"),
        ("source-c", "attribute-a", "claim-a1"),
        ("source-d", "attribute-a", "claim-a2"),

        ("source-a", "attribute-b", "claim-b1"),
        ("source-b", "attribute-b", "claim-b1"),
        ("source-c", "attribute-b", "claim-b1"),
        ("source-d", "attribute-b", "claim-b2"),

        ("source-a", "attribute-c", "claim-c1"),
        ("source-b", "attribute-c", "claim-c1"),
        ("source-c", "attribute-c", "claim-c1"),
        ("source-d", "attribute-c", "claim-c2"),
    ])

    result = evaluate(graph)
    reliability = result["reliability"]

    assert reliability["source-a"] > reliability["source-d"]
    assert reliability["source-b"] > reliability["source-d"]
    assert reliability["source-c"] > reliability["source-d"]

    prior = 1.0 / 4
    assert reliability["source-d"] >= (
        (1.0 - PROPAGATION_WEIGHT) * prior
    )