from credibility.engine import infer
from credibility.loader import load_postgres
from credibility.source_dependency import compute_dependency_matrix


print()
print("Loading credibility graph...")
print()

graph = load_postgres()

print(len(graph.claim_lookup))

print(f"Sources:    {len(graph.source_to_claims)}")
print(f"Claims:     {len(graph.claim_to_sources)}")
print()

print("Computing source dependencies...")
print()

graph.dependency_matrix = compute_dependency_matrix()

print("Running credibility inference...")
print()

result = infer(
    graph
)

credibility = result["credibility"]
claim_support = result["claim_support"]
iterations = result["iterations"]

print(f"Converged in {iterations} iterations.")
print()

print("Top sources")

for source_id, score in sorted(

    credibility.items(),
    key=lambda item: item[1],
    reverse=True,

)[:10]:

    print(
        f"{graph.source_names[source_id]:<25} {score:.6f}"
    )

print()

print("Lowest sources")

for source_id, score in sorted(

    credibility.items(),
    key=lambda item: item[1],

)[:10]:

    print(
        f"{graph.source_names[source_id]:<25} {score:.6f}"
    )

print()

print("Highest supported claims")

for claim_id, score in sorted(

    claim_support.items(),
    key=lambda item: item[1],
    reverse=True,

)[:10]:

    product_id, attribute, value = graph.claim_lookup[
        claim_id
    ]

    print(
        f"{product_id:<15} "
        f"{attribute:<24} "
        f"{str(value):<20} "
        f"{score:.6f}"
    )

print()

print("Lowest supported claims")

for claim_id, score in sorted(

    claim_support.items(),
    key=lambda item: item[1],

)[:10]:

    product_id, attribute, value = graph.claim_lookup[
        claim_id
    ]

    print(
        f"{product_id:<15} "
        f"{attribute:<24} "
        f"{str(value):<20} "
        f"{score:.6f}"
    )