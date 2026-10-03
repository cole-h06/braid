"""Historical research diagnostic; not used by the current BRAID estimator."""


def rarity_scores(
    claim_to_sources
):

    scores = {}

    for claim, sources in claim_to_sources.items():

        scores[claim] = (
            1 / len(sources)
        )

    return scores



def find_pairs(
    source_to_claims,
    rarity
):

    source_ids = list(
        source_to_claims.keys()
    )

    rows = []

    for i, source_a in enumerate(
        source_ids
    ):

        for source_b in source_ids[i + 1:]:

            shared = (
                source_to_claims[source_a]
                &
                source_to_claims[source_b]
            )

            if not shared:
                continue

            score = (
                sum(
                    rarity[claim]
                    for claim in shared
                )
                /
                len(shared)
            )

            rows.append(
                (
                    score,
                    len(shared),
                    source_a,
                    source_b
                )
            )

    rows.sort(
        reverse=True
    )

    return rows



def print_pairs(
    rows,
    source_names,
    n=30
):

    print()
    print("top rarity overlap pairs")
    print("------------------------")

    print(
        f"{'source_a':<25}"
        f"{'source_b':<25}"
        f"{'shared':>8}"
        f"{'rarity':>12}"
    )

    for (
        score,
        shared,
        source_a,
        source_b
    ) in rows[:n]:

        print(
            f"{source_names[source_a]:<25}"
            f"{source_names[source_b]:<25}"
            f"{shared:>8}"
            f"{score:>12.3f}"
        )

