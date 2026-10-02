# Source Dependency Estimation

Normative for **BRAID 1.0.0**. The historical six-signal weighted sum and
mean-dependency claim discount are superseded.

## Records and scope

Every source has assertions, with exactly one evidence record per assertion.
Source, assertion, attribute and claim identities/equality are supplied by the
caller. Ownership and provenance may be unavailable.

For relationship fields, null means unavailable; empty means captured absence.
Upstream IDs may refer to external nonasserting sources; citations and parents
must resolve inside the input. Self-upstream, self-citation and parents
belonging to the same source are invalid. No transitive expansion, cycle solver
or matching-claim requirement for citation/parent links is applied.

Dependency is global per source pair:
\(\delta_{ik}=\delta_{ki}\), \(\delta_{ii}=0\).
Evidence elsewhere can affect every claim that pair supports.

## Signal definitions

Fixed signal order: upstream, citation, assertion_lineage, ownership, temporal,
graph, retrieval. Each value \(x_r\in[0,1]\) has mask \(m_r\in\{0,1\}\).
Let \(F_i^r\) mean field \(r\) is non-null on every assertion of source \(i\).

### Upstream

Let \(U_i\) be the union of recorded upstream IDs for source \(i\).
\[
u_{ik}=\mathbf1[k\in U_i\lor i\in U_k\lor U_i\cap U_k\ne\varnothing],
\quad m_u=\mathbf1[u_{ik}>0\lor(F_i^u\land F_k^u)].
\]
A shared external origin suffices; only recorded one-hop identities are used.

### Citation and assertion lineage

\[
c_{ik}=\mathbf1[i\text{ cites }k\lor k\text{ cites }i],
\quad
a_{ik}=\mathbf1[\text{any recorded parent belongs to the other source}].
\]
For either, \(m_r=\mathbf1[x_r>0\lor(F_i^r\land F_k^r)]\).
Relationship counts do not attenuate the binary signal.

### Ownership

\[
o_{ik}=\mathbf1[\text{both owners known and equal}],\qquad
m_o=\mathbf1[\text{both owners known}].
\]
If all asserting sources have the same known owner, exclude ownership from
fusion AND coverage for every pair. Raw value and mask remain reportable.
Partial capture does not trigger exclusion. This is evaluation-population
dependent, not solely pair-local.

### Temporal proximity

Let \(J_{ik}\) be the attributes where the pair asserts the same claim.
For finite \(W>0\) seconds:
\[
m_t=\mathbf1[J_{ik}\ne\varnothing\land
\text{both modification times present on every matching attribute}],
\]
\[
t_{ik}=
\begin{cases}
|J_{ik}|^{-1}\sum_{j\in J_{ik}}\max(0,1-|T_{ij}-T_{kj}|/W),&m_t=1,\\
0,&m_t=0.
\end{cases}
\]
Equal times give one, separation exactly \(W\) gives zero. One missing matching
timestamp disables the whole signal. Missing nonmatching timestamps do not.
Times must be timezone-aware. Observation time, retrieval time and age relative
to the present are not used: this is not a freshness score.

### Graph

Automatic estimation sets \(g_{ik}=0,m_g=0\), regardless of overlap.
Its configured weight remains in the denominator. Historical structural
redundancy is exploratory only. The lower-level combiner accepts an explicitly
supplied graph signal but defines no alternative automatic graph estimator.

### Retrieval

Let \(R_{ij}\) be the set of (kind, resource identity) pairs for source \(i\)'s
assertion on matching attribute \(j\).
\[
r_{ik}=
\begin{cases}
|J_{ik}|^{-1}\sum_{j\in J_{ik}}\mathbf1[R_{ij}\cap R_{kj}\ne\varnothing],
&J_{ik}\ne\varnothing,\\0,&\text{otherwise},
\end{cases}
\]
\[
m_r=\mathbf1[J_{ik}\ne\varnothing\land
\exists j\in J_{ik}:R_{ij}\cup R_{kj}\ne\varnothing].
\]
One-sided nonempty data establishes observability; two empty collections do
not. Missing/empty collections still count in the matching-attribute denominator.
Event IDs, retrieval times and arbitrary fields do not affect resource equality.

## Fusion and coverage

Finite nonnegative weights \(\beta_r\) have positive finite sum.
\(\alpha_r=\beta_r/\sum_v\beta_v\). The six original weights are required;
omitted retrieval weight means zero. No calibrated weights or temporal-window
default are normative; research examples explicitly configure them.

Let \(e_r=0\) for excluded signals and one otherwise, and \(D=\{u,c,a\}\).
\[
\gamma_{ik}=\sum_r\alpha_rm_re_r,
\]
\[
d_{ik}=\max(\{x_r:r\in D,\ m_re_r=1,\ \alpha_r>0\}\cup\{0\}),\qquad
b_{ik}=\sum_{r\notin D}\alpha_rm_re_rx_r,
\]
\[
\delta_{ik}=
\begin{cases}0,&\gamma_{ik}=0,\\
\min(1,\max(0,d_{ik},b_{ik})),&\gamma_{ik}>0.
\end{cases}
\]

No available-signal renormalization occurs. Positive direct weights enable,
rather than attenuate, direct evidence; zero disables it. Contextual signals
accumulate using normalized configured weights. Coverage is not probability
of correctness. The combiner masks unobservable supplied values.

## Claim independence

\[
q_{ij}=\frac1{1+\sum_{k\in A(j),\,k\ne i}\delta_{ik}}.
\]
Singletons have one; \(n\) fully dependent supporters each have \(1/n\).
This is not the pairwise complement \(1-\delta_{ik}\). Its sum is not generally
the effective support count. Forward support is \(\sum_i s_iw_jq_{ij}/d_i\).

See [Dependency Telemetry](dependency_telemetry.md). Claim-specific pair
estimation, arbitrary metadata interpretation and per-observation externally
supplied signal aggregation are not part of this version.
