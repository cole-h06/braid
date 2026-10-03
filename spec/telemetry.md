# Telemetry

BRAID reports several quantities alongside the source and claim scores. These
describe the evidence used during an evaluation and provide ways to inspect
the result. They are diagnostics, not probabilities of truth.

## Effective independent support

For a claim \(j\), let \(A(j)\) be its set of supporting sources and let
\(n_j=|A(j)|\).

BRAID estimates the amount of independent support as

\[
n_{\mathrm{eff}}(j)=
\frac{n_j^2}
{n_j+2\sum_{\{i,k\}\subseteq A(j)}\delta_{ik}}.
\]

A claim supported by one source has an effective support of one. With no
dependency between the supporting sources, the value is \(n_j\). If every
pair of supporting sources is fully dependent, the value is one.

This quantity is derived from the same pairwise dependencies used by the
inference algorithm. It is a diagnostic and does not modify the propagation
itself.

It should not be confused with

\[
\sum_i q_{ij},
\]

which is calculated from the claim-specific independence factors.

## Dependency coverage

For claims with more than one supporting source, BRAID reports the average
coverage of the dependency signals available for the supporting pairs.

\[
\overline{\gamma}_j=
\binom{n_j}{2}^{-1}
\sum_{\{i,k\}\subseteq A(j)}
\gamma_{ik}.
\]

For a singleton claim there are no source pairs, so this value is null.

The legacy field name `dependency_confidence` is an alias for
`dependency_signal_coverage`. It does not represent statistical confidence.

## Dependency clusters

BRAID can also group sources according to their pairwise dependency.

Given an explicitly supplied threshold

\[
\tau\in[0,1],
\]

two sources are connected when

\[
\delta_{ik}\geq\tau.
\]

The resulting clusters are the connected components of this graph. Isolated
sources are included as single-vertex components.

Connectivity is transitive. Two sources therefore belong to the same cluster
if they are connected by a path, even when their pairwise dependency is below
the threshold. A clique is not required.

At \(\tau=0\), every pair of sources is connected, including pairs with zero
dependency.

For claim-level telemetry, the graph is restricted to the sources supporting
that claim before the components are calculated. A path through a source that
does not support the claim cannot merge two claim supporters.

The threshold is not part of the BRAID inference algorithm. Clustering does
not change source scores, claim scores, or effective independent support. If
no threshold is supplied, claim-level cluster information is null.

## Claim diagnostics

BRAID can report the contribution made by each supporting source to a claim.
The contribution from source \(i\) to claim \(j\) is

\[
\frac{s_iw_jq_{ij}}{d_i}.
\]

These contributions are recomputed using the final source reliability vector.

For each attribute, BRAID also reports the competing claims and their
computed support. A claim is maximal when its support equals the largest
support among the claims for that attribute.

If several claims have exactly the same maximum support, all of them are
maximal. BRAID does not use a tolerance to turn near-equal values into ties
and does not select a single winner from an exact tie.

## What is not part of the telemetry contract

The telemetry contract does not define how results are displayed to users.

Sorting, explanation text, recommendation thresholds, provenance-trace
formatting, and aggregate service-level metrics are outside this contract.

The reference implementation also retains some older directional relationship
diagnostics for research inspection. The `temporal_directions` field refers
to the symmetric temporal-proximity signal; it does not represent causal
direction.