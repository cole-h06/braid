from braid.engine import evaluate

from .dataset import DEPENDENCY_WEIGHTS, load_dataset
from .workflow.graph import build_graph
from .workflow.hybrid_dependency import compute_hybrid_dependency


def run_experiment(
    weights=None,
    debug=False,
):

    sources, observations = load_dataset()

    graph = build_graph(
        sources,
        observations,
    )

    hybrid = compute_hybrid_dependency(
        graph,
        sources,
        observations,
        DEPENDENCY_WEIGHTS if weights is None else weights,
    )

    graph.dependency_matrix = hybrid["dependency_matrix"]
    graph.confidence_matrix = hybrid["confidence_matrix"]

    result = evaluate(
        graph,
        debug=debug,
    )

    return {
        "sources": sources,
        "observations": observations,
        "graph": graph,
        "hybrid": hybrid,
        "evaluation": result,
    }


def print_matrix(
    source_ids,
    matrix,
):

    rows = [["", *source_ids]]
    for source_id in source_ids:
        rows.append([
            source_id,
            *[f"{matrix[source_id][other_id]:.6f}" for other_id in source_ids],
        ])

    column_widths = [
        max(len(cell) for cell in column)
        for column in zip(*rows)
    ]

    for row in rows:
        print("  ".join(
            cell.ljust(width)
            for cell, width in zip(row, column_widths)
        ).rstrip())


def main():

    experiment = run_experiment()

    source_ids = [
        source.source_id
        for source in experiment["sources"]
    ]

    print("=== Normalized Weights ===")
    print()

    for name, weight in experiment["hybrid"]["weights"].items():
        print(f"{name:<20} {weight:.6f}")

    print()
    print("=== Dependency Matrix ===")
    print()

    print_matrix(
        source_ids,
        experiment["hybrid"]["dependency_matrix"],
    )

    print()
    print("=== Source Reliability ===")
    print()

    reliability = experiment["evaluation"]["reliability"]

    for source_id, score in sorted(
        reliability.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{source_id:<20} {score:.6f}")

    print()
    print("=== Claim Support ===")
    print()

    claim_support = experiment["evaluation"]["claim_support"]

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
