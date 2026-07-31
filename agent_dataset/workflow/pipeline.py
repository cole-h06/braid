from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from credibility.engine import infer
from credibility.graph import CredibilityGraph

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

    graph: CredibilityGraph

    hybrid: dict

    inference: dict


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


def collect_node(state):

    assertions = []
    evidence = []

    # keep collection stable after the parallel agent nodes finish
    for source_id in AGENT_ORDER:

        result = state["results"][source_id]

        assertions.extend(result.assertions)
        evidence.extend(result.evidence)

    return {
        "sources": SOURCES,
        "assertions": assertions,
        "evidence": evidence,
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


def build_workflow(
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

    def inference_node(state):

        result = infer(
            state["graph"],
            debug=debug,
        )

        return {
            "inference": result,
        }

    workflow = StateGraph(WorkflowState)

    workflow.add_node("research", research_node)
    workflow.add_node("search", search_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("document", document_node)
    workflow.add_node("api", api_node)

    workflow.add_node("collect", collect_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("build_graph", graph_node)
    workflow.add_node("dependency", dependency_node)
    workflow.add_node("inference", inference_node)

    agents = [
        "research",
        "search",
        "sql",
        "document",
        "api",
    ]

    for agent in agents:
        workflow.add_edge(START, agent)

    # wait for every agent before collecting their results
    workflow.add_edge(agents, "collect")

    workflow.add_edge("collect", "validate")
    workflow.add_edge("validate", "build_graph")
    workflow.add_edge("build_graph", "dependency")
    workflow.add_edge("dependency", "inference")
    workflow.add_edge("inference", END)

    return workflow.compile()


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
        "inference": state["inference"],
    }
