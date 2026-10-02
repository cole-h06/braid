# BRAID Benchmark

This is the directory containing the benchmark dataset used to develop and evaluate the BRAID algorithm.

With this benchmark, you can experiment with:

- Reliability propagation
- Agreement weighting
- Source dependency estimation

Under BRAID 1.0.0 these CSV tables do not supply provenance. The benchmark
therefore explicitly uses zero dependency and zero signal coverage, not an
overlap-derived estimate or evidence of verified independence. Use the
agent datasets to exercise provenance-based estimation.

The CSV adapter collapses repeated source–claim rows into binary edges, as
before; agreement counts distinct sources rather than raw CSV rows. The
normalized inference graph itself must not contain duplicate edges.

## Running the benchmark

Clone the repository:

```bash
git clone https://github.com/cole-h06/braid.git
cd braid
```

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

From the project root, run:

```bash
python run_benchmark.py
```

## Tables

- `sources.csv` - source identifiers
- `claims.csv` - claim nodes
- `assertions.csv` - edges connecting sources to claims

The benchmark computes:

- Source dependency matrix
- Source independence estimates
- Agreement-weighted claim support
- Reliability propagation until convergence
- Final source reliability scores

Product specifications are currently the development benchmark because they provide large amounts of conflicting information retrieved from multiple data sources. BRAID itself is not limited by any specific information domain and operates on structured sources, claims, assertions, and associated dependency signals.
