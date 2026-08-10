## Enterprise Retrieval Experiment

This experiment displays how BRAID can fit into an enterprise retrieval workflow.

Return-policy information is collected from two internal documents, an operational SQL database, and a captured vendor API response in this workflow. A research step then derives additional assertions from the document and vendor results.

Its goal is to show how evidence is collected from different enterprise systems while preserving where that evidence came from. The workflow is coordinated by LangGraph before BRAID's reliability propagation algorithm receives the assertions.

The simulated relationship labels are used only to evaluate the experiment. Retrieval and evaluation do not use them.

Two timestamps are kept separate:

- `retrieved_at` records when a resource was accessed by the workflow.
- `observed_at` records when the source says the information was published or updated.

When calculating temporal dependency, only `observed_at` is used.

Run the experiment from the repository root by opening Python:

```bash
.venv/bin/python
```

Then run:

```python
from agent_dataset.enterprise import run_enterprise

result = run_enterprise(
    debug=True,
)

print(result)
```
