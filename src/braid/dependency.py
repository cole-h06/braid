import math

from datetime import timedelta
from itertools import combinations


SIGNAL_NAMES = (
    "upstream", "citation", "assertion_lineage",
    "ownership", "temporal", "graph", "retrieval",
)
DIRECT_SIGNALS = ("upstream", "citation", "assertion_lineage")


def normalize_weights(weights):
    if set(weights) not in (set(SIGNAL_NAMES), set(SIGNAL_NAMES[:-1])):
        raise ValueError("weights must contain the six original signals and optional retrieval")
    supplied = {name: weights.get(name, 0.0) for name in SIGNAL_NAMES}
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0.0
        for value in supplied.values()
    ):
        raise ValueError("weights must be finite and non-negative")
    total = sum(supplied.values())
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("weights must have a positive finite sum")
    return {name: value / total for name, value in supplied.items()}


def combine_signals(signals, observable, weights, excluded=()):
    normalized = normalize_weights(weights)
    if set(signals) != set(SIGNAL_NAMES) or set(observable) != set(SIGNAL_NAMES):
        raise ValueError("all seven signals and masks are required")
    for name in SIGNAL_NAMES:
        value = signals[name]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError("signal values must be finite and in [0, 1]")
        if observable[name] not in (False, True):
            raise ValueError("observability must be binary")
    if set(excluded) - set(SIGNAL_NAMES):
        raise ValueError("unknown excluded signal")
    available = [
        name for name in SIGNAL_NAMES
        if observable[name] and name not in excluded
    ]
    coverage = sum(normalized[name] for name in available)
    if coverage == 0.0:
        return 0.0, 0.0
    direct = max((
        signals[name] for name in available
        if name in DIRECT_SIGNALS and normalized[name] > 0.0
    ), default=0.0)
    contextual = sum(
        normalized[name] * signals[name]
        for name in available if name not in DIRECT_SIGNALS
    )
    return max(0.0, min(1.0, max(direct, contextual))), coverage


def empty_matrix(source_ids):
    return {
        source: {other: 0.0 for other in source_ids}
        for source in source_ids
    }


def validate_records(sources, assertions, evidence):
    source_ids = [source.source_id for source in sources]
    assertion_ids = [assertion.assertion_id for assertion in assertions]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("source IDs must be unique")
    if len(set(assertion_ids)) != len(assertion_ids):
        raise ValueError("assertion IDs must be unique")
    if not source_ids or not assertion_ids:
        raise ValueError("observation graph must not be empty")
    known_sources = set(source_ids)
    assertion_lookup = {assertion.assertion_id: assertion for assertion in assertions}
    seen = set()
    for assertion in assertions:
        if assertion.source_id not in known_sources:
            raise ValueError("assertion references unknown source")
        key = assertion.source_id, assertion.entity, assertion.attribute
        if key in seen:
            raise ValueError("source has multiple values for one property")
        seen.add(key)
    if {assertion.source_id for assertion in assertions} != known_sources:
        raise ValueError("every source must have an assertion")
    counts = {identifier: 0 for identifier in assertion_ids}
    for item in evidence:
        if item.assertion_id not in counts:
            raise ValueError("evidence references unknown assertion")
        counts[item.assertion_id] += 1
        source = assertion_lookup[item.assertion_id].source_id
        for field in ("observed_at", "source_modified_at"):
            value = getattr(item, field)
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                label = "source modification timestamps" if field == "source_modified_at" else field
                raise ValueError(f"{label} must be timezone-aware")
        if source in (item.upstream_source_ids or ()):
            raise ValueError("source cannot reference itself as upstream")
        for cited in item.cited_source_ids or ():
            if cited not in known_sources:
                raise ValueError("evidence cites unknown source")
            if cited == source:
                raise ValueError("source cannot cite itself")
        for parent in item.parent_assertion_ids or ():
            if parent not in assertion_lookup:
                raise ValueError("evidence references unknown parent assertion")
            if assertion_lookup[parent].source_id == source:
                raise ValueError("parent assertion cannot belong to the same source")
    if any(count != 1 for count in counts.values()):
        raise ValueError("every assertion must have exactly one evidence record")


def compute_hybrid_dependency(
    graph, sources, assertions, evidence, weights,
    temporal_window=timedelta(hours=2),
):
    normalized = normalize_weights(weights)
    window = temporal_window.total_seconds()
    if not math.isfinite(window) or window <= 0.0:
        raise ValueError("temporal window must be finite and positive")
    validate_records(sources, assertions, evidence)
    source_lookup = {source.source_id: source for source in sources}
    source_ids = sorted(source_lookup)
    assertion_lookup = {assertion.assertion_id: assertion for assertion in assertions}
    evidence_lookup = {item.assertion_id: item for item in evidence}
    rows = {source: {} for source in source_ids}
    expected_edges = set()
    for assertion in assertions:
        attribute = assertion.entity, assertion.attribute
        rows[assertion.source_id][attribute] = (
            assertion.value, evidence_lookup[assertion.assertion_id],
        )
        expected_edges.add((assertion.source_id, (*attribute, assertion.value)))
    graph_edges = {
        (source, claim) for source, claims in graph.source_to_claims.items()
        for claim in claims
    }
    if graph_edges != expected_edges:
        raise ValueError("graph and assertion records disagree")
    signals = {name: empty_matrix(source_ids) for name in SIGNAL_NAMES}
    observability = {name: empty_matrix(source_ids) for name in SIGNAL_NAMES}
    dependency = empty_matrix(source_ids)
    confidence = empty_matrix(source_ids)
    directions = {
        name + "_directions": empty_matrix(source_ids)
        for name in DIRECT_SIGNALS
    }
    directions["temporal_directions"] = empty_matrix(source_ids)
    owners = [source_lookup[source].owner_id for source in source_ids]
    excluded = ("ownership",) if None not in owners and len(set(owners)) == 1 else ()

    for first, second in combinations(source_ids, 2):
        first_rows = rows[first]
        second_rows = rows[second]
        matches = sorted(
            attribute for attribute in first_rows.keys() & second_rows.keys()
            if first_rows[attribute][0] == second_rows[attribute][0]
        )
        values = {name: 0.0 for name in SIGNAL_NAMES}
        masks = {name: False for name in SIGNAL_NAMES}
        for name, field in (
            ("upstream", "upstream_source_ids"),
            ("citation", "cited_source_ids"),
            ("assertion_lineage", "parent_assertion_ids"),
        ):
            relationships = []
            captured = []
            for source, other in ((first, second), (second, first)):
                items = [row[1] for row in rows[source].values()]
                captured.append(all(getattr(item, field) is not None for item in items))
                identities = {
                    identifier for item in items
                    for identifier in (getattr(item, field) or ())
                }
                if name == "assertion_lineage":
                    identities = {assertion_lookup[parent].source_id for parent in identities}
                relationships.append(identities)
                directions[name + "_directions"][source][other] = float(other in identities)
            positive = second in relationships[0] or first in relationships[1]
            if name == "upstream":
                positive = positive or bool(relationships[0] & relationships[1])
            values[name] = float(positive)
            masks[name] = positive or all(captured)
        first_owner = source_lookup[first].owner_id
        second_owner = source_lookup[second].owner_id
        masks["ownership"] = first_owner is not None and second_owner is not None
        values["ownership"] = float(masks["ownership"] and first_owner == second_owner)
        masks["temporal"] = bool(matches) and all(
            first_rows[attribute][1].source_modified_at is not None
            and second_rows[attribute][1].source_modified_at is not None
            for attribute in matches
        )
        if masks["temporal"]:
            values["temporal"] = sum(
                max(0.0, 1.0 - abs((
                    first_rows[attribute][1].source_modified_at
                    - second_rows[attribute][1].source_modified_at
                ).total_seconds()) / window)
                for attribute in matches
            ) / len(matches)
        directions["temporal_directions"][first][second] = values["temporal"]
        directions["temporal_directions"][second][first] = values["temporal"]
        if matches:
            resources = [
                (
                    {(item.kind, item.resource_id) for item in (first_rows[attribute][1].retrievals or ())},
                    {(item.kind, item.resource_id) for item in (second_rows[attribute][1].retrievals or ())},
                )
                for attribute in matches
            ]
            values["retrieval"] = sum(bool(left & right) for left, right in resources) / len(matches)
            masks["retrieval"] = any(left or right for left, right in resources)
        estimate, coverage = combine_signals(values, masks, weights, excluded)
        for source, other in ((first, second), (second, first)):
            dependency[source][other] = estimate
            confidence[source][other] = coverage
            for name in SIGNAL_NAMES:
                signals[name][source][other] = values[name]
                observability[name][source][other] = float(masks[name])
    return {
        "weights": normalized,
        "signals": signals,
        "observability": observability,
        "dependency_matrix": dependency,
        "confidence_matrix": confidence,
        "excluded_signals": excluded,
        "diagnostics": directions,
    }


def cluster_members(source_ids, dependency, threshold):
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0.0 <= threshold <= 1.0
    ):
        raise ValueError("threshold must be finite and between zero and one")
    remaining = set(source_ids)
    components = []
    for start in sorted(source_ids):
        if start not in remaining:
            continue
        remaining.remove(start)
        pending = [start]
        component = []
        while pending:
            source = pending.pop()
            component.append(source)
            connected = {
                other for other in remaining
                if dependency[source][other] >= threshold
            }
            remaining -= connected
            pending.extend(sorted(connected))
        components.append(tuple(sorted(component)))
    return tuple(components)


def count_clusters(source_ids, dependency, threshold):
    return len(cluster_members(source_ids, dependency, threshold))


def claim_telemetry(graph, hybrid, threshold=None):
    dependency = hybrid["dependency_matrix"]
    confidence = hybrid["confidence_matrix"]
    if threshold is not None:
        cluster_members((), {}, threshold)
    claims = {}
    for claim, source_ids in sorted(graph.claim_to_sources.items()):
        source_ids = tuple(sorted(source_ids))
        count = len(source_ids)
        pairs = tuple(combinations(source_ids, 2))
        total = sum(dependency[first][second] for first, second in pairs)
        coverage = (
            sum(confidence[first][second] for first, second in pairs) / len(pairs)
            if pairs else None
        )
        components = (
            cluster_members(source_ids, dependency, threshold)
            if threshold is not None else None
        )
        claims[claim] = {
            "supporting_source_count": count,
            "estimated_independent_support_count": count ** 2 / (count + 2 * total),
            "dependency_signal_coverage": coverage,
            "dependency_confidence": coverage,
            "dependency_clusters": len(components) if components is not None else None,
            "cluster_members": components,
        }
    return {"threshold": threshold, "claims": claims}
