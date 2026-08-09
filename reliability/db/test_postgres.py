import psycopg


conn = psycopg.connect(
    dbname="verity_dev",
    user="colehoke",
    host="localhost"
)

print("Connected!")

conn.close()