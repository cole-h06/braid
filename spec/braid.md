# BRAID

BRAID evaluates the reliability of a set of sources by propagating support through a source–claim graph.

A source makes assertions about attributes. Multiple sources may support the same claim, or different claims for the same attribute. BRAID accounts for both the amount of agreement and the dependence between supporting sources before propagating claim support back into source reliability.

The algorithm operates on a canonicalized graph. Semantic extraction and identity resolution happen before BRAID. The algorithm receives the canonicalized graph and its dependency metadata. URL normalization, serialization, and cryptographic operations are outside BRAID's scope.

## 1. Graph

BRAID operates on a finite bipartite graph

$$
G=(S,C,E)
$$

where $S$ is the set of sources, $C$ is the set of claims, and $E$ contains the source–claim assertions.

Each claim has an explicit attribute identity $h(j)$, which includes its entity context. Claims with the same attribute represent competing values. Each source may assert at most one claim for an attribute.

For a claim $j$, define its supporting sources as

$$
A(j)=\{i:(i,j)\in E\}.
$$

For a source $i$, define its claims as

$$
C(i)=\{j:(i,j)\in E\},
$$

with

$$
d_i=|C(i)|.
$$

For an attribute $a$, let

$$
C_a=\{j:h(j)=a\}.
$$

BRAID operates on the canonicalized graph and the dependency metadata supplied with it. It does not perform entity resolution or infer identities from claim content.

## 2. Agreement

Agreement measures how much of the available support for an attribute is concentrated on a particular claim.

For claim $j$, let

$$
P(j)=\bigcup_{\ell:h(\ell)=h(j)}A(\ell).
$$

The agreement weight of the claim is

$$
w_j=\frac{|A(j)|}{|P(j)|}.
$$

The same value is used for every source supporting that claim:

$$
w_{ij}=w_j.
$$

Agreement is computed directly from the graph. Sources are counted once, so duplicate assertions do not increase agreement. Because each source may assert at most one claim for an attribute, the agreement weights of competing claims for an attribute sum to one.

Agreement measures structural support, not factual correctness.

## 3. Source dependence

Agreement alone does not distinguish independent sources from sources that share evidence.

BRAID therefore estimates a dependency value

$$
\delta_{ik}\in[0,1]
$$

for each pair of sources. The matrix is symmetric and has a zero diagonal:

$$
\delta_{ik}=\delta_{ki},\qquad \delta_{ii}=0.
$$

The dependency estimate is derived from the metadata available for the source pair. The current signals are upstream lineage, citation, assertion lineage, ownership, temporal proximity, and retrieval overlap. Graph evidence is supported by the dependency combiner but is not automatically estimated in BRAID 1.0.0.

Missing metadata is treated as unavailable evidence, not evidence of independence.

## 4. Independent support

For each claim, BRAID converts the dependencies among its supporting sources into a claim-specific independence factor.

$$
q_{ij}
=
\frac{1}
{1+\sum_{k\in A(j),\,k\ne i}\delta_{ik}}.
$$

A claim with a single supporting source has

$$
q_{ij}=1.
$$

If the other sources supporting a claim are fully dependent on source $i$, the contribution from source $i$ is reduced accordingly.

The independence factor is applied to source contributions during the forward propagation step. It is not applied again during the reverse pass.

## 5. Dependency signals

The dependency estimate is based on the metadata available for each source pair. Each signal produces a value in $[0,1]$ together with an indication of whether the signal is observable.

### Upstream lineage

Let $U_i$ be the set of recorded upstream source identifiers for source $i$. The upstream signal is

$$
u_{ik}
=
\mathbf{1}
\left[
k\in U_i
\lor
i\in U_k
\lor
U_i\cap U_k\ne\varnothing
\right].
$$

A shared upstream origin is sufficient to establish the signal. Only recorded one-hop identities are used.

### Citation

The citation signal is

$$
c_{ik}
=
\mathbf{1}
\left[
i\text{ cites }k
\lor
k\text{ cites }i
\right].
$$

Citation relationships are treated as binary evidence; the number of citations does not increase the signal.

### Assertion lineage

The assertion-lineage signal is

$$
a_{ik}
=
\mathbf{1}
\left[
\text{an assertion from one source identifies an assertion from the other as a parent}
\right].
$$

Only the recorded parent relationships are used. BRAID does not infer additional ancestry.

### Ownership

The ownership signal is

$$
o_{ik}
=
\mathbf{1}
\left[
\text{both owners are known and equal}
\right].
$$

When ownership is unavailable, it does not provide evidence of independence.

If all asserting sources in the evaluation have the same known owner, ownership is excluded from dependency fusion and coverage for every pair. This exclusion depends on the evaluation population, not only on the individual pair.

### Temporal proximity

Let $J_{ik}$ be the set of attributes for which the two sources assert the same claim. For a finite temporal window $W>0$,

$$
t_{ik}
=
\frac{1}{|J_{ik}|}
\sum_{j\in J_{ik}}
\max
\left(
0,
1-\frac{|T_{ij}-T_{kj}|}{W}
\right).
$$

The temporal signal is observable only when the pair shares at least one attribute and both modification times are available for every matching attribute.

Equal timestamps produce a value of one. A separation equal to $W$ produces zero.

Observation time, retrieval time, and age relative to the present are not used by this signal. Temporal proximity is therefore not a freshness score.

### Graph evidence

Automatic dependency estimation does not infer a graph signal from overlap. The automatic value is

$$
g_{ik}=0.
$$

The graph signal remains available to the lower-level dependency combiner when explicitly supplied. Historical structural redundancy experiments are not part of the automatic estimator.

### Retrieval overlap

For each matching attribute $j$, let $R_{ij}$ be the set of resource-identifying pairs associated with source $i$'s assertion.

The retrieval signal is

$$
r_{ik}
=
\frac{1}{|J_{ik}|}
\sum_{j\in J_{ik}}
\mathbf{1}
\left[
R_{ij}\cap R_{kj}\ne\varnothing
\right].
$$

A matching attribute with at least one nonempty resource set makes the signal observable. Two empty resource sets do not.

Missing or empty resource collections remain part of the matching-attribute denominator.

## 6. Dependency fusion

Each dependency signal has a configured nonnegative weight. Let $\beta_r$ denote the weight for signal $r$, and define

$$
\alpha_r
=
\frac{\beta_r}{\sum_v\beta_v}.
$$

Signals that are unavailable are masked rather than treated as evidence of independence.

For each pair of sources, the available signals are combined according to their configured weights to produce

$$
\delta_{ik}\in[0,1].
$$

No renormalization is performed merely because a signal is unavailable. Coverage records which signals were observable for the pair.

The resulting dependency matrix is symmetric:

$$
\delta_{ik}=\delta_{ki}.
$$

## 7. Reliability propagation

BRAID begins with uniform source reliability:

$$
s_i^{(0)}=\frac{1}{|S|}.
$$

At iteration $t$, each source distributes its current reliability across the claims it supports:

$$
c_j^{(t)}
=
\sum_{i\in A(j)}
\frac{s_i^{(t)}w_jq_{ij}}{d_i}.
$$

The contribution from source $i$ therefore depends on its current reliability, the agreement supporting the claim, the estimated independence of that source from the other supporters, and the number of claims supported by the source.

## 8. Reverse propagation

Claim support is returned to the sources that assert those claims. For each attribute, support is normalized across its competing values:

$$
Z_a^{(t)}
=
\sum_{\ell\in C_a}c_\ell^{(t)}.
$$

A source receives support from each claim it asserts according to that claim's share of the total support for its attribute:

$$
\widetilde{s}_i^{(t+1)}
=
\sum_{\substack{j\in C(i)\\Z_{h(j)}^{(t)}>0}}
\frac{c_j^{(t)}}{Z_{h(j)}^{(t)}}.
$$

An attribute with zero total support contributes nothing.

The resulting source scores are normalized:

$$
s_i^{(t+1)}
=
\frac{\widetilde{s}_i^{(t+1)}}
{\sum_{k\in S}\widetilde{s}_k^{(t+1)}}.
$$

No additional source-degree normalization, damping, prior, or independence adjustment is applied during the reverse pass. The independence adjustment has already been applied through $q_{ij}$ in the forward pass.

## 9. Termination

After each complete update, BRAID measures the maximum change in source reliability:

$$
\Delta_t
=
\max_i
\left|
s_i^{(t+1)}-s_i^{(t)}
\right|.
$$

The iteration stops at the first

$$
\Delta_t<10^{-8}.
$$

Iteration numbering starts at one, and no more than 1,000 updates are permitted. Reaching the limit without satisfying the tolerance is considered nonconvergence. Nonfinite arithmetic is an inference failure.

The reference implementation uses binary64 arithmetic. Uniform initialization is part of the reference behavior. These numerical rules define the reference behavior, but they do not guarantee convergence for every graph.

## 10. Final evaluation

After convergence, BRAID recomputes claim support and individual source contributions using the final source reliability vector. The final claim scores are therefore derived from the converged source scores rather than from the claim vector produced before the final source update.

A successful evaluation records the algorithm version, iteration count, tolerance, final delta, and convergence status.

## 11. Interpretation

Source reliability scores sum to one across the evaluated source set. They represent relative reliability within that evaluation and are not probabilities that a source is truthful.

Claim scores represent support accumulated during the forward pass. They are not normalized per attribute and should not be interpreted as probabilities that a claim is true.

Agreement and dependency measure structural relationships in the supplied evidence graph. Neither is a direct measurement of factual correctness.

Results can depend on the set of sources and claims included in the evaluation, as well as claim volume and attribute partitioning. BRAID does not assume that adding unrelated claims leaves existing source scores unchanged, and the algorithm does not guarantee invariance across disconnected graph components.