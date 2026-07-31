import math

from credibility.engine import infer

from agent_dataset.enterprise.workflow import build_enterprise, run_enterprise
from agent_dataset.workflow.graph import build_graph


def test_nodes():

    workflow = build_enterprise()
    updates = workflow.stream(
        {"results": {}},
        stream_mode="updates",
    )
    nodes = [
        name
        for update in updates
        for name in update
    ]

    assert set(nodes) == {
        "handbook",
        "faq",
        "sql",
        "vendor",
        "research",
        "collect",
        "validate",
        "build_graph",
        "dependency",
        "inference",
    }
    assert nodes.index("research") > nodes.index("handbook")
    assert nodes.index("research") > nodes.index("vendor")
    assert nodes.index("collect") > nodes.index("research")
    assert nodes.index("collect") > nodes.index("faq")
    assert nodes.index("collect") > nodes.index("sql")


def test_repeatability():

    assert run_enterprise(debug=True) == run_enterprise(debug=True)


def test_inference():

    result = run_enterprise(debug=True)
    inference = result["inference"]

    assert all(
        math.isfinite(value)
        for value in inference["credibility"].values()
    )
    assert all(
        math.isfinite(value)
        for value in inference["claim_support"].values()
    )
    assert inference["iterations"] == 15

    singleton = (
        "northstar_returns",
        "return_window",
        "14 days",
    )

    assert inference["independence"][singleton] == {"vendor": 1.0}


def test_adjustment():

    result = run_enterprise()
    graph = build_graph(
        result["sources"],
        result["assertions"],
    )
    zero_dependency = infer(graph)
    claim = (
        "northstar_returns",
        "return_window",
        "30 days",
    )

    assert result["inference"]["claim_support"][claim] < (
        zero_dependency["claim_support"][claim]
    )
