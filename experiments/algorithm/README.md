# Direct BRAID Experiments

This directory contains experiments for studying BRAID behavior under different graph structures.

Each script focuses on a specific aspect of the algorithm.

Run an experiment from the repository root:

```bash
PYTHONPATH=src python -m experiments.algorithm.single_source
```

The reference implementation is in [`src/braid/`](../../src/braid/), with development and conformance fixtures in [`tests/fixtures/`](../../tests/fixtures/README.md).