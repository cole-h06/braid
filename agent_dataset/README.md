## Mocked Hybrid Source-Dependency Experiment

This experiment displays how Verity integrates into a multi-agent workflow.

Five specialized agents independently return fifteen assertions. In each assertion, you can find a separate evidence record that stores the metadata used to test source dependency.

The dataset includes examples of:

- explicit lineage;
- shared provenance;
- shared ownership;
- close publication timing;
- structural assertion overlap;
- independent conflicting evidence.

The credibility inference engine uses the pairwise dependency matrix which is computed by combining these signals.

## Baseline Weights

```text
provenance    0.25
lineage       0.30
ownership     0.15
temporal      0.15
structure     0.15
```

Note that these starting weights have been hand-tuned. They have not been calibrated against real dependency data.

Run the experiment from the repository root:

```bash
.venv/bin/python -m agent_dataset.run
```

Run its tests:

```bash
.venv/bin/python -m pytest agent_dataset/tests -v
```
