"""EQG command-line entrypoint."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from eqg import __version__
from eqg.runtime import EQGRuntime


@click.command()
@click.option("--mode", type=click.Choice(["sim", "hardware"]), default="sim", show_default=True)
@click.option("--arm", default="E", show_default=True, help="Single arm A|C|D|E or 'all'")
@click.option("--n-qubits", default=4, show_default=True, type=int)
@click.option("--shots", default=2048, show_default=True, type=int)
@click.option("--output", "output_dir", default="./outputs", show_default=True, type=click.Path())
@click.option("--smoke", is_flag=True, help="Quick product smoke run")
def main(mode: str, arm: str, n_qubits: int, shots: int, output_dir: str, smoke: bool):
    """Edge Quantum Guard — product CLI."""
    if mode == "hardware":
        click.echo(
            "Hardware mode: set IBM Quantum credentials in the environment "
            "(IBM_QUANTUM_TOKEN / QiskitRuntimeService) before enabling backend jobs.",
            err=True,
        )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rt = EQGRuntime(n_qubits=n_qubits, shots=shots if not smoke else 256)
    if arm.lower() == "all":
        results = {k: v.to_dict() for k, v in rt.run_ablation().items()}
    else:
        results = {arm: rt.run_arm(arm=arm).to_dict()}

    payload = {
        "product": "edge-quantum-guard",
        "version": __version__,
        "mode": mode,
        "results": results,
    }
    path = out / "eqg_result.json"
    path.write_text(json.dumps(payload, indent=2))
    click.echo(json.dumps(payload, indent=2))
    click.echo(f"Wrote {path}", err=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
