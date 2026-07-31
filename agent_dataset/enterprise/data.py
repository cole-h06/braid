import json

from datetime import datetime
from pathlib import Path

from agent_dataset.extraction.schema import SourceMetadata


FIXTURES = Path(__file__).parent / "fixtures"

ORDER = (
    "handbook",
    "faq",
    "sql",
    "vendor",
    "research",
)


def load_manifest():

    path = FIXTURES / "manifest.json"

    return json.loads(path.read_text())


def load_sources():

    manifest = load_manifest()

    return tuple(
        SourceMetadata(**item)
        for item in manifest["sources"]
    )


def controlled_clock():

    value = load_manifest()["retrieved_at"]

    return datetime.fromisoformat(value)


SOURCES = load_sources()
