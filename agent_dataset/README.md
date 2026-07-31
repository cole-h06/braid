## Mocked Agent Dataset

This experiment displays how Verity integrates into a multi-agent workflow.

Five specialized agents return fifteen assertions. Each assertion has a separate evidence record that stores the metadata used to test source dependency.

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

## LangGraph Workflow

The same five agents are also capable of running through LangGraph. They run in parallel, then their results are collected in a fixed order before validation, graph construction, hybrid dependency estimation, and inference.

There is no LLM or external retrieval involved. It produces the same result as the sequential experiment.

Open Python from the repository root:

```bash
.venv/bin/python
```

Then run:

```python
from agent_dataset.workflow.pipeline import run_workflow

result = run_workflow(
    debug=True,
)

print(result)
```Open Python from the repository root:

```bash
.venv/bin/python
```

Then run:

```python
from agent_dataset.workflow.pipeline import run_workflow

result = run_workflow(
    debug=True,
)

print(result)
```

## Enterprise Retrieval

The separate [enterprise experiment](enterprise/README.md) retrieves synthetic business facts through local documents, SQLite, and a vendor API snapshot before running the same dependency and inference code.
