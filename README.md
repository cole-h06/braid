# Verity

A graph-based credibility inference engine for information networks. Verity models sources and claims as a bipartite graph to infer source credibility and claim support.

## Problem

As AI systems, from foundational large language models (LLMs) to fully autonomous agents, reason and execute complex tasks across digital environments using information collected from many sources, evaluating the credibility of this information becomes highly important.

## Research Challenge

Source credibility and claim credibility depend on each other recursively.

A source gains credibility when it supports claims that receive stronger support across the network.
A claim gains support when it is asserted by more credible sources.

When an agent scrapes data from 50 different websites, how do we know who to trust?

We typically rely on agreement between sources as evidence of truth. But, if Source A and Source B agree, is it really agreement? Or did Source B just copy its data from Source A?

## Approach

Sources and claims form a bipartite graph. Each edge represents a source asserting a claim. Verity models information as an interconnected network instead of a collection of independent observations.
<p align="center">
  <img src="images/credibility_animation.gif" width="520">
</p>

<p align="center">
  <em>An animation of credibility propagation running on a small network of sources and claims. Node size represents inferred credibility, while edges represent assertions.</em>
</p>

Credibility is computed iteratively across the graph. At each iteration step, each source distributes its credibility across all claims it asserts, and each claim in turn redistributes the support it has accumulated back to the asserting sources. The iterations repeat until the credibility vector reaches a fixed point. Agreement weighting and dependency adjustment influence how much support each assertion contributes

## Domain-Agnostic Design

Verity does not interpret a claim's meaning. The current implementation uses product specifications as a development dataset because they provide conflicting information collected from multiple sources. Clients can construct the same source-claim graph from information in any domain.

The core inference engine receives unique source and claim identifiers, as well as the assertion edges that create the relationships between them. Before inference, the input data is prepared and converted into a source-claim graph.

The current research also uses provenance and evidence metadata before inference to estimate source dependency. This results in a dependency matrix that is used to reduce the influence of evidence that may not be independent.

Some examples of equivalent assertions that could be merged before graph construction:

```text
Product specifications:

- Bluetooth 5.3
- BT 5.3
- Bluetooth version 5.3

AI coding agents:

- Python 3.12
- Python 3.12.0
- Python v3.12

Enterprise knowledge:

- Financial Report -> Revenue: $4.2M
- ERP Export -> Revenue = 4,200,000 USD
- Slack Discussion -> Quarterly revenue was $4.2 million
```

## Repository

- `agent_dataset/` — Multi-agent and enterprise retrieval experiments
- `benchmark/` — Reproducible benchmark dataset
- `credibility/` — Credibility inference engine and dependency analysis
- `paper/` — Research paper
- `research/` — Research notes
- `scripts/` — Development utilities
  
## Current Status

Verity is an active research project focused on evaluating source credibility based on the graph structure of an information network.

Alongside agreement-weighted credibility propagation, the current engine uses additional signals to identify when apparent agreement may come from dependent sources instead of independent support. It has been tested with a [controlled multi-agent dataset](agent_dataset/README.md) and a [simulated enterprise retrieval workflow](agent_dataset/enterprise/README.md).

## MCP Server

You can find the Verity credibility inference engine through the open-source [`verity-mcp`](https://github.com/cole-h06/verity-mcp) server. It enables AI systems to incorporate credibility signals directly into their workflows through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io).

This repository contains the research and reference implementation behind the server.

## Vision

Verity explores how credibility inference can be made accessible and simplified for AI systems.

Modern autonomous agents are capable of retrieving vast amounts of information at scale, but still lack a native mechanism for reasoning about the underlying credibility of information. This becomes problematic as these agents become integrated into everyday decisions and act on information on behalf of users. Current methods for evaluating information primarily analyze what was said. While LLMs are capable of reasoning about semantic text and supporting evidence, their ability to reason about the structure of information itself is limited.

Verity takes a different approach by modeling information as a bipartite graph of source-to-claim assertions. It evaluates the topology of an information network and shifts credibility inference from reasoning about what was said to reasoning about how evidence is connected across sources.

## Contact

Feel free to connect with me whether you have any ideas, questions, feedback, or if you just want to chat about interesting topics! 

Email: colehoke1@gmail.com

LinkedIn:
https://www.linkedin.com/in/cole-hoke-8537002a2/
