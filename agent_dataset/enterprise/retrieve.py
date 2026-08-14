import hashlib
import json
import sqlite3

from datetime import datetime

from .data import FIXTURES, load_manifest


class RetrievalError(ValueError):

    def __init__(
        self,
        source_id,
        resource_id,
    ):

        self.source_id = source_id
        self.resource_id = resource_id

        super().__init__(
            f"{source_id} retrieval failed: {resource_id}"
        )


def file_hash(content):

    return hashlib.sha256(content).hexdigest()


def _read_snapshot(path):

    content = path.read_bytes()
    relative_path = str(path.relative_to(FIXTURES))
    expected = load_manifest()["snapshots"][relative_path]

    if file_hash(content) != expected:
        raise ValueError(f"snapshot hash mismatch: {relative_path}")

    return content


def document(name, retrieved_at):

    resource_id = f"docs/{name}.md"

    try:
        return _load_document(
            name,
            retrieved_at,
        )
    except (
        KeyError,
        OSError,
        UnicodeError,
        ValueError,
    ) as error:
        raise RetrievalError(
            name,
            resource_id,
        ) from error


def _load_document(name, retrieved_at):

    path = FIXTURES / "docs" / f"{name}.md"
    content = _read_snapshot(path)
    text = content.decode()
    header, *sections = text.strip().split("\n\n")

    metadata = dict(
        line.split(": ", 1)
        for line in header.splitlines()
    )

    source_modified_at = datetime.fromisoformat(
        metadata["source_modified_at"]
    )

    upstream_source_ids = tuple(
        source_id
        for source_id in metadata.get(
            "upstream_source_ids",
            "",
        ).split(",")
        if source_id
    )

    records = []

    for section in sections:

        heading, value = section.split("\n", 1)
        attribute = heading.removeprefix("## ")
        chunk = section.encode()

        records.append({
            "attribute": attribute,
            "value": value.strip(),
            "observed_at": retrieved_at,
            "source_modified_at": source_modified_at,
            "upstream_source_ids": upstream_source_ids,
            "retrieved_at": retrieved_at,
            "resource_id": metadata["document_id"],
            "fields": {
                "document_id": metadata["document_id"],
                "chunk_id": f'{metadata["document_id"]}#{attribute}',
                "path": str(path.relative_to(FIXTURES.parent)),
                "sha256": file_hash(chunk),
                "document_sha256": file_hash(content),
                "policy_release_id": metadata["policy_release_id"],
            },
        })

    return records


def sql_records(retrieved_at):

    try:
        return _load_sql(retrieved_at)
    except (
        KeyError,
        OSError,
        UnicodeError,
        ValueError,
        sqlite3.Error,
    ) as error:
        raise RetrievalError(
            "sql",
            "company.sql",
        ) from error


def _load_sql(retrieved_at):

    manifest = load_manifest()
    path = FIXTURES / "company.sql"
    script = _read_snapshot(path).decode()

    query = (
        "SELECT record_id, attribute, value, "
        "source_modified_at, upstream_source_id "
        "FROM policy_config ORDER BY record_id"
    )

    connection = sqlite3.connect(":memory:")

    try:
        connection.executescript(script)
        rows = connection.execute(query).fetchall()
    finally:
        connection.close()

    return [
        {
            "attribute": attribute,
            "value": value,
            "observed_at": retrieved_at,
            "source_modified_at": datetime.fromisoformat(
                source_modified_at
            ),
            "upstream_source_ids": (
                (upstream_source_id,)
                if upstream_source_id is not None
                else ()
            ),
            "retrieved_at": retrieved_at,
            "resource_id": manifest["database_id"],
            "fields": {
                "database_id": manifest["database_id"],
                "table": "policy_config",
                "query_id": manifest["query_id"],
                "query_sha256": file_hash(query.encode()),
                "record_id": record_id,
            },
        }
        for (
            record_id,
            attribute,
            value,
            source_modified_at,
            upstream_source_id,
        ) in rows
    ]


def api_snapshot(retrieved_at):

    try:
        return _load_api(retrieved_at)
    except (
        KeyError,
        OSError,
        UnicodeError,
        ValueError,
    ) as error:
        raise RetrievalError(
            "vendor",
            "vendor.json",
        ) from error


def _load_api(retrieved_at):

    path = FIXTURES / "vendor.json"
    content = _read_snapshot(path)
    response = json.loads(content)

    source_modified_at = datetime.fromisoformat(
        response["source_modified_at"]
    )

    upstream_source_ids = tuple(
        response.get("upstream_source_ids", ())
    )

    return [
        {
            "attribute": item["attribute"],
            "value": item["value"],
            "observed_at": retrieved_at,
            "source_modified_at": source_modified_at,
            "upstream_source_ids": upstream_source_ids,
            "retrieved_at": retrieved_at,
            "resource_id": response["response_id"],
            "fields": {
                "endpoint": response["endpoint"],
                "response_id": response["response_id"],
                "snapshot_path": str(path.relative_to(FIXTURES.parent)),
                "sha256": file_hash(content),
                "record_id": item["record_id"],
            },
        }
        for item in response["facts"]
    ]