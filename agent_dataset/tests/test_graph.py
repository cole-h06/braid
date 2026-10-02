from agent_dataset.dataset import load_dataset
from agent_dataset.workflow.graph import build_graph


def load_graph():

    sources, assertions, _ = load_dataset()

    return build_graph(
        sources,
        assertions,
    )


def test_counts():

    graph = load_graph()

    assert len(graph.source_to_claims) == 5
    assert len(graph.claim_to_sources) == 9
    assert not hasattr(graph, "evidence")


def test_assertions():

    graph = load_graph()

    for assertions in graph.source_to_assertions.values():
        assert len(assertions) == 3


def test_conflicts():

    graph = load_graph()

    refund_30 = (
        "refund_policy",
        "window_days",
        "30",
    )

    refund_14 = (
        "refund_policy",
        "window_days",
        "14",
    )

    assert refund_30 in graph.claim_to_sources
    assert refund_14 in graph.claim_to_sources

    assert (
        graph.claim_lookup[refund_30]
        == graph.claim_lookup[refund_14]
    )

    assert refund_30 != refund_14
