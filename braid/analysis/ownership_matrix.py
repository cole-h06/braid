import sys
import psycopg

DB_NAME = "braid_dev"


def load_ownership(claim_id):

    with psycopg.connect(
        dbname=DB_NAME
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    s.id,
                    s.domain,
                    o.owner_id
                FROM assertion_ownership o
                JOIN sources s
                    ON o.source_id = s.id
                WHERE o.claim_id = %s
                ORDER BY s.id;
                """,
                (claim_id,)
            )

            return cur.fetchall()


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


def main():

    if len(sys.argv) != 2:

        print(
            "Usage: python3 ownership_matrix.py <claim_id>"
        )

        return

    claim_id = int(sys.argv[1])

    rows = load_ownership(
        claim_id
    )

    if not rows:

        print(
            f"No ownership metadata found for claim {claim_id}."
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