from .agents.api import api_agent
from .agents.documents import document_agent
from .agents.research import research_agent
from .agents.search import search_agent
from .agents.sql import sql_agent
from .extraction.schema import SourceMetadata


SOURCES = (
    SourceMetadata(
        source_id="research_agent",
        display_name="Research Agent",
        owner_id="research_lab",
    ),
    SourceMetadata(
        source_id="search_agent",
        display_name="Search Agent",
        owner_id="search_vendor",
    ),
    SourceMetadata(
        source_id="sql_agent",
        display_name="SQL Agent",
        owner_id="commerce_platform",
    ),
    SourceMetadata(
        source_id="document_agent",
        display_name="Document Agent",
        owner_id="document_vendor",
    ),
    SourceMetadata(
        source_id="api_agent",
        display_name="API Agent",
        owner_id="commerce_platform",
    ),
)


BASELINE_WEIGHTS = {
    "provenance": 0.25,
    "lineage": 0.30,
    "ownership": 0.15,
    "temporal": 0.15,
    "graph": 0.15,
}


SIMULATED_RELATIONSHIPS = {
    ("research_agent", "search_agent"): "lineage",
    ("search_agent", "document_agent"): "provenance",
    ("sql_agent", "api_agent"): "ownership",
    ("research_agent", "sql_agent"): "temporal",
    ("research_agent", "api_agent"): "independent conflict",
}


AGENTS = (
    research_agent,
    search_agent,
    sql_agent,
    document_agent,
    api_agent,
)


def load_dataset():

    assertions = []
    evidence = []

    for agent in AGENTS:

        result = agent()

        assertions.extend(result.assertions)
        evidence.extend(result.evidence)

    validate_dataset(
        SOURCES,
        assertions,
        evidence,
    )

    return SOURCES, assertions, evidence


def validate_dataset(
    sources,
    assertions,
    evidence,
):

    source_ids = [
        source.source_id
        for source in sources
    ]

    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source IDs must be unique")

    assertion_ids = [
        assertion.assertion_id
        for assertion in assertions
    ]

    if len(assertion_ids) != len(set(assertion_ids)):
        raise ValueError("assertion IDs must be unique")

    known_sources = set(source_ids)
    known_assertions = set(assertion_ids)

    property_values = set()

    for assertion in assertions:

        if assertion.source_id not in known_sources:
            raise ValueError("assertion references unknown source")

        source_property = (
            assertion.source_id,
            assertion.entity,
            assertion.attribute,
        )

        if source_property in property_values:
            raise ValueError("source has multiple values for one property")

        property_values.add(source_property)

    evidence_counts = {
        assertion_id: 0
        for assertion_id in assertion_ids
    }

    for item in evidence:

        if item.assertion_id not in known_assertions:
            raise ValueError("evidence references unknown assertion")

        evidence_counts[item.assertion_id] += 1

        if (
            item.observed_at.tzinfo is None
            or item.observed_at.utcoffset() is None
        ):
            raise ValueError("evidence timestamps must be timezone-aware")

        if not set(item.cited_source_ids) <= known_sources:
            raise ValueError("evidence cites unknown source")

        if not set(item.parent_assertion_ids) <= known_assertions:
            raise ValueError("evidence references unknown parent assertion")

    if any(count != 1 for count in evidence_counts.values()):
        raise ValueError("every assertion must have exactly one evidence record")
