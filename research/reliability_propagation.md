# Reliability Propagation

## Motivation

Source reliability and claim support depend on each other. A source gains reliability when it supports claims that receive stronger support across the information network. And a claim, in turn, receives stronger support when it is asserted by sources with higher reliability.

BRAID models these relationships as a bipartite graph. It repeatedly propagates reliability between the source and claim nodes until the source scores converge.

## Graph Framework

Let

$$ G=(S,C,E) $$

define the bipartite graph, where

- $S$ is the set of sources,
- $C$ is the set of claims, and
- $E$ is the set of assertions connecting sources to claims.

An edge $(i,j)\in E$ means that source $i$ asserts claim $j$.

Let

- $A(j)$ denote the sources asserting claim $j$,
- $C(i)$ denote the claims asserted by source $i$, and
- $d_i=|C(i)|$ denote the number of claims asserted by source $i$.

At iteration $t$, let

- $s_i^{(t)}$ represent the reliability of source $i$, and
- $c_j^{(t)}$ represent the support received by claim $j$.

## Initialization

We first distribute reliability evenly (uniformly) across all asserting sources:

$$ s_i^{(0)}=\frac{1}{|S|} $$

This starts each source with the same initial reliability and ensures that

$$ \sum_{i\in S}s_i^{(0)}=1. $$

It is important to note that the initialized scores do not reflect any prior knowledge about the sources. They simply provide us a neutral starting point that allows us to infer reliability from the graph.

## Source-to-Claim Propagation

Each source distributes its current reliability equally across the claims it asserts.

The contribution from source $i$ to one of its claims is

$$ \frac{s_i^{(t)}}{d_i}. $$

We calculate claim support by adding the contributions from every source asserting the claim:

$$ c_j^{(t)}=\sum_{i\in A(j)}\frac{s_i^{(t)}}{d_i}. $$

We intentionally divide by a source degree to prevent a source contributing its complete reliability to every claim it asserts. If a source has many assertions, it must distribute its reliability across those assertions. In contrast, a source with fewer assertions consolidates its reliability over a smaller set of claims.

## Claim-to-Source Propagation

Once we calculate claim support, each source receives support from the claims it asserts.

The unnormalized reliability of source $i$ for the next iteration is

$$ \tilde{s}_i^{(t+1)}=\sum_{j\in C(i)}c_j^{(t)}. $$

Sources receive more reliability when they connect to strongly supported claims. Because those claim-support values were produced by the source scores from the previous iteration, both reliability and claim support are updated through the graph recursively.

## Normalization

We now update the source values by normalizing them so that the complete source-reliability vector continues to sum to $1$:

$$ s_i^{(t+1)}=\frac{\tilde{s}_i^{(t+1)}}{\sum_{k\in S}\tilde{s}_k^{(t+1)}}. $$

Normalization makes each source's score relative to the other sources present in the graph. This means that a score is a source's share of the total reliability inferred from the graph, not a probabilistic guess that the source is truthful.

## Convergence

We continue propagation until the largest change in source reliability between two consecutive iterations falls below a fixed tolerance:

$$ \left\|s^{(t+1)}-s^{(t)}\right\|_{\infty}<\varepsilon. $$

Currently, it is implemented as

$$ \varepsilon=10^{-8}. $$

The largest absolute change across all source scores is chosen by the infinity norm:

$$ \left\|s^{(t+1)}-s^{(t)}\right\|_{\infty}=\max_{i\in S}\left|s_i^{(t+1)}-s_i^{(t)}\right|. $$

We consider the source reliability vector as having reached a fixed point or, "converged", the moment this condition is met. We calculate final claim support from the converged source scores.

## Matrix Representation

Let

$$ M\in\{0,1\}^{|S|\times|C|} $$

be the assertion matrix, where

$$ M_{ij}=\begin{cases}1, & \text{if source } i \text{ asserts claim } j \\ 0, & \text{otherwise}\end{cases}. $$

Let $D_S$ be the diagonal source-degree matrix:

$$ D_S=\text{diag}(d_1,\ldots,d_{|S|}). $$

We can then write source-to-claim propagation as

$$ c^{(t)}=M^\mathsf{T}D_S^{-1}s^{(t)}. $$

Claim-to-source propagation is

$$ \tilde{s}^{(t+1)}=Mc^{(t)}. $$

By combining both steps, we get

$$ \tilde{s}^{(t+1)}=MM^\mathsf{T}D_S^{-1}s^{(t)}, $$

followed by normalization of $\tilde{s}^{(t+1)}$ to produce $s^{(t+1)}$.

## Interpretation

Reliability is measured from the distribution of assertions throughout the graph. Sources receive reliability by supporting claims that have strong support across the network. And claims receive support from the reliability of their asserting sources.

The final score values are internal graph scores. They do not, however, imply probabilities of truth, nor do they directly analyze a claim's semantic meaning.

We treat each assertion equally using this baseline framework. [Agreement weighting](agreement_weighting.md) expands source-to-claim propagation by accounting for agreement or conflict. [Source Dependency Estimation](source_dependency_estimation.md) discounts evidence based on the dependency relationships between sources.
