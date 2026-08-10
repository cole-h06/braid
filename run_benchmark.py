import os
import time

from braid.graph import BipartiteGraph
from braid.loader import load_from_csv
from braid.engine import evaluate
from braid.source_dependency import compute_dependency_matrix


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
        claim_lookup,
        source_to_assertions,
    ) = load_from_csv(
        benchmark
    )

    graph = BipartiteGraph(
        source_to_claims=source_to_claims,
        claim_to_sources=claim_to_sources,
        source_names=source_names,
        agreement_weights=agreement_weights,
        claim_lookup=claim_lookup,
        source_to_assertions=source_to_assertions,
    )

    graph.dependency_matrix = compute_dependency_matrix(
        graph
    )

    print("running assertion evaluation...")
    print()

    print("Graph Statistics")
    print("----------------")
    print(f"Sources:     {len(source_names)}")
    print(f"Claims:      {len(claim_to_sources)}")
    print(
        f"Assertions:  "
        f"{sum(len(v) for v in source_to_claims.values())}"
    )
    print()

    start = time.perf_counter()

    result = evaluate(
        graph
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    reliability = result["reliability"]

    print(
        f"Converged after "
        f"{result['iterations']} iterations"
    )

    print(
        f"Evaluation time: "
        f"{elapsed * 1000:.2f} ms"
    )
    print()

    for source_id, score in sorted(
        reliability.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(
            f"{source_names[source_id]:<25}"
            f"{score:.6f}"
        )


if __name__ == "__main__":
    main()
