from collections import defaultdict

# give rare assertions more weight
def build_rarity(
    assertion_to_sources
):

    rarity = {}

    for assertion, sources in assertion_to_sources.items():

        rarity[assertion] = (
            1.0
            /
            len(sources)
        )

    return rarity


# compare one source pair
def score_pair(
    a_assertions,
    b_assertions,
    rarity
):

    matches = []
    disagreements = 0

    shared_keys = (
        a_assertions.keys()
        &
        b_assertions.keys()
    )

    for key in shared_keys:

        a_value = a_assertions[
            key
        ]

        b_value = b_assertions[
            key
        ]

        if a_value == b_value:

            matches.append(
                (
                    key,
                    a_value
                )
            )

        else:

            disagreements += 1

    match_count = len(
        matches
    )

    if match_count == 0:

        return None

    a_size = len(
        a_assertions
    )

    b_size = len(
        b_assertions
    )

    if a_size == 0 or b_size == 0:
        return None

# measure how fully either source is contained in the other
    inclusion_ab = (
        match_count
        /
        b_size
    )

    inclusion_ba = (
        match_count
        /
        a_size
    )

    inclusion = max(
        inclusion_ab,
        inclusion_ba
    )

# average how rare the matching assertions are
    rarity_score = (
        sum(
            rarity[assertion]
            for assertion in matches
        )
        /
        match_count
    )

# overlap is redundant when inclusion and rarity are both high
    redundancy = (
        inclusion
        *
        rarity_score
    )

    independence = (
        1.0
        -
        redundancy
    )

    shared = (
        match_count
        +
        disagreements
    )

    agreement = (
        match_count
        /
        shared
    )

    return (
        independence,
        redundancy,
        inclusion,
        rarity_score,
        inclusion_ab,
        inclusion_ba,
        agreement,
        match_count,
        disagreements,
        a_size,
        b_size
    )


# score every source pair
def find_pairs(
    source_to_assertions,
    rarity
):

    source_ids = list(
        source_to_assertions.keys()
    )

    rows = []

    pairwise_independence = {}

    for i, source_a in enumerate(
        source_ids
    ):

        for source_b in source_ids[i + 1:]:

            result = score_pair(
                source_to_assertions[source_a],
                source_to_assertions[source_b],
                rarity
            )

            if result is None:
                continue

            (
                independence,
                redundancy,
                inclusion,
                rarity_score,
                inclusion_ab,
                inclusion_ba,
                agreement,
                matches,
                disagreements,
                a_size,
                b_size
            ) = result

            pairwise_independence[
                (source_a, source_b)
            ] = independence

            pairwise_independence[
                (source_b, source_a)
            ] = independence

            rows.append(
                (
                    redundancy,
                    independence,
                    inclusion,
                    rarity_score,
                    agreement,
                    matches,
                    disagreements,
                    source_a,
                    source_b,
                    a_size,
                    b_size,
                    inclusion_ab,
                    inclusion_ba
                )
            )

    rows.sort(
        reverse=True
    )

    return (rows, pairwise_independence)


def build_pairwise_rows(graph):

    assertion_to_sources = defaultdict(set)

    source_to_assertions = defaultdict(dict)

    for (
        source_id,
        assertions
    ) in graph.source_to_assertions.items():

        for (
            claim_id,
            value
        ) in assertions.items():

            property_key = (
                graph.claim_lookup.get(
                    claim_id,
                    claim_id,
                )
            )

            assertion = (
                property_key,
                value,
            )

            source_to_assertions[
                source_id
            ][property_key] = value

            assertion_to_sources[
                assertion
            ].add(
                source_id
            )

    rarity = build_rarity(
        assertion_to_sources
    )

    return find_pairs(
        source_to_assertions,
        rarity
    )


def build_pairwise_independence(graph):

    _, pairwise_independence = (
        build_pairwise_rows(graph)
    )

    return pairwise_independence
