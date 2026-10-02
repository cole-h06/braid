from braid.engine import evaluate


class Graph:

    source_to_claims = {
        "source_1": {
            "shared_claim",
        },
        "source_2": {
            "shared_claim",
            "extra_1",
            "extra_2",
            "extra_3",
            "extra_4",
            "extra_5",
        },
    }

    claim_to_sources = {
        "shared_claim": {
            "source_1",
            "source_2",
        },
        "extra_1": {"source_2"},
        "extra_2": {"source_2"},
        "extra_3": {"source_2"},
        "extra_4": {"source_2"},
        "extra_5": {"source_2"},
    }

    agreement_weights = {
        ("source_1", "shared_claim"): 1.0,
        ("source_2", "shared_claim"): 1.0,
        ("source_2", "extra_1"): 1.0,
        ("source_2", "extra_2"): 1.0,
        ("source_2", "extra_3"): 1.0,
        ("source_2", "extra_4"): 1.0,
        ("source_2", "extra_5"): 1.0,
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


result = evaluate(Graph())

print("reliability:", result["reliability"])
print(
    "shared claim support:",
    result["claim_support"]["shared_claim"],
)
print("iterations:", result["iterations"])
