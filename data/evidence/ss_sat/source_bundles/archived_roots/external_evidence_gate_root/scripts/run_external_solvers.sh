#!/usr/bin/env bash
# carrollian-token-burn-guard-sh-bootstrap
if [ "${CARROLLIAN_TOKEN_BURN_GUARD_SH:-0}" != "1" ]; then
  case "$0" in
    *.sh)
      if command -v mktemp >/dev/null 2>&1; then
        CARROLLIAN_TOKEN_BURN_GUARD_SH=1
        export CARROLLIAN_TOKEN_BURN_GUARD_SH
        _ctbg_out=$(mktemp "${TMPDIR:-/tmp}/carrollian-stdout.XXXXXX") || exit 1
        _ctbg_err=$(mktemp "${TMPDIR:-/tmp}/carrollian-stderr.XXXXXX") || { rm -f "$_ctbg_out"; exit 1; }
        _ctbg_first=$(sed -n '1p' "$0" 2>/dev/null || true)
        case "$_ctbg_first" in *bash*) _ctbg_runner=${BASH:-bash} ;; *) _ctbg_runner=sh ;; esac
        if ! command -v "$_ctbg_runner" >/dev/null 2>&1; then _ctbg_runner=sh; fi
        "$_ctbg_runner" "$0" "$@" >"$_ctbg_out" 2>"$_ctbg_err"
        _ctbg_status=$?
        _ctbg_max_out=${CARROLLIAN_TOKEN_BURN_MAX_STDOUT:-8192}
        _ctbg_max_err=${CARROLLIAN_TOKEN_BURN_MAX_STDERR:-8192}
        _ctbg_size_out=$(wc -c <"$_ctbg_out" | tr -d ' ')
        _ctbg_size_err=$(wc -c <"$_ctbg_err" | tr -d ' ')
        dd if="$_ctbg_out" bs=1 count="$_ctbg_max_out" 2>/dev/null || true
        if [ "${_ctbg_size_out:-0}" -gt "$_ctbg_max_out" ] 2>/dev/null; then
          printf '
[carrollian-token-burn-guard: stdout truncated; full data belongs in files]
'
        fi
        dd if="$_ctbg_err" bs=1 count="$_ctbg_max_err" 2>/dev/null >&2 || true
        if [ "${_ctbg_size_err:-0}" -gt "$_ctbg_max_err" ] 2>/dev/null; then
          printf '
[carrollian-token-burn-guard: stderr truncated; full data belongs in files]
' >&2
        fi
        rm -f "$_ctbg_out" "$_ctbg_err"
        exit "$_ctbg_status"
      fi
      ;;
  esac
fi
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
