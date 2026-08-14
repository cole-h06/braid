from datetime import datetime, timezone

import pytest

from agent_dataset.enterprise.agents import (
    faq_agent,
    handbook_agent,
    sql_agent,
    vendor_agent,
)
from agent_dataset.enterprise import retrieve
from agent_dataset.enterprise.data import FIXTURES, load_manifest
from agent_dataset.enterprise.retrieve import (
    RetrievalError,
    api_snapshot,
    document,
    file_hash,
    sql_records,
)
from agent_dataset.extraction.schema import Retrieval


NOW = datetime(2026, 7, 1, tzinfo=timezone.utc)


def test_documents():

    records = document("handbook", NOW)

    assert [item["value"] for item in records] == [
        "30 days",
        "2 years",
        "customer pays",
    ]

    assert records[0]["observed_at"] == NOW
    assert records[0]["source_modified_at"] == datetime(
        2026,
        2,
        2,
        9,
        tzinfo=timezone.utc,
    )
    assert records[0]["upstream_source_ids"] == ()

    assert records[0]["fields"]["document_id"] == "returns_handbook"
    assert records[0]["fields"]["chunk_id"] == (
        "returns_handbook#return_window"
    )
    assert records[0]["fields"]["path"] == "fixtures/docs/handbook.md"
    assert len(records[0]["fields"]["sha256"]) == 64


def test_sql():

    records = sql_records(NOW)

    assert [item["fields"]["record_id"] for item in records] == [
        "policy-001",
        "policy-002",
        "policy-003",
    ]

    assert records[0]["observed_at"] == NOW
    assert records[0]["source_modified_at"] == datetime(
        2026,
        2,
        2,
        9,
        30,
        tzinfo=timezone.utc,
    )
    assert records[0]["upstream_source_ids"] == ("handbook",)

    assert records[0]["fields"]["database_id"] == (
        "northstar_policy_config"
    )
    assert records[0]["fields"]["table"] == "policy_config"
    assert records[0]["fields"]["query_id"] == (
        "returns_policy_by_record"
    )


def test_api():

    records = api_snapshot(NOW)

    assert [item["value"] for item in records] == [
        "14 days",
        "1 year",
        "USD 5",
    ]

    assert records[0]["observed_at"] == NOW
    assert records[0]["source_modified_at"] == datetime(
        2026,
        2,
        5,
        12,
        tzinfo=timezone.utc,
    )
    assert records[0]["upstream_source_ids"] == ()

    assert records[0]["fields"]["endpoint"] == (
        "https://returns.vendor.example/v1/policy"
    )
    assert records[0]["fields"]["response_id"] == (
        "vendor-policy-response-004"
    )
    assert records[0]["fields"]["snapshot_path"] == (
        "fixtures/vendor.json"
    )


def test_agents():

    results = (
        handbook_agent(NOW),
        faq_agent(NOW),
        sql_agent(NOW),
        vendor_agent(NOW),
    )

    assert all(
        len(result.assertions) == 3
        for result in results
    )

    assert all(
        len(result.evidence) == 3
        for result in results
    )

    assert all(
        item.retrievals[0].retrieved_at == NOW
        for result in results
        for item in result.evidence
    )

    assert all(
        item.observed_at == NOW
        for result in results
        for item in result.evidence
    )

    assert all(
        item.source_modified_at is not None
        for result in results
        for item in result.evidence
    )


def test_timestamp():

    with pytest.raises(ValueError):
        Retrieval(
            retrieval_id="bad-time",
            kind="api",
            resource_id="vendor-response",
            retrieved_at=datetime(2026, 7, 1),
        )


def test_missing(tmp_path, monkeypatch):

    monkeypatch.setattr(retrieve, "FIXTURES", tmp_path)

    with pytest.raises(RetrievalError) as caught:
        document("handbook", NOW)

    assert caught.value.source_id == "handbook"
    assert caught.value.resource_id == "docs/handbook.md"
    assert isinstance(caught.value.__cause__, FileNotFoundError)


def test_malformed(tmp_path, monkeypatch):

    path = tmp_path / "company.sql"
    path.write_text("not valid SQL")

    manifest = {
        "database_id": "bad-database",
        "query_id": "bad-query",
        "snapshots": {
            "company.sql": file_hash(path.read_bytes()),
        },
    }

    monkeypatch.setattr(retrieve, "FIXTURES", tmp_path)
    monkeypatch.setattr(retrieve, "load_manifest", lambda: manifest)

    with pytest.raises(RetrievalError) as caught:
        sql_records(NOW)

    assert caught.value.source_id == "sql"
    assert caught.value.resource_id == "company.sql"
    assert caught.value.__cause__ is not None


def test_hash(tmp_path, monkeypatch):

    path = tmp_path / "vendor.json"
    path.write_text("{}")

    manifest = {
        "snapshots": {
            "vendor.json": "0" * 64,
        },
    }

    monkeypatch.setattr(retrieve, "FIXTURES", tmp_path)
    monkeypatch.setattr(retrieve, "load_manifest", lambda: manifest)

    with pytest.raises(RetrievalError) as caught:
        api_snapshot(NOW)

    assert caught.value.source_id == "vendor"
    assert caught.value.resource_id == "vendor.json"

    assert str(caught.value.__cause__) == (
        "snapshot hash mismatch: vendor.json"
    )


def test_stale_hashes():

    snapshots = load_manifest()["snapshots"]

    assert snapshots == {
        name: file_hash((FIXTURES / name).read_bytes())
        for name in snapshots
    }