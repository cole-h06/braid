from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from braid.engine import evaluate
from braid.graph import BipartiteGraph

from ..agents.api import api_agent
from ..agents.documents import document_agent
from ..agents.research import research_agent
from ..agents.search import search_agent
from ..agents.sql import sql_agent
from ..dataset import BASELINE_WEIGHTS, SOURCES, validate_dataset
from ..extraction.schema import (
    AgentResult,
    Assertion,
    Evidence,
    SourceMetadata,
)
from .graph import build_graph
from .hybrid_dependency import compute_hybrid_dependency


AGENT_ORDER = (
    "research_agent",
    "search_agent",
    "sql_agent",
    "document_agent",
    "api_agent",
)


def merge_results(
    left,
    right,
):

    overlap = left.keys() & right.keys()

    if overlap:
        raise ValueError("agent result already exists")

    return {
        **left,
        **right,
    }


class WorkflowState(TypedDict, total=False):

    results: Annotated[
        dict[str, AgentResult],
        merge_results,
    ]

    sources: tuple[SourceMetadata, ...]

    assertions: list[Assertion]

    evidence: list[Evidence]

    graph: BipartiteGraph

    hybrid: dict

    evaluation: dict


def research_node(state):

    return {
        "results": {
            "research_agent": research_agent(),
        }
    }


def search_node(state):

    return {
        "results": {
            "search_agent": search_agent(),
        }
    }


def sql_node(state):

    return {
        "results": {
            "sql_agent": sql_agent(),
        }
    }


def document_node(state):

    return {
        "results": {
            "document_agent": document_agent(),
        }
    }


def api_node(state):

    return {
        "results": {
            "api_agent": api_agent(),
        }
    }


def validate_node(state):

    validate_dataset(
        state["sources"],
        state["assertions"],
        state["evidence"],
    )

    return {}


def graph_node(state):

    graph = build_graph(
        state["sources"],
        state["assertions"],
    )

    return {
        "graph": graph,
    }


def build_pipeline(
    agent_nodes,
    order,
    sources,
    roots,
    collect_from,
    joins=(),
    weights=None,
    debug=False,
):

    weights = (
        BASELINE_WEIGHTS
        if weights is None
        else weights
    )

    def dependency_node(state):

        hybrid = compute_hybrid_dependency(
            state["graph"],
            state["sources"],
            state["assertions"],
            state["evidence"],
            weights,
        )

        graph = state["graph"]
        graph.dependency_matrix = hybrid["dependency_matrix"]

        return {
            "graph": graph,
            "hybrid": hybrid,
        }

    def evaluation_node(state):

        result = evaluate(
            state["graph"],
            debug=debug,
        )

        return {
            "evaluation": result,
        }

    def collect_node(state):

        assertions = []
        evidence = []

        # keep collection stable after the parallel agent nodes finish
        for source_id in order:

            result = state["results"][source_id]

            assertions.extend(result.assertions)
            evidence.extend(result.evidence)

        return {
            "sources": sources,
            "assertions": assertions,
            "evidence": evidence,
        }

    workflow = StateGraph(WorkflowState)

    for name, node in agent_nodes.items():
        workflow.add_node(name, node)

    workflow.add_node("collect", collect_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("build_graph", graph_node)
    workflow.add_node("dependency", dependency_node)
    workflow.add_node("evaluation", evaluation_node)

    for agent in roots:
        workflow.add_edge(START, agent)

    for parents, child in joins:
        workflow.add_edge(parents, child)

    # wait for every terminal agent before collecting their results
    workflow.add_edge(collect_from, "collect")

    workflow.add_edge("collect", "validate")
    workflow.add_edge("validate", "build_graph")
    workflow.add_edge("build_graph", "dependency")
    workflow.add_edge("dependency", "evaluation")
    workflow.add_edge("evaluation", END)

    return workflow.compile()


def build_workflow(
    weights=None,
    debug=False,
):

    agents = {
        "research": research_node,
        "search": search_node,
        "sql": sql_node,
        "document": document_node,
        "api": api_node,
    }

    return build_pipeline(
        agent_nodes=agents,
        order=AGENT_ORDER,
        sources=SOURCES,
        roots=tuple(agents),
        collect_from=tuple(agents),
        weights=weights,
        debug=debug,
    )


def run_workflow(
    weights=None,
    debug=False,
):

    workflow = build_workflow(
        weights=weights,
        debug=debug,
    )

    state = workflow.invoke({
        "results": {},
    })

    return {
        "sources": state["sources"],
        "assertions": state["assertions"],
        "evidence": state["evidence"],
        "graph": state["graph"],
        "hybrid": state["hybrid"],
        "evaluation": state["evaluation"],
    }
