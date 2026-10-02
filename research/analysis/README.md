# Research diagnostics

These modules preserve exploratory calculations from the former `braid/analysis/`
directory. They are not normative BRAID dependency estimators; their formulas and
research interpretations have not changed. Automatic structural-overlap estimation
remains disabled in BRAID 1.0.0.

The modules accept in-memory data. Obsolete PostgreSQL loaders and command-line
entry points were removed. Import from the repository root, for example:

```python
from research.analysis.directional_inclusion import directional_inclusion

result = directional_inclusion({"claim": "value"}, {"claim": "value"})
```

`community_overlap` accepts assertion rows and requires NetworkX. The overlap,
evidence-independence and matrix modules accept the mappings or metadata rows
specified by their function arguments. `graph_matrix` combines caller-supplied
matrices. The legacy temporal diagnostic retains its seven-day window; it is not
the normative temporal estimator or the agent adapter's two-hour default.

Product-specific normalization, database mutation scripts, the database pair
inspection CLI and the CSV benchmark are retired. Their prior versions remain
available in git history.
