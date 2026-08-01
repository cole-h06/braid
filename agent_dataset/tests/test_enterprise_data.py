import json

from datetime import datetime, timezone
from pathlib import Path

from agent_dataset.dataset import validate_dataset
from agent_dataset.enterprise.data import FIXTURES, ORDER
from agent_dataset.enterprise.workflow import run_enterprise
from agent_dataset.workflow.hybrid_dependency import claim_telemetry


def test_counts():

    result = run_enterprise()

    assert len(result["sources"]) == 5
    assert len(result["assertions"]) == 15
    assert len(result["evidence"]) == 15
    assert all(
        len(item.retrievals) == 1
        for item in result["evidence"]
    )

    validate_dataset(
        result["sources"],
        result["assertions"],
        result["evidence"],
    )


def test_order():

    result = run_enterprise()

    assert tuple(
        source.source_id
        for source in result["sources"]
    ) == ORDER

    assert tuple(
        assertion.source_id
        for assertion in result["assertions"][::3]
    ) == ORDER


def test_lineage():

    result = run_enterprise()
    research = result["evidence"][-3:]

    assert [item.cited_source_ids for item in research] == [
        ("handbook",),
        ("handbook",),
        ("vendor",),
    ]
    assert [item.parent_assertion_ids for item in research] == [
        ("handbook-001",),
        ("handbook-002",),
        ("vendor-003",),
    ]


def test_times():

    first = run_enterprise()
    later = datetime(2026, 8, 1, tzinfo=timezone.utc)
    second = run_enterprise(clock=lambda: later)

    assert [
        item.observed_at
        for item in first["evidence"]
    ] == [
        item.observed_at
        for item in second["evidence"]
    ]
    assert first["hybrid"] == second["hybrid"]
    assert claim_telemetry(
        first["graph"],
        first["hybrid"],
        0.15,
    ) == claim_telemetry(
        second["graph"],
        second["hybrid"],
        0.15,
    )
    assert all(
        retrieval.retrieved_at == later
        for item in second["evidence"]
        for retrieval in item.retrievals
    )


def test_labels():

    result = run_enterprise()
    content = repr(result)
    relationships = json.loads(
        (FIXTURES / "relationships.json").read_text()
    )

    assert set(relationships.values()).isdisjoint({
        assertion.value
        for assertion in result["assertions"]
    })
    assert "SQL seeded from handbook" not in content
    assert not hasattr(result["graph"], "evidence")
    assert not hasattr(result["graph"], "retrievals")


def test_label_isolation(monkeypatch):

    read_text = Path.read_text

    def guarded_read(path, *args, **kwargs):

        if path.name == "relationships.json":
            raise AssertionError("workflow read simulated relationships")

        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)

    result = run_enterprise()

    assert len(result["assertions"]) == 15


def test_owners():

    result = run_enterprise()

    assert {
        source.source_id: source.owner_id
        for source in result["sources"]
    } == {
        "handbook": "northstar_policy",
        "faq": "northstar_policy",
        "sql": "northstar_ops",
        "vendor": "returns_vendor",
        "research": "northstar_research",
    }
