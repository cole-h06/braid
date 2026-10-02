# Direct BRAID experiments

These nine synthetic research scripts were moved unchanged from
`braid/experiments/validation/`. From the repository root, run for example:

```bash
PYTHONPATH=src python -m experiments.algorithm.single_source
```

All nine currently fail with `ValueError: every claim requires an explicit attribute
identity`. Their graph stubs predate the explicit attribute-identity contract.
This reorganization deliberately preserves those failures, including the protected
`claim_volume.py` and `propagation_topology.py` experiments.

Use [repository conformance](../../tests/test_spec_conformance.py) and the
[canonical frozen fixtures](../../tests/fixtures/README.md) to validate the reference:

```bash
python -m pytest tests/test_spec_conformance.py
```
