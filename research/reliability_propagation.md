# Reliability Propagation

Normative for **BRAID 1.0.0**, the synchronization baseline. This specifies
behavior, not optimality or a probability-of-truth model.

## Input graph

Let \(G=(S,C,E)\) be a finite, nonempty binary source–claim graph. Every source
and claim participates in an edge. Each claim has one explicit attribute
identity \(h(j)\), including its entity context. Each source asserts at most
one claim per attribute. Duplicate assertions, inconsistent adjacency maps,
and missing attribute identities are invalid.

Write \(A(j)=\{i:(i,j)\in E\}\), \(C(i)=\{j:(i,j)\in E\}\),
\(d_i=|C(i)|\), and \(C_a=\{j:h(j)=a\}\). Identities are already normalized:
semantic extraction, URL rules, serialization and cryptography are outside BRAID.
Distinct claims sharing an attribute are competing values.

Dependency is a complete symmetric matrix with zero diagonal and entries in
\([0,1]\). Pair coverage is a separate symmetric matrix in \([0,1]\),
also represented with a zero diagonal.
Empty dependency/coverage dictionaries in the reference explicitly abbreviate
all-zero matrices, not verified independence. Partial nonempty matrices are invalid.

## Initialization and forward pass

\[
s_i^{(0)}=\frac1{|S|},\qquad
c_j^{(t)}=\sum_{i\in A(j)}\frac{s_i^{(t)}w_jq_{ij}}{d_i}.
\]

Agreement \(w_j\) is defined in [Agreement Weighting](agreement_weighting.md).
The fixed discount \(q_{ij}\) is defined in
[Source Dependency Estimation](source_dependency_estimation.md).
The individual contribution is the summand. Degree counts distinct claims.

## Attribute-normalized reverse pass

\[
Z_a^{(t)}=\sum_{\ell\in C_a}c_\ell^{(t)},\qquad
\widetilde s_i^{(t+1)}
=\sum_{\substack{j\in C(i)\\Z_{h(j)}^{(t)}>0}}
\frac{c_j^{(t)}}{Z_{h(j)}^{(t)}}.
\]

An attribute with exactly zero total contributes nothing. No source-degree
division, supporter-count division, damping, prior, or independence factor is
applied in this reverse pass.

\[
s_i^{(t+1)}=\frac{\widetilde s_i^{(t+1)}}
{\sum_{k\in S}\widetilde s_k^{(t+1)}}.
\]

A zero normalization total is an inference failure. This supersedes the
historical raw reverse sum \(\sum_{j\in C(i)}c_j\); that equation is not an
implicit alternative current mode.

## Termination and numerical contract

Use binary64 arithmetic and uniform initialization. After each full update:
\[
\Delta_t=\max_i|s_i^{(t+1)}-s_i^{(t)}|.
\]
Stop at the first \(\Delta_t<10^{-8}\), with iteration numbering starting at
one. At most 1,000 updates are permitted. Exceeding the cap is nonconvergence,
not a successful partial result. Nonfinite arithmetic is an inference failure.
These rules do not promise convergence for every valid graph.

Recompute final support and contributions from the final source vector; do not
return the pre-update claim vector as final support. Successful metadata records
version, iterations, tolerance, final delta and convergence. Reference history
pairs each new source vector with the claim vector that produced it.

The reference traverses sorted sources, attributes and claims. Fixtures use
string identities and prescribe numeric comparison tolerances. Research tuple
and integer identities must be consistently orderable. Display order is not
normative.

## Interpretation and limitations

Source scores sum to one. Returned forward claim scores are not normalized per
attribute and are not truth probabilities. Uncontested positive-support
attributes return one unit to each asserting source: with only uncontested
attributes, reverse reliability is proportional to source degree. Claim volume,
attribute partitioning and evaluation population can affect results. No
invariance to unrelated claims or disconnected components is promised.
