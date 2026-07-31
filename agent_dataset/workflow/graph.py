from collections import defaultdict

from credibility.graph import CredibilityGraph


def build_graph(
    sources,
    assertions,
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

    for assertion in assertions:

        source_id = assertion.source_id

        property_key = (
            assertion.entity,
            assertion.attribute,
        )

        claim_id = (
            assertion.entity,
            assertion.attribute,
            assertion.value,
        )

        source_to_claims[source_id].add(claim_id)

        claim_to_sources[claim_id].add(source_id)

        source_to_assertions[source_id][property_key] = assertion.value

        claim_lookup[claim_id] = property_key

    return CredibilityGraph(
        source_to_claims=dict(source_to_claims),
        claim_to_sources=dict(claim_to_sources),
        source_names=source_names,
        agreement_weights=agreement_weights,
        claim_lookup=claim_lookup,
        source_to_assertions=dict(source_to_assertions),
    )
