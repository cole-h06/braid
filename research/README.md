# BRAID Research

In this directory you can find the documented experimental research behind the BRAID algorithm.

## Methods

- [Reliability Propagation](reliability_propagation.md) describes the full process of how reliability and support scores are distributed between sources and claims. This process repeats across the graph until convergence.

- [Agreement Weighting](agreement_weighting.md) adjusts the influence each assertion has on claim support. We base this off the distribution of sources across conflicting claims.

- [Structural Source Dependencies](structural_source_dependencies.md) analyzes which source relationship signals can be derived from graph structure and identifies the limitations of structural dependency estimation.

- [Hybrid Source Dependencies](hybrid_source_dependencies.md) combines graph structure with provenance and contextual metadata to estimate pairwise source dependencies. Defines how those estimates can adjust reliability propagation.

## Experiments

The [`agent_dataset`](../agent_dataset/README.md) contains the test for evaluating the dependency framework using a controlled multi-agent dataset and enterprise retrieval workflow.

In the [`benchmark`](../benchmark/README.md) you can find the reproducible product specification dataset used during development.

The BRAID reference implementation is located in [`braid`](../braid/).

## Status

Please note these documents are notes in progress, not a final specification.

The developing research paper is located in [`paper`](../paper/).
