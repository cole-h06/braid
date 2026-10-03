"""Historical research diagnostic; not used by the current BRAID estimator."""


def graph_matrix(

    inclusion_matrix,
    rarity_matrix,

    beta_inclusion=0.5,
    beta_rarity=0.5

):

    graph_matrix = {}

    for source_i in inclusion_matrix:

        graph_matrix[source_i] = {}

        for source_k in inclusion_matrix[source_i]:

            # combine the structural signals
            graph_matrix[source_i][source_k] = (

                beta_inclusion
                * inclusion_matrix[source_i][source_k]

                +

                beta_rarity
                * rarity_matrix[source_i][source_k]

            )

    return graph_matrix



def print_matrix(
    matrix
):

    ...

