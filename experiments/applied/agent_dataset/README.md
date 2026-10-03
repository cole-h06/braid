## Mocked Agent Dataset

This experiment displays how BRAID integrates into a multi-agent workflow.

Five specialized agents return fifteen observations. Each `Observation` is a
structured assertion accompanied by provenance metadata, matching Omneum's
observation boundary. The schema is local to this experiment and does not depend
on the Omneum repository or package.

An observation contains `assertion_id`, `source_id`, `entity_namespace`, `entity`,
`attribute`, and `value`, together with `observed_at`, `source_modified_at`,
`upstream_source_ids`, `cited_source_ids`, `parent_assertion_ids`, `retrievals`,
`metadata`, and `dependency_signals`. Provenance belongs to the observation.
Unknown relationship metadata is `None`; an empty tuple means capture found no
relationships. Timestamps must be timezone-aware.

`AgentResult.observations` holds each agent's records. `load_dataset()` returns
`(sources, observations)`, and experiment and workflow results expose an
`observations` collection. The local adapter passes these same records to BRAID's
claim and provenance input slots without creating separate records. The existing
source/claim graph keys and dependency calculation are preserved. This fixture
uses the single namespace `agent_dataset`; `metadata` and `dependency_signals`
are extensible metadata mappings, empty by default, and do not override the
estimator's existing provenance-derived signals.

In this dataset, there are examples of:

- upstream source relationships;
- explicit citations;
- assertion lineage;
- shared ownership;
- close publication timing;
- structural assertion overlap;
- independent conflicting information.

BRAID 1.0.0 uses the [normative estimator](../../../spec/braid.md).
Structural overlap is not active provenance. Modification-time proximity is
unavailable in this mocked dataset; observation times do not substitute for it.
Direct relationships use a maximum; contextual signals uses a weighted sum.
Dependency discounts forward contributions, but does not guarantee every
converged claim score decreases.

## Baseline Weights

```text
upstream             0.25
citation             0.20
assertion_lineage    0.20
ownership            0.10
temporal             0.10
graph                0.15
retrieval            0.00
```

Note that these starting weights have been hand-tuned. They have not been calibrated against labeled source-dependency data.
The adapter uses a two-hour temporal window. The inactive graph weight remains
in the normalization denominator. Neither these weights nor this window are
universal calibrated BRAID defaults.

Run the experiment from the repository root:

```bash
PYTHONPATH=src:experiments/applied python3 -m agent_dataset.run
```

Run the tests:

```bash
python3 -m pytest experiments/applied/agent_dataset/tests -v
```

## LangGraph Workflow

The same five agents are also capable of running through LangGraph. They run in parallel, then their results are collected in a fixed order before validation, graph construction, dependency estimation, and observation evaluation.

There is no LLM or external retrieval involved. The workflow produces the same result as the sequential experiment.

Open Python from the repository root:

```bash
PYTHONPATH=src:experiments/applied .venv/bin/python
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
