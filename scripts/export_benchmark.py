import csv
import os

import psycopg


ROOT = os.path.dirname(
    os.path.dirname(__file__)
)

BENCHMARK = os.path.join(
    ROOT,
    "benchmark"
)


def export_sources(cur):

    path = os.path.join(
        BENCHMARK,
        "sources.csv"
    )

    cur.execute(
        """
        SELECT
            id,
            domain
        FROM sources
        ORDER BY id
        """
    )

    with open(
        path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "source_id",
            "name"
        ])

        writer.writerows(
            cur.fetchall()
        )


def export_claims(cur):

    path = os.path.join(
        BENCHMARK,
        "claims.csv"
    )

    cur.execute(
        """
        SELECT
            claim_id,
            product_id,
            attribute
        FROM claims
        ORDER BY claim_id
        """
    )

    with open(
        path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "claim_id",
            "product_id",
            "attribute"
        ])

        writer.writerows(
            cur.fetchall()
        )


def export_assertions(cur):

    path = os.path.join(
        BENCHMARK,
        "assertions.csv"
    )

    cur.execute(
        """
        SELECT
            source_id,
            claim_id,
            value_string,
            value_numeric,
            unit
        FROM source_claims
        ORDER BY id
        """
    )

    with open(
        path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "source_id",
            "claim_id",
            "value_string",
            "value_numeric",
            "unit"
        ])

        writer.writerows(
            cur.fetchall()
        )


def main():

    os.makedirs(
        BENCHMARK,
        exist_ok=True
    )

    with psycopg.connect(
        "dbname=braid_dev"
    ) as conn:

        with conn.cursor() as cur:

            print("Exporting sources...")
            export_sources(cur)

            print("Exporting claims...")
            export_claims(cur)

            print("Exporting assertions...")
            export_assertions(cur)

    print()
    print("Benchmark exported.")


if __name__ == "__main__":
    main()