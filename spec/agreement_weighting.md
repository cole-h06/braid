# Agreement Weighting

Normative for **BRAID 1.0.0**.

For claim \(j\), let \(A(j)\) be its distinct asserting sources and
\(P(j)=\bigcup_{\ell:h(\ell)=h(j)}A(\ell)\). Define
\[
w_j=|A(j)|/|P(j)|,\qquad w_{ij}=w_j.
\]

Agreement is always computed from the graph, not supplied as a tunable edge
weight. Each source has at most one claim per attribute, so competing weights
sum to one. Duplicates must not inflate counts. Attribute identity includes
entity context.

The forward contribution is \(s_iw_jq_{ij}/d_i\). The reverse pass uses
attribute-normalized support, without multiplying by agreement again.

For three agreeing sources and one dissenting source on a sole attribute,
uniform initial reliability and zero dependency give first-pass supports
\(9/16\) and \(1/16\). These are not converged values.

Agreement is not factual correctness. Historical hand-built graphs lacking
attribute mappings cannot be interpreted by guessing from claim names or
previously supplied weights.
