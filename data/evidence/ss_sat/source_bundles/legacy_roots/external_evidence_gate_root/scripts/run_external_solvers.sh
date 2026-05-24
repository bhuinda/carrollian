#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/drop_external_logs_here}"
mkdir -p "$OUT"
for cnf in "$ROOT"/benchmarks/*.cnf; do
  base="$(basename "$cnf" .cnf)"
  if command -v cadical >/dev/null 2>&1; then
    cadical "$cnf" > "$OUT/${base}.cadical.stdout.txt" 2> "$OUT/${base}.cadical.stderr.txt" || true
  fi
  if command -v kissat >/dev/null 2>&1; then
    kissat "$cnf" > "$OUT/${base}.kissat.stdout.txt" 2> "$OUT/${base}.kissat.stderr.txt" || true
  fi
  if command -v minisat >/dev/null 2>&1; then
    minisat "$cnf" "$OUT/${base}.minisat.model.txt" > "$OUT/${base}.minisat.stdout.txt" 2> "$OUT/${base}.minisat.stderr.txt" || true
  fi
done
python3 "$ROOT/scripts/analyze_external_evidence.py" "$OUT" --out "$ROOT/external_analysis"
