import psycopg


def get_db():
    return psycopg.connect(
        dbname="verity_dev",
        user="colehoke",
        host="localhost"
    )