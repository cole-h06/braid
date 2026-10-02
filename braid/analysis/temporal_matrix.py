import sys
from datetime import datetime

import psycopg

DB_NAME = "braid_dev"

WINDOW_HOURS = 24 * 7


def load_temporal(claim_id):

    with psycopg.connect(
        dbname=DB_NAME
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    s.id,
                    s.domain,
                    t.published_at
                FROM assertion_temporal t
                JOIN sources s
                    ON t.source_id = s.id
                WHERE t.claim_id = %s
                ORDER BY s.id;
                """,
                (claim_id,)
            )

            return cur.fetchall()


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


def main():

    if len(sys.argv) != 2:

        print(
            "Usage: python3 temporal_matrix.py <claim_id>"
        )

        return

    claim_id = int(
        sys.argv[1]
    )

    rows = load_temporal(
        claim_id
    )

    if not rows:

        print(
            f"No temporal metadata found for claim {claim_id}."
        )

        return

    matrix = build_matrix(
        rows
    )

    print_matrix(
        matrix
    )


if __name__ == "__main__":
    main()