from braid.engine import evaluate


class BaseGraph:

    source_to_claims = {
        "source_1": {
            "claim_a",
        },
        "source_2": {
            "claim_a",
        },
    }

    claim_to_sources = {
        "claim_a": {
            "source_1",
            "source_2",
        },
    }

    agreement_weights = {
        ("source_1", "claim_a"): 1.0,
        ("source_2", "claim_a"): 1.0,
    }

    dependency_matrix = {
        "source_1": {
            "source_1": 0.0,
            "source_2": 0.0,
        },
        "source_2": {
            "source_1": 0.0,
            "source_2": 0.0,
        },
    }


class AdditionalClaimGraph:

    source_to_claims = {
        "source_1": {
            "claim_a",
        },
        "source_2": {
            "claim_a",
            "claim_b",
        },
    }

    claim_to_sources = {
        "claim_a": {
            "source_1",
            "source_2",
        },
        "claim_b": {
            "source_2",
        },
    }

    agreement_weights = {
        ("source_1", "claim_a"): 1.0,
        ("source_2", "claim_a"): 1.0,
        ("source_2", "claim_b"): 1.0,
    }

    dependency_matrix = {
        "source_1": {
            "source_1": 0.0,
            "source_2": 0.0,
        },
        "source_2": {
            "source_1": 0.0,
            "source_2": 0.0,
        },
    }


base = evaluate(
    BaseGraph()
)

additional_claim = evaluate(
    AdditionalClaimGraph()
)

print(
    "base claim_a support:",
    base["claim_support"]["claim_a"],
)

print(
    "with unrelated claim_b:",
    additional_claim["claim_support"]["claim_a"],
)

print(
    "change:",
    additional_claim["claim_support"]["claim_a"]
    - base["claim_support"]["claim_a"],
)
