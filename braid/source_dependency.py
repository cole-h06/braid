from .dependency import empty_matrix


def compute_dependency_matrix(graph):
    return empty_matrix(sorted(graph.source_to_claims))


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
