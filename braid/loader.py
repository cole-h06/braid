import csv

from collections import defaultdict

from .graph import BipartiteGraph, prepare_graph


def load_from_csv(folder):

    source_names = load_sources(
        folder
    )

    (
        source_to_claims,
        claim_to_sources,
        source_to_assertions,
    ) = load_assertions(
        folder
    )

    claim_lookup = load_claims(
        folder
    )  

    claim_lookup = {
        claim: claim_lookup[claim]
        for claim in claim_to_sources
    }
    graph = prepare_graph(BipartiteGraph(
        source_to_claims,
        claim_to_sources,
        source_names,
        {},
        claim_lookup,
        source_to_assertions,
    ))
    agreement_weights = graph.agreement_weights

    return (
        source_to_claims,
        claim_to_sources,
        source_names,
        agreement_weights,
        claim_lookup,
        source_to_assertions,
    )


def load_sources(folder):

    source_names = {}

    path = f"{folder}/sources.csv"

    with open(
        path,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            source_id = int(
               row["source_id"]
            )

            source_names[source_id] = row[
                "name"
            ]

    return source_names


def load_claims(folder):

    claim_lookup = {}

    path = f"{folder}/claims.csv"

    with open(
        path,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            claim_lookup[
                int(row["claim_id"])
            ] = (
                row["product_id"],
                row["attribute"],
            )

    return claim_lookup


def load_assertions(folder):

    source_to_claims = defaultdict(set)
    claim_to_sources = defaultdict(set)
    source_to_assertions = defaultdict(dict)

    path = f"{folder}/assertions.csv"

    with open(
        path,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            source_id = int(
                row["source_id"]
            )

            claim_id = int(
                row["claim_id"]
            )

            if row["value_string"]:

                value = row["value_string"]

            else:

                value = row["value_numeric"]

            source_to_assertions[
                source_id
            ][claim_id] = value

            source_to_claims[
                source_id
            ].add(
                claim_id
            )

            claim_to_sources[
                claim_id
            ].add(
                source_id
            )

    return (
        source_to_claims,
        claim_to_sources,
        source_to_assertions,
    )


def load_agreement_weights(folder, claim_lookup):
    source_claims, claim_sources, source_assertions = load_assertions(folder)
    return prepare_graph(BipartiteGraph(
        source_claims,
        claim_sources,
        {},
        {},
        {claim: claim_lookup[claim] for claim in claim_sources},
        source_assertions,
    )).agreement_weights
