from .analysis.evidence_independence import (
    build_pairwise_independence,
)


def compute_dependency_matrix(graph):

    independence = build_pairwise_independence(graph)

    dependency_matrix = {}

    for source_id in graph.source_to_claims:

        dependency_matrix[source_id] = {}

    for (source_a, source_b), value in independence.items():

        dependency = 1.0 - value

        dependency_matrix[source_a][source_b] = dependency
        dependency_matrix[source_b][source_a] = dependency

    print("Strongest dependencies")
    print()

    for source_id, dependencies in dependency_matrix.items():

        print(graph.source_names[source_id])

        top = sorted(
            dependencies.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]

        for other_id, dependency in top:

            print(
                f"    {graph.source_names[other_id]:<25}"
                f"{dependency:.3f}"
            )

        print()

    return dependency_matrix


def build(
    independence,
    source_names
):

    return score(
        independence,
        source_names
    )


def score(
    independence,
    source_names
):

    dependency = {}

    for source_id, domain in source_names.items():

        links = []

        for (
            a,
            b
        ), value in independence.items():

            if a != source_id:
                continue

            links.append(
                (
                    source_names[b],
                    1.0 - value
                )
            )

        links.sort(
            key=lambda x: x[1],
            reverse=True
        )

        dependency[domain] = links

    return dependency


def main():

    dependency = build()

    for domain, links in dependency.items():

        print()
        print(domain)

        for other, score in links[:10]:

            print(
                f"  {other:<24}"
                f"{score:.3f}"
            )


if __name__ == "__main__":
    main()