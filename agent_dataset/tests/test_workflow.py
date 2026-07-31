from agent_dataset.run import run_experiment
from agent_dataset.workflow.pipeline import (
    AGENT_ORDER,
    build_workflow,
    run_workflow,
)


def test_nodes():

    workflow = build_workflow()

    updates = workflow.stream(
        {"results": {}},
        stream_mode="updates",
    )

    nodes = {
        name
        for update in updates
        for name in update
    }

    assert nodes == {
        "research",
        "search",
        "sql",
        "document",
        "api",
        "collect",
        "validate",
        "build_graph",
        "dependency",
        "inference",
    }


def test_collection():

    workflow = build_workflow()

    state = workflow.invoke({
        "results": {},
    })

    assert set(state["results"]) == set(AGENT_ORDER)
    assert len(state["sources"]) == 5
    assert len(state["assertions"]) == 15
    assert len(state["evidence"]) == 15

    source_order = tuple(
        source.source_id
        for source in state["sources"]
    )

    source_ids = tuple(
        assertion.source_id
        for assertion in state["assertions"][::3]
    )

    evidence_ids = tuple(
        item.assertion_id
        for item in state["evidence"]
    )

    assertion_ids = tuple(
        assertion.assertion_id
        for assertion in state["assertions"]
    )

    assert source_order == AGENT_ORDER
    assert source_ids == AGENT_ORDER
    assert evidence_ids == assertion_ids
    assert not hasattr(state["graph"], "evidence")


def test_repeatability():

    first = run_workflow(debug=True)
    second = run_workflow(debug=True)

    assert first == second


def test_equivalence():

    sequential = run_experiment(debug=True)
    workflow = run_workflow(debug=True)

    assert workflow["sources"] == sequential["sources"]
    assert workflow["assertions"] == sequential["assertions"]
    assert workflow["evidence"] == sequential["evidence"]

    workflow_graph = workflow["graph"]
    sequential_graph = sequential["graph"]

    assert workflow_graph.source_to_claims == sequential_graph.source_to_claims
    assert workflow_graph.claim_to_sources == sequential_graph.claim_to_sources
    assert workflow_graph.source_names == sequential_graph.source_names
    assert workflow_graph.agreement_weights == sequential_graph.agreement_weights
    assert workflow_graph.claim_lookup == sequential_graph.claim_lookup
    assert (
        workflow_graph.source_to_assertions
        == sequential_graph.source_to_assertions
    )

    workflow_hybrid = workflow["hybrid"]
    sequential_hybrid = sequential["hybrid"]

    assert workflow_hybrid["signals"] == sequential_hybrid["signals"]
    assert (
        workflow_hybrid["diagnostics"]
        == sequential_hybrid["diagnostics"]
    )
    assert workflow_hybrid["weights"] == sequential_hybrid["weights"]
    assert (
        workflow_hybrid["dependency_matrix"]
        == sequential_hybrid["dependency_matrix"]
    )

    workflow_result = workflow["inference"]
    sequential_result = sequential["inference"]

    assert workflow_result["credibility"] == sequential_result["credibility"]
    assert workflow_result["claim_support"] == sequential_result["claim_support"]
    assert workflow_result["independence"] == sequential_result["independence"]
    assert workflow_result["iterations"] == sequential_result["iterations"]
