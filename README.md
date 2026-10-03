# BRAID

*Bipartite Reliability Analysis for Interdependent Data-Sources*

[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

BRAID is an algorithm for measuring the reliability of AI context.

It assigns a numerical reliability score to each source in a set of sources and a support score for each claim, with the purpose of estimating how much reliable, independent support that context contains.

<img src="research/figures/braid-example.png" alt="BRAID example" width="700">

*A simplified illustration of the BRAID algorithm, showing sources (red) and claims (blue). Node size represents perceived reliability or support. Directed edges represent assertions between sources and claims and bidirectional edges represent dependencies between sources.*

## How BRAID Works

BRAID evaluates context by recursively relating source reliability to claim support. The underlying assumption is that reliable sources are more likely to support well-supported claims.

A source is considered more reliable when it contributes claims that are themselves well supported by reliable sources. Likewise, claims in the context receive greater support when they are supported by reliable sources. The amount of support attributed is adjusted based on how independent its sources are.

These relationships are recursive: source reliability influences the support assigned to information in the context, while that support in turn influences source reliability. BRAID repeatedly propagates these scores through the context graph while accounting for dependencies among sources, until the scores converge.

### Context as a Graph

BRAID represents AI context as a finite bipartite graph

$$
G = (S, C, E)
$$

where:

- $S$ is the finite set of sources.
- $C$ is the finite set of claims.
- $E \subseteq S \times C$ is the set of assertions connecting sources to claims.

For a claim $j \in C$, let

$$
A(j) = \{i \in S : (i,j) \in E\}
$$

denote the set of sources asserting that claim.

For a source $i \in S$, let

$$
C(i) = \{j \in C : (i,j) \in E\}
$$

denote the set of claims asserted by that source.

For an attribute $a$, let

$$
C_a = \{j \in C : h(j) = a\}
$$

denote the set of claims associated with that attribute. This allows BRAID to distinguish competing claims about the same attribute.

BRAID assigns a reliability score $s_i$ to each source and a support score $c_j$ to each claim. Source scores are normalized across the context so that

$$
\sum_{i \in S} s_i = 1.
$$

Claim support is determined from the reliability of its supporting sources and adjusted according to their estimated independence.

## Algorithm

BRAID outputs a normalized score vector used to represent the relative reliability of sources within a given context. Each source is assigned a numerical reliability score, with the scores collectively normalized to sum to 1.

For example, suppose we have a small network of five sources. Each source is initialized with equal reliability, so they would receive a score of 0.2. BRAID then repeatedly updates these scores based on the claims supported by each source and the estimated independence of the sources supporting those claims.

BRAID also assigns a support score to each claim. A claim receives greater support when it is supported by sources with higher reliability and when those sources are estimated to be independent of one another.

The algorithm requires several passes, called iterations, through the
context graph. During each iteration, source reliability is propagated to the claims those sources support, and claim support is propagated back to the sources that support those claims. The process continues until the scores converge.

BRAID therefore works on the assumption that a claim supported by reliable and independent sources should receive greater support, while a source that consistently supports well-supported claims should receive greater reliability.

### Simplified Algorithm

Consider a context containing three sources supporting the same claim:

- Source A
- Source B
- Source C

BRAID initially assigns each source an equal reliability score:

$$
s_A = s_B = s_C = \frac{1}{3}
$$

Suppose Source B and Source C are partially dependent because they obtained their information from the same upstream source. Source A is independent of both.

BRAID first propagates each source's reliability to the claim. Because B and C are partially dependent, their contributions are discounted relative to the independent contribution from A.

The resulting claim support is then propagated back to the sources. A source whose contribution helps establish a well-supported claim receives greater reliability in the next iteration.

This process is repeated:

$$
\text{source reliability}
\rightarrow
\text{claim support}
\rightarrow
\text{source reliability}
\rightarrow \cdots
$$

until the scores converge.

This is a simplified illustration of BRAID's recursive propagation process. For the complete mathematical specification of BRAID, see the
[BRAID specification](spec/braid.md).

## Quick Start

Clone the repository:

```bash
git clone https://github.com/cole-h06/braid.git
cd braid
```

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest
```

BRAID includes generic synthetic fixtures that exercise the algorithm without tying it to a specific application domain.

For an applied example, see [`experiments/applied/agent_dataset/`](experiments/applied/agent_dataset/README.md). It evaluates BRAID on a controlled multi-agent workflow in which five specialized agents produce fifteen assertions.

## Repository Structure

- [`src/braid/`](src/braid/) — BRAID implementation.
- [`spec/`](spec/) — mathematical specification.
- [`tests/fixtures/`](tests/fixtures/README.md) — development and conformance data.
- [`experiments/algorithm/`](experiments/algorithm/README.md) — direct BRAID experiments.
- [`experiments/applied/`](experiments/applied/) — applied AI-context experiments.

## Citation

If you use BRAID in your research, please cite it using [`CITATION.cff`](CITATION.cff).

## License

BRAID is licensed under the [MIT License](LICENSE).