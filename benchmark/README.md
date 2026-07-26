# Verity Benchmark

This is the directory containing the benchmark dataset used for developing the Verity credibility inference engine.

With this benchmark, you can experiment with:

- Credibility propagation
- Agreement weighting
- Source dependency modeling

## Running the benchmark

Clone the repository:

```bash
git clone https://github.com/cole-h06/Verity.git
cd Verity
```

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

From the project root, run:

```bash
python3 run_benchmark.py
```

## Tables

- `sources.csv` - source identifiers
- `claims.csv` - claim nodes
- `assertions.csv` - edges connecting sources to claims

The benchmark computes:

- Source dependency matrix
- Source independence estimates
- Agreement-weighted claim support
- Credibility propagation until convergence
- Final source credibility scores

Product specifications are currently the benchmark being used for development as they provide large amounts of conflicting data published by independent sources. That said, the inference algorithms themselves are not limited by any specific domain and operate only on graph structure.perate only on graph structure.grate source dependency inference)
ate only on graph structure.