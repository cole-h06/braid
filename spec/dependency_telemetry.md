# Dependency Telemetry

Normative for **BRAID 1.0.0**. These quantities describe the algorithm's
inputs and results, not probabilities of truth.

For claim \(j\), let \(A(j)\) contain its \(n_j\) supporting sources.
Using the same global pair estimates as propagation:

\[
n_{\mathrm{eff}}(j)=
\frac{n_j^2}{n_j+2\sum_{\{i,k\}\subseteq A(j)}\delta_{ik}}.
\]

For a singleton this equals one; for all-zero pair dependence it equals \(n_j\);
for all-one pair dependence it equals one. In general it is not
\(\sum_i q_{ij}\). It is a diagnostic, not an extra inference multiplier.

When \(n_j>1\), dependency signal coverage is

\[
\overline\gamma_j=
\binom{n_j}{2}^{-1}\sum_{\{i,k\}\subseteq A(j)}\gamma_{ik}.
\]

For singletons it is undefined (null), not one or zero. The reference's legacy
`dependency_confidence` name is an alias of
`dependency_signal_coverage`, not statistical confidence.

## Optional clusters

For explicitly supplied finite \(\tau\in[0,1]\), connect distinct sources
when \(\delta_{ik}\geq\tau\). Return connected components, including isolated
vertices. Connectivity is transitive; no clique requirement applies. At zero
threshold, even zero-dependency pairs connect.

For claim telemetry, restrict vertices to \(A(j)\) **before** computing
components. Paths through non-supporters do not merge claim clusters.
The same operation on all sources defines graph-level clusters.
No threshold is implied by the algorithm. Without one, claim cluster count
and membership are null; clustering does not change scores or effective counts.

## Final claim diagnostics

Contribution from source \(i\) is \(s_iw_jq_{ij}/d_i\), recomputed with the final
source vector. Conflicts are all distinct claims with the same attribute.
A claim is maximal iff its computed support equals the largest computed support
on its attribute. Every exact tie is maximal; there is no tolerance-based
tie merging or uniquely selected winner.

Neither sorting for presentation, explanation templates, recommendation
thresholds, provenance trace formatting nor aggregate service telemetry belongs
to this mathematical contract. The reference keeps legacy directional
relationship diagnostics for research inspection; `temporal_directions`
now contains the symmetric proximity signal, not causal direction.
