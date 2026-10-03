from dataclasses import dataclass, field
from math import isfinite


@dataclass
class BipartiteGraph:

    source_to_claims: dict
    claim_to_sources: dict
    source_names: dict
    agreement_weights: dict
    claim_lookup: dict = field(default_factory=dict)
    source_to_assertions: dict = field(default_factory=dict)

    dependency_matrix: dict = field(default_factory=dict)
    confidence_matrix: dict = field(default_factory=dict)


def complete_matrix(source_ids, matrix):
    if not matrix:
        return {
            source: {other: 0.0 for other in source_ids}
            for source in source_ids
        }
    if set(matrix) != set(source_ids):
        raise ValueError("pair matrix must contain exactly the graph sources")
    if any(set(matrix[source]) != set(source_ids) for source in source_ids):
        raise ValueError("pair matrix must be complete")
    result = {}
    for source in source_ids:
        if set(matrix[source]) != set(source_ids):
            raise ValueError("pair matrix must be complete")
        result[source] = {}
        for other in source_ids:
            value = matrix[source][other]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or not 0.0 <= value <= 1.0
            ):
                raise ValueError("pair values must be finite and in [0, 1]")
            if source == other and value != 0.0:
                raise ValueError("pair diagonal must be zero")
            if value != matrix[other][source]:
                raise ValueError("pair matrix must be symmetric")
            result[source][other] = float(value)
    return result


def prepare_graph(graph):
    source_claims = graph.source_to_claims
    claim_sources = graph.claim_to_sources
    lookup = getattr(graph, "claim_lookup", {})
    if not source_claims or not claim_sources:
        raise ValueError("assertion graph must not be empty")
    if set(lookup) != set(claim_sources):
        raise ValueError("every claim requires an explicit attribute identity")
    edges = set()
    for source, claims in source_claims.items():
        if not claims or len(claims) != len(set(claims)):
            raise ValueError("empty source or duplicate assertion")
        attributes = set()
        for claim in claims:
            if claim not in lookup:
                raise ValueError("assertion references unknown claim")
            attribute = lookup[claim]
            if attribute in attributes:
                raise ValueError("source has multiple claims for an attribute")
            attributes.add(attribute)
            edges.add((source, claim))
    reverse_edges = set()
    for claim, sources in claim_sources.items():
        if not sources or len(sources) != len(set(sources)):
            raise ValueError("empty claim or duplicate assertion")
        reverse_edges.update((source, claim) for source in sources)
    if edges != reverse_edges:
        raise ValueError("source and claim adjacency maps disagree")
    source_ids = sorted(source_claims)
    claim_ids = sorted(claim_sources)
    attribute_sources = {}
    for claim in claim_ids:
        attribute_sources.setdefault(lookup[claim], set()).update(claim_sources[claim])
    agreement = {
        (source, claim): len(claim_sources[claim]) / len(attribute_sources[lookup[claim]])
        for source in source_ids
        for claim in sorted(source_claims[source])
    }
    return BipartiteGraph(
        source_to_claims={source: tuple(sorted(source_claims[source])) for source in source_ids},
        claim_to_sources={claim: tuple(sorted(claim_sources[claim])) for claim in claim_ids},
        source_names=dict(getattr(graph, "source_names", {})),
        agreement_weights=agreement,
        claim_lookup={claim: lookup[claim] for claim in claim_ids},
        source_to_assertions=dict(getattr(graph, "source_to_assertions", {})),
        dependency_matrix=complete_matrix(source_ids, graph.dependency_matrix),
        confidence_matrix=complete_matrix(source_ids, getattr(graph, "confidence_matrix", {})),
    )


def from_assertions(assertions, dependency_matrix=None, confidence_matrix=None):
    source_claims = {}
    claim_sources = {}
    lookup = {}
    for source, attribute, claim in assertions:
        if claim in lookup and lookup[claim] != attribute:
            raise ValueError("claim belongs to multiple attributes")
        lookup[claim] = attribute
        source_claims.setdefault(source, []).append(claim)
        claim_sources.setdefault(claim, []).append(source)
    return prepare_graph(BipartiteGraph(
        source_to_claims=source_claims,
        claim_to_sources=claim_sources,
        source_names={},
        agreement_weights={},
        claim_lookup=lookup,
        dependency_matrix=dependency_matrix or {},
        confidence_matrix=confidence_matrix or {},
    ))
