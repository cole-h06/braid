from backend.credibility.engine import infer


class Graph:

    source_to_claims = {

        "source_1": {
            "claim_a",
            "claim_b",
        },

        "source_2": {
            "claim_a",
        },

        "source_3": {
            "claim_a",
        },

    }

    claim_to_sources = {

        "claim_a": {
            "source_1",
            "source_2",
            "source_3",
        },

        "claim_b": {
            "source_1",
        },

    }

    agreement_weights = {

        ("source_1", "claim_a"): 1.0,
        ("source_2", "claim_a"): 1.0,
        ("source_3", "claim_a"): 1.0,

        ("source_1", "claim_b"): 1.0,

    }

    dependency_matrix = {

        "source_1": {

            "source_1": 0.0,
            "source_2": 0.90,
            "source_3": 0.0,

        },

        "source_2": {

            "source_1": 0.90,
            "source_2": 0.0,
            "source_3": 0.0,

        },

        "source_3": {

            "source_1": 0.0,
            "source_2": 0.0,
            "source_3": 0.0,

        },

    }


result = infer(
    Graph()
)

print(result)