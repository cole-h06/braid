## Mocked Hybrid Source-Dependency Experiment

Five deterministic agents produce fifteen assertions and separate evidence records. The fixture exercises explicit lineage, shared provenance, shared ownership, temporal copying, graph overlap, and independent conflicting evidence.

The experiment:

1. Validates source metadata, assertions, and evidence.
2. Builds exact claim nodes and property/value maps.
3. Derives provenance, lineage, ownership, temporal, and graph signals.
4. Combines the signals into a symmetric dependency matrix.
5. Runs dependency-adjusted credibility inference.

The baseline normalized weights are:

- Provenance: `0.25`
- Lineage: `0.30`
- Ownership: `0.15`
- Temporal: `0.15`
- Graph: `0.15`

These weights are an initial hand-selected baseline for the mocked experiment, not calibrated estimates. Alternative finite, non-negative configurations are normalized internally.

From the repository root, run:

```bash
.venv/bin/python -m agent_dataset.run
```

Run the experiment tests with:

```bash
.venv/bin/python -m pytest agent_dataset/tests -v
```
