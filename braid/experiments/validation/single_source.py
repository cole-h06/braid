from braid.engine import evaluate


class Graph:

    source_to_claims = {
        "source_1": {
            "claim_a"
        }
    }

    claim_to_sources = {
        "claim_a": {
            "source_1"
        }
    }

    agreement_weights = {
        (
            "source_1",
            "claim_a"
        ): 1.0
    }

    dependency_matrix = {
        "source_1": {
            "source_1": 0.0
        }
    }


result = evaluate(
    Graph()
)

print(result)
