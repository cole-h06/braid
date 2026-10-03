"""Historical research diagnostic; not used by the current BRAID estimator."""


from collections import defaultdict
from itertools import combinations

import networkx as nx


def build_source_claims(rows):

    source_claims = defaultdict(set)

    for (
        source_id,
        product_id,
        attribute,
        value_string,
        value_numeric,
        unit
    ) in rows:

        value = (
            value_numeric
            if value_numeric is not None
            else value_string
        )

        claim = (
            product_id,
            attribute,
            value,
            unit
        )

        source_claims[source_id].add(claim)

    return source_claims



def build_claim_sources(source_claims):

    claim_sources = defaultdict(set)

    for source_id, claims in source_claims.items():

        for claim in claims:

            claim_sources[claim].add(source_id)

    return claim_sources



def build_source_graph(claim_sources):

    graph = nx.Graph()

    # connect sources that assert the same claim
    for sources in claim_sources.values():

        if len(sources) < 2:
            continue

        for source_a, source_b in combinations(sorted(sources), 2):

            if graph.has_edge(source_a, source_b):

                graph[source_a][source_b]["weight"] += 1

            else:

                graph.add_edge(
                    source_a,
                    source_b,
                    weight=1
                )

    return graph



def find_communities(graph):

    return list(
        nx.community.louvain_communities(
            graph,
            weight="weight"
        )
    )



def print_communities(
    communities,
    source_names
):

    print()
    print("Communities")
    print("-" * 40)

    for i, community in enumerate(communities, start=1):

        print()
        print(f"Community {i}")

        for source in sorted(community):

            print(
                f"  {source_names.get(source, source)}"
            )



def print_edge_weights(
    graph,
    source_names
):

    print()
    print("Edge Weights")
    print("-" * 40)

    edges = sorted(
        graph.edges(data=True),
        key=lambda edge: edge[2]["weight"],
        reverse=True
    )

    for source_a, source_b, data in edges:

        print(
            f"{source_names[source_a]} ↔ "
            f"{source_names[source_b]} : "
            f"{data['weight']}"
        )



def print_bridge_edges(
    graph,
    communities,
    source_names
):

    print()
    print("Bridge Edges")
    print("-" * 40)

    community_map = {}

    for i, community in enumerate(communities):

        for source in community:

            community_map[source] = i

    bridges = []

    for source_a, source_b, data in graph.edges(data=True):

        if community_map[source_a] != community_map[source_b]:

            bridges.append(
                (
                    data["weight"],
                    source_a,
                    source_b
                )
            )

    bridges.sort(reverse=True)

    for weight, source_a, source_b in bridges:

        print(
            f"{source_names[source_a]} ↔ "
            f"{source_names[source_b]} : "
            f"{weight}"
        )

