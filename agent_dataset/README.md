## Mocked Agent Dataset

This experiment displays how BRAID integrates into a multi-agent workflow.

Five specialized agents return fifteen assertions. Each assertion has a separate evidence record that stores the metadata used to test source dependency.

In this dataset, there are examples of:

- upstream source relationships;
- explicit citations;
- assertion lineage;
- shared ownership;
- close publication timing;
- structural assertion overlap;
- independent conflicting information.

BRAID combines these signals to form a pairwise dependency matrix, which is then used by the reliability propagation algorithm. This is to reduce the influence of dependent support.

## Baseline Weights

```text
upstream             0.25
citation             0.20
assertion_lineage    0.20
ownership            0.10
temporal             0.10
graph                0.15
```

Note that these starting weights have been hand-tuned. They have not been calibrated against labeled source-dependency data.

Run the experiment from the repository root:

```bash
python3 -m agent_dataset.run
```

Run the tests:

```bash
python3 -m pytest agent_dataset/tests -v
```

## LangGraph Workflow

The same five agents are also capable of running through LangGraph. They run in parallel, then their results are collected in a fixed order before validation, graph construction, dependency estimation, and assertion evaluation.

There is no LLM or external retrieval involved. The workflow produces the same result as the sequential experiment.

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
```

## Enterprise Retrieval

The separate [enterprise experiment](enterprise/README.md) retrieves synthetic business facts through local documents, SQLite, and a vendor API snapshot before running the same dependency and evaluation code.
