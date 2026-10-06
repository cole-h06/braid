from math import isfinite
from .graph import prepare_graph


ALGORITHM_VERSION = "braid-1.1.0"
CONVERGENCE_TOLERANCE = 1e-8
MAX_ITERATIONS = 1000
PROPAGATION_WEIGHT = 0.70

class InferenceError(RuntimeError):
    pass


def finite(value):
    if not isfinite(value):
        raise InferenceError("inference produced a nonfinite value")
    return value


# start every source with equal reliability
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

                independence[claim_id][source_id] = (
                    1.0 / (1.0 + dependency_sum)
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


# distribute source reliability across the claims it asserts
def score_claims(
    reliability_vector,
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

            # sources with many claims split their reliability
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

                reliability_vector[source_id]
                * edge_weight
                * claim_independence[source_id]
                / degree

            )

        claim_support[claim_id] = finite(support)

    return claim_support


# claims propagate support back into their sources
def update_sources(
    claim_support,
    source_to_claims,
    claim_lookup,
):

    next_reliability_vector = {}
    attribute_claims = {}
    for claim_id in claim_support:
        attribute_claims.setdefault(claim_lookup[claim_id], []).append(claim_id)

    for source_id, claim_ids in source_to_claims.items():

        if not claim_ids:
            next_reliability_vector[source_id] = 0.0
            continue

        support_sum = 0.0

        for attribute in sorted(attribute_claims):
            attribute_total = sum(
                claim_support[claim_id]
                for claim_id in sorted(attribute_claims[attribute])
            )
            if attribute_total == 0.0:
                continue
            for claim_id in claim_ids:
                if claim_lookup[claim_id] == attribute:
                    support_sum += claim_support[claim_id] / attribute_total

        next_reliability_vector[source_id] = finite(support_sum)

    return next_reliability_vector


# keep the reliability vector
# on a fixed scale
def normalize(
    reliability_vector
):

    total = finite(sum(
        reliability_vector.values()
    ))

    if total == 0:
        raise InferenceError("inference propagation total is zero")

    return {
        source_id: finite(score / total)
        for source_id, score
        in reliability_vector.items()
    }

def apply_prior(
    reliability_vector,
    prior,
    propagation_weight=PROPAGATION_WEIGHT,
):
    prior_weight = 1.0 - propagation_weight

    return {
        source_id: finite(
            propagation_weight * reliability_vector[source_id]
            + prior_weight * prior[source_id]
        )
        for source_id in reliability_vector
    }


# repeatedly pass reliability through the graph until the scores stop changing
def run_until_convergence(
    source_to_claims,
    claim_to_sources,
    reliability_vector,
    agreement_weights,
    dependency_matrix,
    tolerance=CONVERGENCE_TOLERANCE,
    max_iterations=MAX_ITERATIONS,
    propagation_weight=PROPAGATION_WEIGHT,
    *,
    claim_lookup,
):

    iteration = 0

    history = []

    prior = normalize(reliability_vector.copy())

    independence = compute_independence(
        claim_to_sources,
        dependency_matrix,
    )

    degrees = compute_degrees(
        source_to_claims,
    )

    while iteration < max_iterations:

        previous = reliability_vector.copy()

        # source -> claim
        claim_support = score_claims(
            reliability_vector,
            claim_to_sources,
            agreement_weights,
            independence,
            degrees,
        )

        # claim -> source
        reliability_vector = update_sources(
            claim_support,
            source_to_claims,
            claim_lookup,
        )

        reliability_vector = normalize(
            reliability_vector
        )

        reliability_vector = apply_prior(
            reliability_vector,
            prior,
            propagation_weight,
        )

        history.append({

            "iteration": iteration + 1,

            "reliability": reliability_vector.copy(),

            "claim_support": claim_support.copy(),

        })

        # we measure how much the reliability vector changed
        maximum_difference = 0.0

        for source_id in reliability_vector:

            difference = abs(
                reliability_vector[source_id]
                - previous[source_id]
            )

            if difference > maximum_difference:
                maximum_difference = difference

        # once the vector stops moving we consider it converged
        if maximum_difference < tolerance:

            claim_support = score_claims(
                reliability_vector,
                claim_to_sources,
                agreement_weights,
                independence,
                degrees,
            )
            return (
                reliability_vector,
                claim_support,
                iteration + 1,
                history,
                independence,
                degrees,
            )

        iteration += 1

    raise InferenceError("inference did not converge")


def evaluate(
    graph,
    debug=False,
    propagation_weight=PROPAGATION_WEIGHT,
):

    graph = prepare_graph(graph)
    source_ids = list(
        graph.source_to_claims.keys()
    )

    reliability_vector = initialize_uniform(
        source_ids
    )

    (
        reliability_vector,
        claim_support,
        iterations,
        history,
        independence,
        degrees,
    ) = run_until_convergence(
        graph.source_to_claims,
        graph.claim_to_sources,
        reliability_vector,
        graph.agreement_weights,
        graph.dependency_matrix,
        propagation_weight=propagation_weight,
        claim_lookup=graph.claim_lookup,
    )

    previous = (
        history[-2]["reliability"]
        if len(history) > 1
        else initialize_uniform(source_ids)
    )
    contributions = {
        claim: {
            source: finite(
                reliability_vector[source]
                * graph.agreement_weights[source, claim]
                * independence[claim][source]
                / degrees[source]
            )
            for source in sources
        }
        for claim, sources in graph.claim_to_sources.items()
    }
    attribute_maxima = {}
    for claim, support in claim_support.items():
        attribute = graph.claim_lookup[claim]
        attribute_maxima[attribute] = max(attribute_maxima.get(attribute, 0.0), support)
    result = {
        "reliability": reliability_vector,
        "claim_support": claim_support,
        "iterations": iterations,
        "contributions": contributions,
        "attribute_maxima": {
            claim: support == attribute_maxima[graph.claim_lookup[claim]]
            for claim, support in claim_support.items()
        },
        "conflicting_claims": {
            claim: tuple(
                other for other in claim_support
                if other != claim and graph.claim_lookup[other] == graph.claim_lookup[claim]
            )
            for claim in claim_support
        },
        "metadata": {
            "algorithm_version": ALGORITHM_VERSION,
            "iterations": iterations,
            "converged": True,
            "convergence_tolerance": CONVERGENCE_TOLERANCE,
            "convergence_delta": max(
                abs(reliability_vector[source] - previous[source])
                for source in source_ids
            ),
        },
    }

    if debug:
        result["history"] = history
        result["independence"] = independence
        result["degrees"] = degrees
        result["dependency_matrix"] = graph.dependency_matrix
    return result
