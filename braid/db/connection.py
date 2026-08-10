import psycopg


def get_db():
    return psycopg.connect(
        dbname="braid_dev",
        user="colehoke",
        host="localhost"
    )