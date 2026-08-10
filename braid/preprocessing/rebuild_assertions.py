from db import get_db

conn = get_db()
cursor = conn.cursor()

print("clearing assertions...")
cursor.execute("DELETE FROM assertions")
conn.commit()

print("building assertions...")

cursor.execute("""
    INSERT OR IGNORE INTO assertions (
        source_id,
        claim_id
    )
    SELECT
        source_id,
        claim_id
    FROM source_claims
    WHERE claim_id IS NOT NULL
""")

conn.commit()

actual = cursor.execute("""
    SELECT COUNT(*)
    FROM assertions
""").fetchone()[0]

missing = cursor.execute("""
    SELECT COUNT(*)
    FROM source_claims
    WHERE claim_id IS NULL
""").fetchone()[0]

print()
print("assertions:", actual)
print("missing claim_id:", missing)

conn.close()
print("done.")