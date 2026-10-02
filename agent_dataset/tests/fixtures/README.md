# BRAID-owned conformance vectors

These frozen inputs and expected outputs belong to BRAID 1.0.0, fixture
revision 1. Consumers need only these JSON files and the BRAID specification;
no Omneum checkout, package or executable is needed.

- `braid_sync_v1.json`: normalized assertion triples, complete pair matrices
  (an empty object explicitly abbreviates zero), expected propagation outputs,
  lower-level signal fusion and clustering.
- `braid_dependency_v1.json`: synthetic provenance records and expected
  source-pair a/b signals, masks, dependency, coverage and exclusions.

String identities in the vectors are already normalized. Compare floats using
the declared absolute/relative tolerances, integers and masks exactly, and
cluster members as sets of sets. All exact score ties are maxima. No
presentation order or product-specific identifiers are prescribed.

The migration comparison is documented in
`research/synchronization.md`. Expected graph outputs were frozen after
cross-checking the pinned migration baseline against the reference. Signal
boundary and fusion expectations also follow directly from the equations.
Do not automatically regenerate expectations from the reference under test.

Downstream implementations must pin the BRAID git revision, algorithm version
and fixture revision, adapt these inputs without inventing provenance, and
compare their results against these expected values. Omneum is a consumer,
never a runtime oracle for BRAID.
