#!/usr/bin/env python3
"""EQG product entrypoint — ablation A/C/D/E."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eqg import __version__
from eqg.runtime import EQGRuntime


def main():
    p = argparse.ArgumentParser(description="Edge Quantum Guard product runtime")
    p.add_argument("--mode", choices=["sim", "hardware"], default="sim")
    p.add_argument("--n-qubits", type=int, default=4)
    p.add_argument("--shots", type=int, default=2048)
    p.add_argument("--output-dir", default="./outputs")
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rt = EQGRuntime(
        n_qubits=args.n_qubits,
        shots=256 if args.smoke else args.shots,
    )
    results = {k: v.to_dict() for k, v in rt.run_ablation().items()}
    payload = {
        "product": "edge-quantum-guard",
        "version": __version__,
        "mode": args.mode,
        "results": results,
    }
    path = out / "eqg_ablation.json"
    path.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    print(f"Wrote {path}", flush=True)


if __name__ == "__main__":
    main()
