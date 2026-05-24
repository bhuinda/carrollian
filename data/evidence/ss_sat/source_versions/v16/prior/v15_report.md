# G^natural Ontological Computation v15

## Scope

V15 builds the external solver/proof-log bridge. It probes the sandbox for third-party SAT solvers and DRAT/LRAT tools, adds runnable adapters, adds a small DIMACS benchmark suite, and certifies canary ingestion for solver stdout, DRAT-like, and LRAT-like inputs.

It does **not** claim third-party solver evidence yet: no common external solver binary or proof verifier was found on this sandbox PATH during the probe.

The finite base remains \(G^
atural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## External tool probe

| item | result |
|---|---:|
| solver binaries found | 0 |
| proof tools found | 0 |
| benchmarks included | 5 |
| canary fixture formats parsed | 4 |

## Status

\[
oxed{	ext{third-party solver/proof ingestion is harness-ready but evidence-pending}}
\]

V14's internally generated proof-certificate layer is carried forward as the last completed proof-log invariant. The v15 contribution is the external reproducibility interface needed to ingest genuine MiniSat/CaDiCaL/Kissat-style solver logs or DRAT/LRAT proof files when supplied.

## How to run locally

```bash
cd gnatural_ontological_computation_v15
python3 adapters/run_external_solvers.py --solver cadical --cnf benchmarks/horn_chain_8.cnf --out external_runs
python3 adapters/ingest_external_logs.py external_runs/*.stdout.txt external_runs/*.proof --out external_runs/canonical_events.json
```

If a solver emits DRAT/LRAT files, pass those files directly to `ingest_external_logs.py`.
