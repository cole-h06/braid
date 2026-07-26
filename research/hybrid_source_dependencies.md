# Hybrid Source Dependency Estimation

## Motivation

The previous structural source dependency investigation showed that useful relationship signals can, in fact, be derived directly from the source-claim graph. The experiments that tested directional inclusion asymmetry, rarity weighted overlap, and community structure each contain structural signals of how sources relate to each other.

However, that said, I have observed that these graph-derived signals are incapable of estimating source dependencies accurately alone. The graph can ultimately only capture the observed pattern of shared assertions. It does not provide any information as to how those assertions originated, if they were copied, if they share a common owner, or if they were simply independently produced.

This motivated me to look into a hybrid approach that combines structural graph signals with provenance and metadata. It doesn't replace the information contained within the graph. Instead, these additional signals can provide complementary evidence which may enable source dependencies to be estimated more reliably and actively.

## Research Question

Can source dependencies be estimated more reliably through combining structural graph signals with provenance and metadata rather than just using graph topology alone?

## Hypothesis

Complementary information can be provided by combining structural graph signals and provenance regarding relationships between sources. I believe that combining both forms of "evidence" within a hybrid framework could lead to more accurate estimation of source dependencies than either could alone.

## Mathematical Framework

In order to formalize this hybrid approach, let $d_{ik}$ denote the estimated dependency between sources $i$ and $k$. Specifically, let

$$ d_{ik} = \alpha_1 p_{ik} + \alpha_2 l_{ik} + \alpha_3 o_{ik} + \alpha_4 t_{ik} + \alpha_5 g_{ik} $$

where

- $p_{ik}$ represents shared provenance,
- $l_{ik}$ represents explicit lineage or citation relationships,
- $o_{ik}$ represents shared ownership,
- $t_{ik}$ represents temporal copying evidence, and
- $g_{ik}$ represents graph-derived structural signals.

The coefficients $\alpha_1,\ldots,\alpha_5$ determine the relative contribution of each signal toward the estimated dependency. Determining appropriate values for these coefficients is itself a research problem and is left for future experiments.

The estimated dependency is constrained to the interval

$$
0 \le d_{ik} \le 1
$$

where a value of $0$ represents complete independence and a value of $1$ represents complete dependency.

In correspondence, the estimated independence between sources is defined as

$$
q_{ik} = 1 - d_{ik}
$$

Collectively, the pairwise dependency estimates form the dependency matrix

$$
D \in [0,1]^{|S| \times |S|}
$$

where each entry represents the estimated dependency between a pair of sources. This matrix sets the foundation for incorporating dependency information into the credibility inference process. It can allow corroboration to be adjusted according to each contributing source's estimated independence.
