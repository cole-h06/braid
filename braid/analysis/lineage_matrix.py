import sys

import psycopg

DB_NAME = "braid_dev"


def load_lineage(claim_id):

    with psycopg.connect(
        dbname=DB_NAME
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    s.id,
                    s.domain,
                    l.parent_source_id
                FROM assertion_lineage l
                JOIN sources s
                    ON l.source_id = s.id
                WHERE l.claim_id = %s
                ORDER BY s.id;
                """,
                (claim_id,)
            )

            return cur.fetchall()


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


def main():

    if len(sys.argv) != 2:

        print(
            "Usage: python3 lineage_matrix.py <claim_id>"
        )

        return

    claim_id = int(
        sys.argv[1]
    )

    rows = load_lineage(
        claim_id
    )

    if not rows:

        print(
            f"No lineage metadata found for claim {claim_id}."
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