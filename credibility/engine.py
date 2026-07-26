

# start every source with equal credibility
def initialize_uniform(source_ids):

    n = len(source_ids)

    return {
        source_id: 1.0 / n
        for source_id in source_ids
    }


# estimate how independent each supporting source is
def compute_independence(
    claim_to_sources,
    dependency_matrix,
):

    independence = {}

    for claim_id, source_ids in claim_to_sources.items():

        independence[claim_id] = {}

        for source_id in source_ids:

            dependency_sum = 0.0
            dependency_count = 0

            for other_source in source_ids:

                if source_id == other_source:
                    continue

                dependency_sum += (
                    dependency_matrix
                    .get(source_id, {})
                    .get(other_source, 0.0)
                )

                dependency_count += 1

            if dependency_count == 0:

                independence[claim_id][source_id] = 1.0

            else:

                average_dependency = (
                    dependency_sum
                    / dependency_count
                )

                independence[claim_id][source_id] = max(

                    0.0,

                    min(

                        1.0,
                        1.0 - average_dependency

                    )

                )

    return independence


# compute the number of claims asserted by each source
def compute_degrees(
    source_to_claims,
):

    return {

        source_id: len(claim_ids)

        for source_id, claim_ids
        in source_to_claims.items()

    }


# distribute source credibility across the claims it asserts
def score_claims(
    credibility,
    claim_to_sources,
    agreement_weights,
    independence,
    degrees,
):

    claim_support = {}

    for claim_id, source_ids in claim_to_sources.items():

        support = 0.0
        
        claim_independence = independence[claim_id]

        for source_id in source_ids:

            # sources with many claims split their credibility
            degree = degrees[source_id]

            if degree == 0:
                continue

            edge_weight = agreement_weights.get(
                (
                    source_id,
                    claim_id
                ),
                1.0
            )

            support += (

                credibility[source_id]
                * edge_weight
                * claim_independence[source_id]
                / degree

            )

        claim_support[claim_id] = support

    return claim_support


# claims propagate support back into their sources
def update_sources(
    claim_support,
    source_to_claims
):

    next_credibility = {}

    for source_id, claim_ids in source_to_claims.items():

        if not claim_ids:
            next_credibility[source_id] = 0.0
            continue

        support_sum = 0.0

        for claim_id in claim_ids:
            support_sum += claim_support[claim_id]

        next_credibility[source_id] = support_sum

    return next_credibility


# keep the credibility vector
# on a fixed scale
def normalize(
    credibility
):

    total = sum(
        credibility.values()
    )

    if total == 0:
        return credibility

    return {
        source_id: score / total
        for source_id, score
        in credibility.items()
    }


# repeatedly pass credibility through the graph until the scores stop changing
def run_until_convergence(
    source_to_claims,
    claim_to_sources,
    credibility,
    agreement_weights,
    dependency_matrix,
    tolerance=1e-8,
    max_iterations=1000,
):

    iteration = 0

    history = []

    independence = compute_independence(
        claim_to_sources,
        dependency_matrix,
    )

    degrees = compute_degrees(
        source_to_claims,
    )

    while iteration < max_iterations:

        previous = credibility.copy()

        # source -> claim
        claim_support = score_claims(
            credibility,
            claim_to_sources,
            agreement_weights,
            independence,
            degrees,
        )

        # claim -> source
        credibility = update_sources(
            claim_support,
            source_to_claims
        )

        credibility = normalize(
            credibility
        )

        history.append({

            "iteration": iteration + 1,

            "credibility": credibility.copy(),

            "claim_support": claim_support.copy(),

        })

        # we measure how much the credibility vector changed
        maximum_difference = 0.0

        for source_id in credibility:

            difference = abs(
                credibility[source_id]
                - previous[source_id]
            )

            if difference > maximum_difference:
                maximum_difference = difference

        # once the vector stops moving we consider it converged
        if maximum_difference < tolerance:

            return (
                credibility,
                claim_support,
                iteration + 1,
                history,
                independence,
                degrees,
            )

        iteration += 1

    return (
        credibility,
        claim_support,
        max_iterations,
        history,
        independence,
        degrees,
    )


def infer(
    graph,
    debug=False,
):

    source_ids = list(
        graph.source_to_claims.keys()
    )

    credibility = initialize_uniform(
        source_ids
    )

    (
        credibility,
        claim_support,
        iterations,
        history,
        independence,
        degrees,
    ) = run_until_convergence(
        graph.source_to_claims,
        graph.claim_to_sources,
        credibility,
        graph.agreement_weights,
        graph.dependency_matrix,
    )

    result = {
        "credibility": credibility,
        "claim_support": claim_support,
        "iterations": iterations,
    }

    if debug:
        result["history"] = history
        result["independence"] = independence
        result["degrees"] = degrees
        result["dependency_matrix"] = graph.dependency_matrix
    return result