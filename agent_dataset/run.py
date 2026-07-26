from .agents.research import research_agent
from .agents.search import search_agent
from .agents.sql import sql_agent
from .agents.documents import document_agent
from .agents.api import api_agent

from .workflow.graph import build_graph

from credibility.engine import infer
from credibility.source_dependency import compute_dependency_matrix


def main():

    assertions = []

    assertions.extend(research_agent())
    assertions.extend(search_agent())
    assertions.extend(sql_agent())
    assertions.extend(document_agent())
    assertions.extend(api_agent())

    graph = build_graph(assertions)

    graph.dependency_matrix = compute_dependency_matrix(graph)

    result = infer(graph)

    credibility = result["credibility"]
    claim_support = result["claim_support"]

    print("=== Source Credibility ===")
    print()

    for source_id, score in sorted(
        credibility.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{source_id:<20} {score:.6f}")

    print()

    print("=== Claim Support ===")
    print()

    for claim_id, score in sorted(
        claim_support.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        entity, attribute, value = claim_id

        print(
            f"{entity:<20}"
            f"{attribute:<20}"
            f"{value:<12}"
            f"{score:.6f}"
        )


if __name__ == "__main__":
    main()