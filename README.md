# Edge Quantum Guard (EQG)

**EQG** is an autonomous low-level control layer for quantum execution. It sits between the workload and the backend and runs a closed loop:

| Role | Module | Function |
|------|--------|----------|
| Eyes | Observer / AOM | Estimates qubit health, friction, and regime |
| Reflexes | MORPH | Selects an optimal connected layout under conflict constraints |
| Judgment | Governance | Chooses hold / remap / conditional DD with causal scoring |
| Hands | Centinela | Applies low-privilege actuation (phase / CPMG-XY4 DD) |

Primary metric: **Hamiltonian Integrity Score (HIS)** — fidelity of estimating Pauli Hamiltonian observables under noise.

## Product install

```bash
pip install -e .
# or
docker build -t eqg:0.1.0 .
```

## Run

```bash
# Local smoke
python main.py --mode sim --smoke --output-dir ./outputs

# CLI
eqg --arm all --mode sim --output ./outputs

# Container
docker run --rm -v "$PWD/outputs:/app/outputs" eqg:0.1.0 \
  --mode sim --smoke --output-dir /app/outputs
```

## Helm (IBM Cloud / OpenShift catalog delivery)

```bash
helm package chart
helm install eqg ./chart --set mode=sim --set smoke=true
```

For IBM Quantum hardware jobs, set:

```bash
--set mode=hardware --set ibmQuantum.existingSecret=ibm-quantum-token
```

## Configuration

See `configs/default.yaml`.

| Key | Default | Description |
|-----|---------|-------------|
| `runtime.mode` | `sim` | `sim` or `hardware` |
| `runtime.n_qubits` | 4 | Logical width |
| `runtime.shots` | 2048 | Shots per circuit |
| `runtime.health_threshold` | 0.92 | Eyes threshold for conditional DD |
| `arms` | A,C,D,E | Ablation / product arms |

## Arms

| Arm | Behavior |
|-----|----------|
| A | Naive layout, DD off |
| C | MORPH layout, DD off |
| D | MORPH + DD always |
| E | Full EQG (live Eyes + Judgment + conditional Centinela) |

## IBM Cloud catalog

- **Product type:** Software  
- **Delivery method:** Helm chart  
- **Source:** release tarball of this product tree (`chart/` + container image `eqg:0.1.0`)

## Version

`0.1.0` — see `VERSION` and `CHANGELOG.md`.

## License

Elastic License 2.0 (ELv2). See `LICENSE`.
