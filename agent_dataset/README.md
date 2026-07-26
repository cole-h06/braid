## Agent Dataset Demo

This directory shows how Verity integrates into a multi-agent workflow.

Five specialized agents independently produce structured assertions, which are then combined into a `CredibilityGraph`.

The benchmark computes:

- Pairwise source dependencies
- Source credibility
- Claim support

The agents have been intentionally designed so that some agents agree while others disagree. This allows the inference engine to derive credibility from the graph.