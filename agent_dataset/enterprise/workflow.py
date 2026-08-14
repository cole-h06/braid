from datetime import datetime

from agent_dataset.dataset import DEPENDENCY_WEIGHTS
from agent_dataset.workflow.pipeline import build_pipeline

from .agents import (
    faq_agent,
    handbook_agent,
    research_agent,
    sql_agent,
    vendor_agent,
)
from .data import ORDER, SOURCES, controlled_clock, load_manifest


def build_enterprise(
    clock=controlled_clock,
    weights=None,
    debug=False,
):

    source_modified_at = datetime.fromisoformat(
        load_manifest()["research_source_modified_at"]
    )

    def handbook_node(state):

        return {
            "results": {
                "handbook": handbook_agent(clock()),
            }
        }

    def faq_node(state):

        return {
            "results": {
                "faq": faq_agent(clock()),
            }
        }

    def sql_node(state):

        return {
            "results": {
                "sql": sql_agent(clock()),
            }
        }

    def vendor_node(state):

        return {
            "results": {
                "vendor": vendor_agent(clock()),
            }
        }

    def research_node(state):

        return {
            "results": {
                "research": research_agent(
                    state["results"]["handbook"],
                    state["results"]["vendor"],
                    source_modified_at,
                    clock(),
                ),
            }
        }

    agents = {
        "handbook": handbook_node,
        "faq": faq_node,
        "sql": sql_node,
        "vendor": vendor_node,
        "research": research_node,
    }

    return build_pipeline(
        agent_nodes=agents,
        order=ORDER,
        sources=SOURCES,
        roots=("handbook", "faq", "sql", "vendor"),
        collect_from=("faq", "sql", "research"),
        joins=((
            ("handbook", "vendor"),
            "research",
        ),),
        weights=(
            DEPENDENCY_WEIGHTS
            if weights is None
            else weights
        ),
        debug=debug,
    )


def run_enterprise(
    clock=controlled_clock,
    weights=None,
    debug=False,
):

    workflow = build_enterprise(
        clock=clock,
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
