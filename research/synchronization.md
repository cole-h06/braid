# BRAID synchronization baseline

BRAID 1.0.0 formalizes a one-time migration from committed Omneum
`af1ee33bee4fcaef845416541d4004c70494e8bc` (propagation `omneum-v2`,
estimator `dependency-estimator-v4`). The pre-migration BRAID HEAD was
`9bdc44c21020edd76468543c5c1e47f5590e8b2b`.
This records implemented behavior, not a claim of mathematical optimality.
Those two Omneum labels alone were insufficient to identify the complete semantics.

## Changes, in dependency order

1. Explicit attribute identity and valid binary graphs; distinct-source agreement.
2. Attribute-normalized reverse propagation; reciprocal summed-dependency
   claim independence (retaining the already-present protected research edit).
3. Uniform initialization, strict convergence tolerance, failure rather than
   partial results at the cap, and final forward recomputation.
4. Seven dependency signals: shared external upstreams, binary global direct
   relationships, capture masks, universal-owner exclusion, symmetric modification
   time decay, disabled automatic graph signal and resource-overlap retrieval.
5. Direct-evidence maximum versus contextual weighted sum, no missing-signal
   renormalization, and independent coverage.
6. Effective supporter counts, optional induced-subgraph clusters, contributions,
   conflicts and exact-tie maxima.

Historical structural-overlap code and notes remain exploratory. CSV graph
benchmarks lack provenance and explicitly use zero dependency and zero coverage;
overlap is not silently promoted to provenance. Agent examples retain explicit,
uncalibrated weights and a two-hour adapter default temporal window. Callers
must record the actual weights, window and optional threshold with evaluations.
The existing CSV adapter continues collapsing repeated rows into binary edges;
its agreement calculation now counts distinct sources. Catalog sources with
no selected assertions remain outside the active graph.

## Temporary migration evidence

A temporary comparator loads the pinned committed Python modules using
`git show`, not the working Omneum tree. No comparator or Omneum import is
part of BRAID's permanent test suite. Comparisons use relative tolerance
1e-12 and absolute tolerance 1e-14, with exact iteration counts and masks.

Initial comparison passed 200 seeded fusion cases, 100 seeded graph cases
(including five matching nonconvergence outcomes), eight frozen graph cases,
and both existing synthetic provenance datasets. The seed was 617.
Frozen graph outputs include singletons, unequal degrees, ties, disconnected
components, dependency discounting, nonconvergence and mixed synthetic graphs.
Eight hand-derived fusion cases and 18 provenance-boundary cases also pass
the pinned migration comparison. Three hand-derived clustering vectors
cover threshold equality, zero threshold and induced-supporter connectivity.
Passing these finite cases is not proof of equivalence on every graph.

Pinned source SHA-256 digests:
- inference.py: `f5bd4a1427184c66eb81ad61de660bfe275d158a86bb1d53c962a9d8de01065e`
- dependency.py: `f497844574ebf87cd3cb5736f2dcce24dd1d651d66b19d466bd9ff2464c6bf66`
- engine_graph.py: `f161a375a25abdf5742d5b33e7ac23c9b53d7b87da3952755874227e766bd4d8`

## Protected work and unresolved hypothesis

Validation of this patch:
- Independent conformance: 53 passed.
- Full repository pytest run: 118 passed, one failed (the protected test below).
- Explicitly deselecting that one test: 118 passed, one deselected.
- CSV benchmark: completed, converging after two updates.
- Protected test and two experiment files: byte-for-byte equal to pre-edit backups.
  Protected independence function: unchanged.
- Omneum and operator workspaces: no edits.
- Diff whitespace audit: no newly introduced whitespace errors; the protected
  engine's existing blank-line trailing whitespace is retained.

The full-suite failure is not suppressed in the repository.

The pre-existing `compute_independence` function is preserved. The protected
`agent_dataset/tests/test_inference.py`, `claim_volume.py` and
`propagation_topology.py` experiments/tests are not edited.

The protected `test_discount` assumes strict reduction of every shared
claim's converged support. It fails on shipping/free: synchronized reference
0.11111111099324643 versus zero-dependency 0.11111111095633869.
Pinned Omneum reproduces the same ordering (last-bit differences only).
This is not a translation mismatch. The assertion is not a specified invariant:
dependencies change source feedback as well as direct claim discounts.
Resolving this protected research hypothesis/test requires Cole's approval;
the migration neither hides it with an xfail nor changes the algorithm to pass it.

Convergence for all valid graphs, claim-volume/topology invariance, calibrated
weights and truth-probability interpretation remain research questions.
Identity equivalence is supplied by adapters; BRAID does not adopt Omneum URL,
SDK, crypto, packaging, resource-limit or presentation rules.

## Authority and release process

The BRAID specification, reference and frozen fixtures are normative together.
A disagreement among them is a BRAID defect to resolve explicitly, not
permission for a downstream implementation to pick its preferred behavior.

Downstream implementations must declare the BRAID algorithm version, exact
BRAID git revision and fixture revision, and retain configuration with results.
No self-referential git hash is embedded in the manifest: pin the actual
reviewed commit in downstream dependency/configuration metadata. Until the
migration is reviewed and committed, no new immutable revision is available.

Future changes begin here: preserve evidence, obtain a research decision,
update equations/reference/fixtures together, increment algorithm/fixture
versions as appropriate, commit, then port downstream and run the BRAID-owned
vectors. Never regenerate expected vectors merely to accommodate a failing
implementation. Old frozen vectors remain identifiable through git history.

External evaluations record observations, normalized inputs, both repository
revisions and configuration separately from normative fixtures. They may
motivate a later BRAID proposal; they do not silently amend this baseline.
Omneum's downstream pin and fixture consumer are intentionally not changed
during this BRAID-only migration.

## Changed-file map

| Area | Files |
|---|---|
| Normative specification | `research/reliability_propagation.md`, `research/agreement_weighting.md`, `research/source_dependency_estimation.md`, `research/dependency_telemetry.md` |
| Authority, version and evidence | `research/algorithm.json`, `research/README.md`, `research/synchronization.md` |
| Reference | `braid/engine.py` (outside the protected independence function), `braid/graph.py`, new `braid/dependency.py` |
| CSV integration | `braid/loader.py`, `braid/source_dependency.py`, `run_benchmark.py` |
| Agent adapters | `agent_dataset/dataset.py`, `agent_dataset/run.py`, `agent_dataset/workflow/graph.py`, `agent_dataset/workflow/hybrid_dependency.py`, `agent_dataset/workflow/pipeline.py` |
| Existing tests updated | `agent_dataset/tests/test_dataset.py`, `agent_dataset/tests/test_hybrid_dependency.py`, `agent_dataset/tests/test_enterprise_dependency.py` |
| Independent conformance | `agent_dataset/tests/test_spec_conformance.py`, `agent_dataset/tests/fixtures/braid_sync_v1.json`, `agent_dataset/tests/fixtures/braid_dependency_v1.json`, `agent_dataset/tests/fixtures/README.md` |
| Documentation and historical labeling | `README.md`, `agent_dataset/README.md`, `benchmark/README.md`, `research/structural_source_dependencies.md` |

The pre-existing modified inference test and untracked topology/volume
experiments are not migration changes. No files have been staged or committed.
