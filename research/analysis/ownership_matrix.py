"""Historical research diagnostic; not used by the current BRAID estimator."""


def build_matrix(rows):

    matrix = {}

    for _, domain, owner in rows:

        matrix[domain] = {}

        for _, other_domain, other_owner in rows:

            if owner == other_owner:
                matrix[domain][other_domain] = 1.0
            else:
                matrix[domain][other_domain] = 0.0

    return matrix



def print_matrix(matrix):

    domains = list(matrix.keys())

    print()

    print(f'{"":20}', end="")

    for domain in domains:
        print(f"{domain:20}", end="")

    print()

    for domain in domains:

        print(f"{domain:20}", end="")

        for other_domain in domains:
            print(
                f"{matrix[domain][other_domain]:<20.1f}",
                end=""
            )

        print()

