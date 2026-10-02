import math

from braid.engine import evaluate

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
        "evaluation",
    }

    assert nodes.index("research") > nodes.index("handbook")
    assert nodes.index("research") > nodes.index("vendor")
    assert nodes.index("collect") > nodes.index("research")
    assert nodes.index("collect") > nodes.index("faq")
    assert nodes.index("collect") > nodes.index("sql")


def test_repeatability():

    assert run_enterprise(debug=True) == run_enterprise(debug=True)


def test_evaluation():

    result = run_enterprise(debug=True)
    evaluation = result["evaluation"]

    assert evaluation["iterations"] < 1000

    assert all(
        math.isfinite(value)
        for value in evaluation["reliability"].values()
    )

    assert all(
        math.isfinite(value)
        for value in evaluation["claim_support"].values()
    )

    singleton = (
        "northstar_returns",
        "return_window",
        "14 days",
    )

    assert evaluation["independence"][singleton] == {"vendor": 1.0}


def test_adjustment():

    result = run_enterprise()

    graph = build_graph(
        result["sources"],
        result["assertions"],
    )

    zero_dependency = evaluate(graph)

    claim = (
        "northstar_returns",
        "return_window",
        "30 days",
    )

    assert result["evaluation"]["claim_support"][claim] < (
        zero_dependency["claim_support"][claim]
    )