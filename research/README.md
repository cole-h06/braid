# Verity Research

In this directory you can find the documented research of the mathematical and experimental of the Verity credibility inference engine.

The research includes the baseline credibility propagation algorithm, as well as methods for accounting for claim agreement and relationships between sources.

## Framework

- [Credibility Propagation](credibility_propagation.md) describes the baseline iterative algorithm.

- [Agreement Weighting](agreement_weighting.md) explains how the influence of each assertion can be changed based on the distribution of sources across conflicting claims.

- [Structural Source Dependencies](structural_source_dependencies.md) analyze if assertion overlap and graph structure can provide meaningful signals relating to source relationships.

- [Hybrid Source Dependencies](hybrid_source_dependencies.md) combines graph structure with provenance and metadata evidence. Also defines how source dependency affects propagation and claim-level telemetry.

## Experiments

The [`agent_dataset`](../agent_dataset/README.md) contains the test for evaluating the dependency framework using a controlled multi-agent dataset and enterprise retrieval workflow.

In the [`benchmark`](../benchmark/README.md) you can find the reproducible product specification dataset used during development.

The inference engine and dependency analysis code are located in [`credibility`](../credibility/).

## Status

Please note these documents are research notes in progress, not a final specification.

The developing research paper is located in [`paper`](../paper/).