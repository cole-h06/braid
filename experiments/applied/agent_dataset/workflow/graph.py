from collections import defaultdict

from braid.graph import BipartiteGraph, prepare_graph


def build_graph(
    sources,
    observations,
):

    source_to_claims = defaultdict(set)

    claim_to_sources = defaultdict(set)

    source_to_assertions = defaultdict(dict)

    source_names = {
        source.source_id: source.display_name
        for source in sources
    }

    claim_lookup = {}

    agreement_weights = {}
    seen = set()

    for observation in observations:

        source_id = observation.source_id

        property_key = (
            observation.entity,
            observation.attribute,
        )

        claim_id = (
            observation.entity,
            observation.attribute,
            observation.value,
        )
        if (source_id, property_key) in seen:
            raise ValueError("source has multiple claims for an attribute")
        seen.add((source_id, property_key))

        source_to_claims[source_id].add(claim_id)

        claim_to_sources[claim_id].add(source_id)

        source_to_assertions[source_id][property_key] = observation.value

        claim_lookup[claim_id] = property_key

    return prepare_graph(BipartiteGraph(
        source_to_claims=dict(source_to_claims),
        claim_to_sources=dict(claim_to_sources),
        source_names=source_names,
        agreement_weights=agreement_weights,
        claim_lookup=claim_lookup,
        source_to_assertions=dict(source_to_assertions),
    ))
