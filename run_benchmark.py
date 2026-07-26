import os

from credibility.graph import CredibilityGraph
from credibility.loader import load_from_csv
from credibility.engine import infer
from credibility.source_dependency import compute_dependency_matrix


def main():

    benchmark = os.path.join(
        os.path.dirname(__file__),
        "benchmark"
    )

    print()
    print("loading benchmark...")
    print()

    (
        source_to_claims,
        claim_to_sources,
        source_names,
        agreement_weights,
    ) = load_from_csv(
        benchmark
    )

    dependency_matrix = compute_dependency_matrix(
        source_to_claims
    )

    graph = CredibilityGraph(
        source_to_claims=source_to_claims,
        claim_to_sources=claim_to_sources,
        source_names=source_names,
        agreement_weights=agreement_weights,
        dependency_matrix=dependency_matrix,
    )

    print("running credibility inference...")
    print()

    result = infer(
        graph
    )

    credibility = result["credibility"]

    for source_id, score in sorted(
        credibility.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(
            f"{source_names[source_id]:<25}"
            f"{score:.6f}"
        )


if __name__ == "__main__":
    main()