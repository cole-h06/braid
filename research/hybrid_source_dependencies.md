# Hybrid Source Dependency Estimation

## Motivation

The previous structural source dependency investigation showed that useful relationship signals can, in fact, be derived directly from the source-claim graph. The experiments that tested directional inclusion asymmetry, rarity weighted overlap, and community structure each contain structural signals of how sources relate to each other.

However, that said, I have observed that these graph-derived signals are incapable of estimating source dependencies accurately alone. The graph can ultimately only capture the observed pattern of shared assertions. It does not provide any information as to how those assertions originated, if they were copied, if they share a common owner, or if they were simply independently produced.

This motivated me to look into a hybrid approach that combines structural graph signals with provenance and metadata. It doesn't replace the information contained within the graph. Instead, these additional signals can provide complementary evidence which may enable source dependencies to be estimated more reliably and accurately.

## Research Question

Can source dependencies be estimated more reliably through combining structural graph signals with provenance and metadata rather than just using graph topology alone?

## Hypothesis

Complementary information can be provided by combining structural graph signals and provenance regarding relationships between sources. I believe that combining both forms of "evidence" within a hybrid framework could lead to more accurate estimation of source dependencies than either could alone.

## Mathematical Framework

In order to formalize this hybrid approach, let $\delta_{ik}$ denote the estimated dependency between sources $i$ and $k$. Specifically, let

$$ \delta_{ik} = \alpha_1 p_{ik} + \alpha_2 l_{ik} + \alpha_3 o_{ik} + \alpha_4 t_{ik} + \alpha_5 g_{ik} $$

where

- $p_{ik}$ represents shared provenance,
- $l_{ik}$ represents explicit lineage or citation relationships,
- $o_{ik}$ represents shared ownership,
- $t_{ik}$ represents temporal copying evidence, and
- $g_{ik}$ represents graph-derived structural signals.

The coefficients $\alpha_1,\ldots,\alpha_5$ determine the relative contribution of each signal toward the estimated dependency. Determining appropriate values for these coefficients is itself a research problem and is left for future experiments.

The signal weights are normalized so that

$$
\sum_{r=1}^{5}\alpha_r=1.
$$

When a signal is unavailable, its contribution to $\delta_{ik}$ is defined as $0$. The remaining weights are not renormalized. We do this to prevent missing metadata from increasing the influence of remaining signals. Dependency confidence separately reports how much of the weighted signal set was observable.

The estimated dependency is constrained to the interval

$$
0 \le \delta_{ik} \le 1
$$

where a value of $0$ represents no estimated dependency under the available signals and a value of $1$ represents maximum estimated dependency under the model.

In correspondence, the estimated independence between sources is defined as

$$
q_{ik} = 1 - \delta_{ik}
$$

Collectively, the pairwise dependency estimates form the dependency matrix

$$
D \in [0,1]^{|S| \times |S|}
$$

where each entry represents the estimated dependency between a pair of sources. This matrix sets the foundation for adjusting credibility propagation and calculating claim-level dependency telemetry. It can allow corroboration to be adjusted according to each contributing source's estimated independence.

The current framework treats dependency as symmetric, such that

$$
\delta_{ik} = \delta_{ki}
$$

and defines each diagonal entry as

$$
\delta_{ii} = 0.
$$

## Claim-Specific Independence

For each source $i$ asserting claim $j$, independence is calculated relative to the other sources asserting the same claim.

$$
q_{ij} = 1 - \frac{\sum_{k \in A(j),\, k \neq i} \delta_{ik}}{a(j)-1}
$$

where

- $A(j)$ is the set of sources asserting claim $j$,
- $a(j)=|A(j)|$ is the number of sources asserting claim $j$,
- $\delta_{ik}$ is the estimated dependency between sources $i$ and $k$.

If source $i$ is the only source asserting claim $j$, then

$$
q_{ij}=1
$$

The dependency matrix is global to each source pair, not specific to any individual claim. Claim-specific independence applies those global source dependencies to the subset of sources supporting claim $j$. Therefore, a relationship observed elsewhere between two sources may affect every claim they both support. A possible extension of this framework could involve claim-specific dependency estimation.

## Dependency-Adjusted Claim Support

We incorporate the claim-specific independence score into source-to-claim propagation:

$$
c_j^{(t)} = \sum_{i \in A(j)} \frac{s_i^{(t)} w_{ij} q_{ij}}{d_i}
$$

where

- $s_i^{(t)}$ is the credibility of source $i$ at iteration $t$,
- $w_{ij}$ is the agreement weight for source $i$'s assertion of claim $j$,
- $q_{ij}$ is the independence of source $i$ for claim $j$, and
- $d_i$ is the number of claims asserted by source $i$.

Dependent sources are discounted through this adjustment and independent corroboration receives greater influence.

## Claim-Level Dependency Telemetry

The dependency matrix can also be used to summarize the structure of the evidence supporting a claim. The supporting-source count comes from the source-claim graph, whereas the estimated independent support count and dependency clusters are derived from the pairwise dependencies among those sources. We calculate dependency confidence separately from the available signals used to estimate those dependencies.

Let $n_j = |A(j)|$ denote the number of sources supporting claim $j$. 

This is reported as `supporting_source_count`.

### Estimated Independent Support

The independence of evidence is not immediately obvious based on the number of supporting sources. Therefore, we define the following effective-support heuristic:

$$ \hat{n}_j = \frac{n_j^2}{n_j + 2\sum_{i<k,\;i,k\in A(j)}\delta_{ik}} $$

where the sum includes every unordered source pair supporting claim $j$.

When all supporting sources are estimated to be independent, $\hat{n}_j=n_j$. When they are completely dependent, $\hat{n}_j=1$. When there is partial dependency, it is a value between these bounds.

This value is reported as `estimated_independent_support_count`.

This is essentially pairwise dependency represented as an effective amount of support. It is not a literal count of independently verified origins, nor is it derived directly from the propagation equation.

### Dependency Clusters

Dependency clusters represent an estimated number of threshold-connected groups among the sources supporting a claim.

For each claim $j$, construct a graph containing the sources in $A(j)$. An edge is added between sources $i$ and $k$ when

$$
\delta_{ik} \ge \tau
$$

where $\tau$ is an explicit dependency threshold. The number of connected components in this graph defines

$$
K_j
$$

which is reported as `dependency_clusters`.

Either directly or transitively, sources connected by dependencies that meet the threshold belong to the same component. Therefore, two sources can belong to the same cluster even when their own pairwise dependency is below $\tau$.

No default threshold is selected. Its final value remains an experimental decision that should be informed by sensitivity analysis. Once selected, the threshold must be versioned and applied consistently.

### Dependency Confidence

We can describe dependency confidence based on how much observable evidence was available at the time when estimating the pairwise dependencies. It is weighted signal coverage, not the probability that the estimate is correct.

For each dependency signal $r$, let

$$
m_{ik}^{(r)} =
\begin{cases}
1, & \text{if the signal was observable for sources } i \text{ and } k \\
0, & \text{if the signal was unavailable}
\end{cases}
$$

It is important that an observable signal with a value of $0$ must be distinguishable from a signal that's unavailable. If there is a value of $0$, it means that the signal was analyzed but no evidence of dependency was provided. An unavailable signal, on the other hand, means that the required metadata was not present.

For raw provenance and lineage fields, `None` means that metadata was unavailable or was not captured. An empty tuple means capture was completed without finding a relationship, and a nonempty tuple contains the observed relationships. Computed observability remains separate from the raw records.

The confidence associated with a pairwise dependency estimate is

$$
\gamma_{ik} = \frac{\sum_{r=1}^{5}\alpha_r m_{ik}^{(r)}}{\sum_{r=1}^{5}\alpha_r}$$

We then calculate claim-level dependency confidence across the source pairs supporting claim $j$:

$$ \gamma_j = \frac{2}{n_j(n_j-1)} \sum_{i<k} \gamma_{ik} $$ where the sum includes every unordered pair of sources $i,k\in A(j)$.

This value is reported as `dependency_confidence`.

Suppose a claim has only one supporting source. Its supporting and estimated independent source counts are both $1$, and the source forms one dependency cluster. Dependency confidence is undefined because no pairwise dependency was estimated and is therefore reported as `null`.

When combined, a hypothetical telemetry result could be:

```json
{
  "supporting_source_count": 4,
  "estimated_independent_support_count": 2.0,
  "dependency_clusters": 2,
  "dependency_confidence": 0.86
}
```

These values define the estimated structure of the evidence supporting a claim. They do not, however, replace the dependency-adjusted propagation calculation.
