# BRAID Research

In this directory you can find the documented mathematical framework and research behind the BRAID algorithm.

## Methods

- [Reliability Propagation](reliability_propagation.md) describes the full process of how reliability and support scores are distributed between sources and claims. This process repeats across the graph until convergence.

- [Agreement Weighting](agreement_weighting.md) adjusts the influence each assertion has on claim support. We base this off the distribution of sources across conflicting claims.

- [Structural Source Dependencies](structural_source_dependencies.md) defines the graph-derived structural redundancy signal used for source dependency estimation.

- [Source Dependency Estimation](source_dependency_estimation.md) defines the v1 model for estimating pairwise source dependencies by combining graph-derived structural redundancy with provenance and metadata. It goes in full detail on how those estimates adjust reliability propagation.

## Experiments

The [`agent_dataset`](../agent_dataset/README.md) contains the test for evaluating the dependency framework using a controlled multi-agent dataset and enterprise retrieval workflow.

In the [`benchmark`](../benchmark/README.md) you can find the reproducible product specification dataset used during development.

The BRAID reference implementation is located in [`braid`](../braid/).

## Status

The methods documents describe the current mathematical framework implemented by BRAID. Experimental results are subject to change as the model develops.