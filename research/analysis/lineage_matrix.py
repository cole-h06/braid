"""Historical research diagnostic; not a normative BRAID estimator."""



def build_matrix(rows):

    matrix = {}

    parents = {}

    for source_id, domain, parent_source_id in rows:

        parents[source_id] = parent_source_id
        matrix[domain] = {}

    for source_id, domain, _ in rows:

        for other_source_id, other_domain, _ in rows:

            score = 0.0

            if source_id == other_source_id:
                score = 1.0

            elif parents[source_id] == other_source_id:
                score = 1.0

            elif parents[other_source_id] == source_id:
                score = 1.0

            matrix[domain][other_domain] = score

    return matrix



def print_matrix(matrix):

    domains = list(
        matrix.keys()
    )

    print()

    print(
        f'{"":20}',
        end=""
    )

    for domain in domains:

        print(
            f"{domain:20}",
            end=""
        )

    print()

    for domain in domains:

        print(
            f"{domain:20}",
            end=""
        )

        for other_domain in domains:

            print(
                f"{matrix[domain][other_domain]:<20.1f}",
                end=""
            )

        print()

