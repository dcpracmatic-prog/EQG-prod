#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(cat "$ROOT/VERSION")"
cd "$ROOT"

echo "Building EQG product image eqg:${VERSION}"
docker build -t "eqg:${VERSION}" -t eqg:latest .

echo "Packaging Helm chart"
helm package chart -d dist/ 2>/dev/null || mkdir -p dist && tar -czf "dist/edge-quantum-guard-${VERSION}.tgz" chart

echo "Done. Artifacts:"
ls -la dist/ 2>/dev/null || true
docker images eqg --format '{{.Repository}}:{{.Tag}}  {{.ID}}'
