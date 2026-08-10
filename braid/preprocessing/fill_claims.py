import psycopg
import os

conn = psycopg.connect(
    dbname="braid_dev",
    user="colehoke",
)
cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        product_id,
        canonical_attribute
    FROM source_claims
    WHERE claim_id IS NULL
""")

rows = cursor.fetchall()

found = 0
missing = 0
updated = 0

for (
    source_claim_id,
    product_id,
    canonical_attribute
) in rows:

    cursor.execute("""
        SELECT claim_id
        FROM claims
        WHERE product_id = %s
        AND attribute = %s
        LIMIT 1
    """, (
        product_id,
        canonical_attribute
    ))

    result = cursor.fetchone()

    if result:

        claim_id = result[0]

        cursor.execute("""
            UPDATE source_claims
            SET claim_id = %s
            WHERE id = %s
        """, (
            claim_id,
            source_claim_id
        ))

        print(
            "FOUND:",
            source_claim_id,
            "-> claim",
            claim_id
        )

        found += 1
        updated += 1

    else:

        cursor.execute("""
            INSERT INTO claims (
                product_id,
                attribute
            )
            VALUES (%s, %s)
            RETURNING claim_id
            """, (
                product_id,
                canonical_attribute
            ))

        claim_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE source_claims
            SET claim_id = %s
            WHERE id = %s
        """, (
            claim_id,
            source_claim_id
        ))

        print(
            "CREATED:",
            source_claim_id,
            "-> claim",
            claim_id
        )

        missing += 1
        updated += 1

conn.commit()

print()
print("updated:", updated)
print("found:", found)
print("missing:", missing)

cursor.execute("""
    SELECT COUNT(*)
    FROM source_claims
    WHERE claim_id IS NULL
""")

remaining = cursor.fetchone()[0]

print("remaining nulls:", remaining)

conn.close()

print("done.")