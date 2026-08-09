import math

from datetime import timedelta
from itertools import combinations

from reliability.analysis.evidence_independence import build_pairwise_rows


SIGNAL_NAMES = (
    "provenance",
    "lineage",
    "ownership",
    "temporal",
    "graph",
)

OBSERVABILITY_NAMES = (
    "provenance",
    "lineage",
    "ownership",
    "temporal",
    "structure",
)


def normalize_weights(weights):

    if set(weights) != set(SIGNAL_NAMES):
        raise ValueError("weights must contain exactly five signal names")

    if any(
        not math.isfinite(value) or value < 0.0
        for value in weights.values()
    ):
        raise ValueError("weights must be finite and non-negative")

    total = sum(weights.values())

    if total <= 0.0:
        raise ValueError("weights must have a positive sum")

    # normalize the weights without changing the input
    return {
        name: value / total
        for name, value in weights.items()
    }


def compute_hybrid_dependency(
    graph,
    sources,
    assertions,
    evidence,
    weights,
    temporal_window=timedelta(hours=2),
):

    normalized_weights = normalize_weights(weights)

    temporal_seconds = temporal_window.total_seconds()

    if not math.isfinite(temporal_seconds) or temporal_seconds <= 0.0:
        raise ValueError("temporal window must be finite and positive")

    source_ids = [
        source.source_id
        for source in sources
    ]

    source_lookup = {
        source.source_id: source
        for source in sources
    }

    assertion_lookup = {
        assertion.assertion_id: assertion
        for assertion in assertions
    }

    evidence_lookup = {
        item.assertion_id: item
        for item in evidence
    }

    provenance_capture = build_capture(
        source_ids,
        assertion_lookup,
        evidence,
        ("provenance_ids",),
    )

    lineage_capture = build_capture(
        source_ids,
        assertion_lookup,
        evidence,
        (
            "cited_source_ids",
            "parent_assertion_ids",
        ),
    )

    temporal_capture = build_capture(
        source_ids,
        assertion_lookup,
        evidence,
        ("observed_at",),
    )

    provenance = build_provenance(
        source_ids,
        assertion_lookup,
        evidence,
    )

    lineage = build_lineage(
        source_ids,
        assertion_lookup,
        evidence,
    )

    temporal = build_temporal(
        source_ids,
        graph.source_to_assertions,
        assertions,
        evidence_lookup,
        temporal_window,
    )

    structure = build_structure(
        graph
    )

    signals = {
        name: empty_matrix(source_ids)
        for name in SIGNAL_NAMES
    }

    observability = {
        name: empty_matrix(source_ids)
        for name in OBSERVABILITY_NAMES
    }

    dependency_matrix = empty_matrix(source_ids)
    confidence_matrix = empty_matrix(source_ids)

    # compare one source pair
    for source_a, source_b in combinations(source_ids, 2):

        pair_signals = {
            "provenance": provenance_score(
                provenance[source_a],
                provenance[source_b],
            ),
            "lineage": max(
                lineage[source_a][source_b],
                lineage[source_b][source_a],
            ),
            "ownership": ownership_score(
                source_lookup[source_a],
                source_lookup[source_b],
            ),
            "temporal": max(
                temporal[source_a][source_b],
                temporal[source_b][source_a],
            ),
            "graph": structural_score(
                structure,
                source_a,
                source_b,
            ),
        }

        if not (
            provenance_capture[source_a]
            and provenance_capture[source_b]
        ):
            pair_signals["provenance"] = 0.0

        pair_observability = {
            "provenance": float(
                provenance_capture[source_a]
                and provenance_capture[source_b]
            ),
            "lineage": float(
                pair_signals["lineage"] == 1.0
                or (
                    lineage_capture[source_a]
                    and lineage_capture[source_b]
                )
            ),
            "ownership": float(
                source_lookup[source_a].owner_id is not None
                and source_lookup[source_b].owner_id is not None
            ),
            "temporal": float(
                temporal_capture[source_a]
                and temporal_capture[source_b]
            ),
            "structure": 1.0,
        }

        # combine the five signals using the normalized weights
        dependency = sum(
            normalized_weights[name] * value
            for name, value in pair_signals.items()
        )

        dependency = min(1.0, max(0.0, dependency))

        confidence = sum(
            normalized_weights[
                "graph" if name == "structure" else name
            ] * value
            for name, value in pair_observability.items()
        ) / sum(normalized_weights.values())

        for name, value in pair_signals.items():
            signals[name][source_a][source_b] = value
            signals[name][source_b][source_a] = value

        for name, value in pair_observability.items():
            observability[name][source_a][source_b] = value
            observability[name][source_b][source_a] = value

        dependency_matrix[source_a][source_b] = dependency
        dependency_matrix[source_b][source_a] = dependency
        confidence_matrix[source_a][source_b] = confidence
        confidence_matrix[source_b][source_a] = confidence

    diagnostics = {
        "lineage_directions": lineage,
        "temporal_directions": temporal,
    }

    return {
        "weights": normalized_weights,
        "signals": signals,
        "observability": observability,
        "dependency_matrix": dependency_matrix,
        "confidence_matrix": confidence_matrix,
        "diagnostics": diagnostics,
    }


def empty_matrix(source_ids):

    return {
        source_id: {
            other_id: 0.0
            for other_id in source_ids
        }
        for source_id in source_ids
    }


def build_capture(
    source_ids,
    assertion_lookup,
    evidence,
    fields,
):

    seen = {
        source_id: False
        for source_id in source_ids
    }

    available = {
        source_id: True
        for source_id in source_ids
    }

    for item in evidence:

        source_id = assertion_lookup[item.assertion_id].source_id

        seen[source_id] = True

        if any(
            getattr(item, field) is None
            for field in fields
        ):
            available[source_id] = False

    return {
        source_id: seen[source_id] and available[source_id]
        for source_id in source_ids
    }


def build_provenance(
    source_ids,
    assertion_lookup,
    evidence,
):

    provenance = {
        source_id: set()
        for source_id in source_ids
    }

    for item in evidence:

        source_id = assertion_lookup[item.assertion_id].source_id

        if item.provenance_ids is not None:
            provenance[source_id].update(item.provenance_ids)

    return provenance


def provenance_score(
    provenance_a,
    provenance_b,
):

    union = provenance_a | provenance_b

    if not union:
        return 0.0

    return len(provenance_a & provenance_b) / len(union)


def build_lineage(
    source_ids,
    assertion_lookup,
    evidence,
):

    directions = empty_matrix(source_ids)

    for item in evidence:

        child_source = assertion_lookup[item.assertion_id].source_id

        for parent_source in item.cited_source_ids or ():
            directions[child_source][parent_source] = 1.0

        for parent_id in item.parent_assertion_ids or ():

            parent_source = assertion_lookup[parent_id].source_id

            directions[child_source][parent_source] = 1.0

    return directions


def build_temporal(
    source_ids,
    source_to_assertions,
    assertions,
    evidence_lookup,
    temporal_window,
):

    directions = empty_matrix(source_ids)

    observed_at = {}

    for assertion in assertions:

        property_key = (
            assertion.entity,
            assertion.attribute,
        )

        observed_at[assertion.source_id, property_key] = (
            evidence_lookup[assertion.assertion_id].observed_at
        )

    for child_source, parent_source in combinations(source_ids, 2):

        directions[child_source][parent_source] = temporal_score(
            child_source,
            parent_source,
            source_to_assertions,
            observed_at,
            temporal_window,
        )

        directions[parent_source][child_source] = temporal_score(
            parent_source,
            child_source,
            source_to_assertions,
            observed_at,
            temporal_window,
        )

    return directions


def temporal_score(
    child_source,
    parent_source,
    source_to_assertions,
    observed_at,
    temporal_window,
):

    child_assertions = source_to_assertions[child_source]
    parent_assertions = source_to_assertions[parent_source]

    matches = [
        property_key
        for property_key in child_assertions.keys() & parent_assertions.keys()
        if child_assertions[property_key] == parent_assertions[property_key]
    ]

    if not matches:
        return 0.0

    qualifying = 0

    for property_key in matches:

        difference = (
            observed_at[child_source, property_key]
            - observed_at[parent_source, property_key]
        )

        if timedelta(0) < difference <= temporal_window:
            qualifying += 1

    return qualifying / len(matches)


def ownership_score(
    source_a,
    source_b,
):

    if source_a.owner_id is None or source_b.owner_id is None:
        return 0.0

    return float(source_a.owner_id == source_b.owner_id)


def build_structure(graph):

    rows, _ = build_pairwise_rows(graph)

    scores = {}

    for row in rows:

        redundancy = row[0]
        source_a = row[7]
        source_b = row[8]

        scores[source_a, source_b] = redundancy
        scores[source_b, source_a] = redundancy

    return scores


def structural_score(
    scores,
    source_a,
    source_b,
):

    return scores.get(
        (source_a, source_b),
        0.0,
    )


def claim_telemetry(
    graph,
    hybrid,
    threshold,
):

    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be finite and between zero and one")

    dependency = hybrid["dependency_matrix"]
    confidence = hybrid["confidence_matrix"]
    claims = {}

    for claim_id, source_ids in graph.claim_to_sources.items():

        source_ids = tuple(sorted(source_ids))
        source_count = len(source_ids)

        if source_count == 1:
            claims[claim_id] = {
                "supporting_source_count": 1,
                "estimated_independent_support_count": 1.0,
                "dependency_clusters": 1,
                "dependency_confidence": None,
            }
            continue

        pairs = tuple(combinations(source_ids, 2))
        dependency_sum = sum(
            dependency[source_a][source_b]
            for source_a, source_b in pairs
        )

        independent_count = (
            source_count ** 2
            / (source_count + 2 * dependency_sum)
        )

        pair_confidence = sum(
            confidence[source_a][source_b]
            for source_a, source_b in pairs
        ) / len(pairs)

        claims[claim_id] = {
            "supporting_source_count": source_count,
            "estimated_independent_support_count": independent_count,
            "dependency_clusters": count_clusters(
                source_ids,
                dependency,
                threshold,
            ),
            "dependency_confidence": pair_confidence,
        }

    return {
        "threshold": threshold,
        "claims": claims,
    }


def count_clusters(
    source_ids,
    dependency,
    threshold,
):

    remaining = set(source_ids)
    clusters = 0

    while remaining:

        clusters += 1
        pending = [remaining.pop()]

        while pending:

            source_id = pending.pop()
            connected = {
                other_id
                for other_id in remaining
                if dependency[source_id][other_id] >= threshold
            }

            remaining -= connected
            pending.extend(connected)

    return clusters
