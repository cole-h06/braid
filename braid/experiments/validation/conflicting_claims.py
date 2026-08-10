from braid.engine import evaluate


class Graph:

    source_to_claims = {

        "source_1": {
            "claim_true",
        },

        "source_2": {
            "claim_true",
        },

        "source_3": {
            "claim_false",
        },

        "source_4": {
            "claim_false",
        },

    }

    claim_to_sources = {

        "claim_true": {
            "source_1",
            "source_2",
        },

        "claim_false": {
            "source_3",
            "source_4",
        },

    }

    agreement_weights = {

        ("source_1", "claim_true"): 1.0,
        ("source_2", "claim_true"): 1.0,

        ("source_3", "claim_false"): 1.0,
        ("source_4", "claim_false"): 1.0,

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

        "source_3": {

            "source_3": 0.0,
            "source_4": 0.0,

        },

        "source_4": {

            "source_3": 0.0,
            "source_4": 0.0,

        },

    }


result = evaluate(
    Graph()
)

print(result)
