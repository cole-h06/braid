# BRAID Research

BRAID owns the normative mathematical specification, reference implementation
and frozen conformance fixtures. Downstream implementations follow a specific
BRAID version and repository revision.

## Open Research Questions

BRAID is an active research algorithm. The current implementation provides a working propagation system, but several properties of that system remain open:

- **Convergence and uniqueness.** Under what conditions does reliability propagation converge to a unique fixed point, and how do graph structure, initialization, and normalization affect that behavior?

- **Fixed-point interpretation.** What structural quantity does the equilibrium distribution represent, and under what assumptions can it be interpreted as reliability?

- **Self-reinforcement.** Under what conditions can mutually reinforcing source-claim structures amplify their own scores? When does that reinforcement cease to represent independent support?

- **Disconnected components.** How should reliability scores be interpreted or compared across disconnected or weakly connected regions of the graph?

- **Dependency-adjusted propagation.** How does weighting assertions by estimated source independence change the propagation operator, its equilibrium, and its susceptibility to redundant evidence?

- **Structural cold start.** How should newly introduced sources and claims enter an established reliability distribution without requiring arbitrary prior scores or structurally disadvantaging new evidence?

These questions motivate the ongoing theoretical analysis and experimental evaluation of BRAID.

## Normative BRAID 1.0.0

- [Algorithm manifest](algorithm.json)
- [Reliability propagation](reliability_propagation.md)
- [Agreement weighting](agreement_weighting.md)
- [Dependency estimation](source_dependency_estimation.md)
- [Dependency telemetry](dependency_telemetry.md)

The reference is in ../braid/engine.py, ../braid/graph.py and
../braid/dependency.py. Agent workflows adapt records to that reference.

## Evidence and history

[Synchronization](synchronization.md) records migration evidence and limitations.
[Structural redundancy](structural_source_dependencies.md) is historical
exploratory mathematics, not an active estimator signal. Synthetic datasets
are research inputs, not proof of optimality or truth-probability calibration.

Future changes require a BRAID decision, specification, reference and fixture
update first. Downstream evaluations can motivate proposals, not silently
redefine the algorithm.
