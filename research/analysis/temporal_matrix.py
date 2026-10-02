"""Historical research diagnostic; not a normative BRAID estimator."""

WINDOW_HOURS = 24 * 7


def temporal_score(time_a, time_b):

    difference = abs(
        time_a - time_b
    )

    hours = (
        difference.total_seconds()
        / 3600.0
    )

    score = max(
        0.0,
        1.0 - (hours / WINDOW_HOURS)
    )

    return score



def build_matrix(rows):

    matrix = {}

    for _, domain, published_at in rows:

        matrix[domain] = {}

        for _, other_domain, other_published_at in rows:

            matrix[domain][other_domain] = temporal_score(
                published_at,
                other_published_at
            )

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
                f"{matrix[domain][other_domain]:<20.3f}",
                end=""
            )

        print()

