from braid.engine import evaluate


class Graph:

    source_to_claims = {

        "source_1": {
            "claim_a",
            "claim_b",
        },

        "source_2": {
            "claim_a",
            "claim_c",
        },

        "source_3": {
            "claim_a",
            "claim_d",
        },

        "source_4": {
            "claim_b",
            "claim_d",
        },

        "source_5": {
            "claim_c",
            "claim_d",
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
            "source_4",
        },

        "claim_c": {
            "source_2",
            "source_5",
        },

        "claim_d": {
            "source_3",
            "source_4",
            "source_5",
        },

    }

    agreement_weights = {

        ("source_1", "claim_a"): 1.0,
        ("source_2", "claim_a"): 0.9,
        ("source_3", "claim_a"): 0.8,

        ("source_1", "claim_b"): 1.0,
        ("source_4", "claim_b"): 1.0,

        ("source_2", "claim_c"): 1.0,
        ("source_5", "claim_c"): 0.9,

        ("source_3", "claim_d"): 1.0,
        ("source_4", "claim_d"): 0.9,
        ("source_5", "claim_d"): 0.8,

    }

    dependency_matrix = {

        "source_1": {

            "source_1": 0.0,
            "source_2": 0.80,
            "source_3": 0.10,
            "source_4": 0.20,
            "source_5": 0.00,

        },

        "source_2": {

            "source_1": 0.80,
            "source_2": 0.0,
            "source_3": 0.20,
            "source_4": 0.10,
            "source_5": 0.30,

        },

        "source_3": {

            "source_1": 0.10,
            "source_2": 0.20,
            "source_3": 0.0,
            "source_4": 0.40,
            "source_5": 0.20,

        },

        "source_4": {

            "source_1": 0.20,
            "source_2": 0.10,
            "source_3": 0.40,
            "source_4": 0.0,
            "source_5": 0.50,

        },

        "source_5": {

            "source_1": 0.00,
            "source_2": 0.30,
            "source_3": 0.20,
            "source_4": 0.50,
            "source_5": 0.0,

        },

    }


result = evaluate(
    Graph()
)

print(result)
