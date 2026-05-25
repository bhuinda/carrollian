#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path
from typing import Any


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "README.md").exists() and (parent / "data").is_dir():
            return parent
    raise SystemExit("could not locate repository root")


ROOT = find_repo_root()
BASE = ROOT / "data" / "evidence" / "ss_sat"
SOURCE_ARCHIVE_ROOT = BASE / "source_bundles" / "archived_roots" / "external_evidence_gate_root"

CADICAL = SOURCE_ARCHIVE_ROOT / "cadical-rel-3.0.0" / "build" / "cadical.exe"
DRAT_TRIM = SOURCE_ARCHIVE_ROOT / "cadical-rel-3.0.0" / "build" / "drat-trim.exe"
LRAT_TRIM = SOURCE_ARCHIVE_ROOT / "cadical-rel-3.0.0" / "build" / "lrat-trim.exe"
KISSAT = SOURCE_ARCHIVE_ROOT / "kissat-rel-4.0.4" / "build" / "kissat.exe"
MINISAT = SOURCE_ARCHIVE_ROOT / "minisat" / "simp" / "minisat.exe"

BENCH_DIR = BASE / "benchmarks" / "scaled"
SOLVER_LOG_DIR = BASE / "logs" / "scaled_solver_runs"
PROOF_LOG_DIR = BASE / "logs" / "scaled_proof_runs"
DRAT_DIR = BASE / "proofs" / "scaled_cadical_drat"
LRAT_DIR = BASE / "proofs" / "scaled_cadical_lrat"
TABLE_DIR = BASE / "tables"
REPORT_DIR = BASE / "reports"
MANIFEST_DIR = BASE / "manifests"
RESIDUE_DIR = BASE / "residues"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(BASE).as_posix()


def ensure_tools() -> None:
    missing = [p for p in [CADICAL, DRAT_TRIM, LRAT_TRIM, KISSAT, MINISAT] if not p.exists()]
    if missing:
        raise SystemExit("missing solver/checker executables: " + ", ".join(str(p) for p in missing))


def write_once(path: Path, data: str | bytes, *, force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing evidence file: {path}")
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8", newline="\n")


def dimacs(var_count: int, clauses: list[list[int]], comments: list[str]) -> str:
    lines = [f"c {comment}" for comment in comments]
    lines.append(f"p cnf {var_count} {len(clauses)}")
    lines.extend(" ".join(str(lit) for lit in clause) + " 0" for clause in clauses)
    return "\n".join(lines) + "\n"


def horn_chain(n: int) -> tuple[int, list[list[int]], list[str]]:
    clauses = [[1]]
    clauses.extend([[-i, i + 1] for i in range(1, n)])
    clauses.append([-n])
    return n, clauses, [f"scaled horn chain UNSAT witness n={n}"]


def php(pigeons: int, holes: int) -> tuple[int, list[list[int]], list[str]]:
    def var(pigeon: int, hole: int) -> int:
        return (pigeon - 1) * holes + hole

    clauses: list[list[int]] = []
    for pigeon in range(1, pigeons + 1):
        clauses.append([var(pigeon, hole) for hole in range(1, holes + 1)])
    for hole in range(1, holes + 1):
        for p, q in itertools.combinations(range(1, pigeons + 1), 2):
            clauses.append([-var(p, hole), -var(q, hole)])
    return pigeons * holes, clauses, [f"scaled pigeonhole UNSAT PHP({pigeons},{holes})"]


def xor_contradiction(n: int) -> tuple[int, list[list[int]], list[str]]:
    clauses: list[list[int]] = []
    for assignment in itertools.product([False, True], repeat=n):
        clause = []
        for idx, value in enumerate(assignment, start=1):
            clause.append(-idx if value else idx)
        clauses.append(clause)
    return n, clauses, [f"scaled parity contradiction over {n} variables"]


def benchmark_specs() -> dict[str, tuple[int, list[list[int]], list[str]]]:
    specs: dict[str, tuple[int, list[list[int]], list[str]]] = {}
    for n in [16, 32, 64, 128]:
        specs[f"horn_chain_{n}"] = horn_chain(n)
    for pigeons, holes in [(4, 3), (5, 4), (6, 5)]:
        specs[f"php_{pigeons}_{holes}"] = php(pigeons, holes)
    for n in [6, 8]:
        specs[f"xor_parity_{n}_unsat"] = xor_contradiction(n)
    return specs


def run_capture(cmd: list[Path | str], stdout_path: Path, stderr_path: Path, *, timeout: int, force: bool) -> dict[str, Any]:
    if (stdout_path.exists() or stderr_path.exists()) and not force:
        raise SystemExit(f"refusing to overwrite existing logs for {stdout_path.name}")
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            [str(part) for part in cmd],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        timed_out = False
        stdout = proc.stdout
        stderr = proc.stderr
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or b""
        stderr = (exc.stderr or b"") + f"\nTIMEOUT after {timeout}s\n".encode("utf-8")
        returncode = None
    elapsed = time.perf_counter() - started
    write_once(stdout_path, stdout, force=force)
    write_once(stderr_path, stderr, force=force)
    return {
        "command": " ".join(str(part) for part in cmd),
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 6),
        "stdout": rel(stdout_path),
        "stdout_sha256": sha_file(stdout_path),
        "stderr": rel(stderr_path),
        "stderr_sha256": sha_file(stderr_path),
        "stdout_size": stdout_path.stat().st_size,
        "stderr_size": stderr_path.stat().st_size,
    }


def classify_solver(text: str, returncode: int | None, timed_out: bool) -> str:
    if timed_out:
        return "TIMEOUT"
    upper = text.upper()
    if "SIGSEGV" in upper or "SEGMENTATION" in upper:
        return "SIGSEGV"
    if "UNSATISFIABLE" in upper or "S UNSAT" in upper:
        return "UNSAT"
    if "SATISFIABLE" in upper or "S SAT" in upper:
        return "SAT"
    if returncode not in (0, 10, 20):
        return "ERROR"
    return "UNKNOWN"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def solver_runs(benchmarks: dict[str, Path], *, force: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    solvers = [
        ("cadical", "3.0.0", [CADICAL], 120),
        ("kissat", "4.0.4 local-manual-build", [KISSAT], 120),
        ("minisat", "2.0 beta", [MINISAT], 120),
    ]
    for base, cnf in benchmarks.items():
        for solver, solver_identity, prefix, timeout in solvers:
            model_path = SOLVER_LOG_DIR / f"{base}.minisat.model.txt"
            cmd = [*prefix, cnf]
            if solver == "minisat":
                if model_path.exists() and not force:
                    raise SystemExit(f"refusing to overwrite existing MiniSat model: {model_path}")
                cmd.append(model_path)
            stdout = SOLVER_LOG_DIR / f"{base}.{solver}.stdout.txt"
            stderr = SOLVER_LOG_DIR / f"{base}.{solver}.stderr.txt"
            info = run_capture(cmd, stdout, stderr, timeout=timeout, force=force)
            text = read_text(stdout) + "\n" + read_text(stderr)
            status = classify_solver(text, info["returncode"], info["timed_out"])
            row = {
                "benchmark": f"scaled/{base}.cnf",
                "solver": solver,
                "solver_identity": solver_identity,
                "status": status,
                **info,
            }
            if solver == "minisat" and model_path.exists():
                row["model"] = rel(model_path)
                row["model_sha256"] = sha_file(model_path)
            rows.append(row)
            print(f"{base} {solver}: {status}", flush=True)
    return rows


def proof_runs(benchmarks: dict[str, Path], *, force: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for base, cnf in benchmarks.items():
        drat = DRAT_DIR / f"{base}.cadical.drat"
        lrat = LRAT_DIR / f"{base}.cadical.lrat"
        drat_info = run_capture(
            [CADICAL, "--checkproof=3", "--no-binary", cnf, drat],
            PROOF_LOG_DIR / f"{base}.cadical_drat.stdout.txt",
            PROOF_LOG_DIR / f"{base}.cadical_drat.stderr.txt",
            timeout=180,
            force=force,
        )
        lrat_info = run_capture(
            [CADICAL, "--lrat", "--checkproof=2", "--no-binary", cnf, lrat],
            PROOF_LOG_DIR / f"{base}.cadical_lrat.stdout.txt",
            PROOF_LOG_DIR / f"{base}.cadical_lrat.stderr.txt",
            timeout=180,
            force=force,
        )
        drat_verify = run_capture(
            [DRAT_TRIM, cnf, drat],
            PROOF_LOG_DIR / f"{base}.drat_trim.stdout.txt",
            PROOF_LOG_DIR / f"{base}.drat_trim.stderr.txt",
            timeout=180,
            force=force,
        )
        lrat_verify = run_capture(
            [LRAT_TRIM, cnf, lrat],
            PROOF_LOG_DIR / f"{base}.lrat_trim.stdout.txt",
            PROOF_LOG_DIR / f"{base}.lrat_trim.stderr.txt",
            timeout=180,
            force=force,
        )
        for proof_format, proof_path, solver_info, verifier, verify_info in [
            ("DRAT", drat, drat_info, "drat-trim", drat_verify),
            ("LRAT", lrat, lrat_info, "lrat-trim", lrat_verify),
        ]:
            verify_text = read_text(BASE / verify_info["stdout"]) + "\n" + read_text(BASE / verify_info["stderr"])
            verified = "VERIFIED" in verify_text.upper()
            rows.append({
                "benchmark": f"scaled/{base}.cnf",
                "proof_format": proof_format,
                "proof": rel(proof_path),
                "proof_sha256": sha_file(proof_path),
                "proof_size": proof_path.stat().st_size,
                "cadical_command": solver_info["command"],
                "cadical_returncode": solver_info["returncode"],
                "cadical_stdout": solver_info["stdout"],
                "cadical_stderr": solver_info["stderr"],
                "verifier": verifier,
                "verifier_command": verify_info["command"],
                "verifier_returncode": verify_info["returncode"],
                "verifier_stdout": verify_info["stdout"],
                "verifier_stderr": verify_info["stderr"],
                "verified": verified,
            })
        print(f"{base} proofs: DRAT/LRAT", flush=True)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], *, force: bool) -> None:
    if not rows:
        return
    fieldnames = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing table: {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any], *, force: bool) -> None:
    write_once(path, json.dumps(payload, indent=2, sort_keys=True) + "\n", force=force)


def summarize_solver(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"total": len(rows)}
    for row in rows:
        key = f"{row['solver']}_{row['status']}".lower()
        out[key] = out.get(key, 0) + 1
    return out


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def summarize_proofs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_format: dict[str, dict[str, int]] = {}
    for row in rows:
        fmt = row["proof_format"].lower()
        by_format.setdefault(fmt, {"total": 0, "verified": 0})
        by_format[fmt]["total"] += 1
        by_format[fmt]["verified"] += int(truthy(row["verified"]))
    return by_format


def artifact_entry(path: Path, kind: str) -> dict[str, Any]:
    return {
        "path": rel(path),
        "kind": kind,
        "size": path.stat().st_size,
        "sha256": sha_file(path),
    }


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rewrite_scaled_derivatives(
    benchmark_rows: list[dict[str, Any]],
    solver_rows: list[dict[str, Any]],
    proof_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    solver_table = TABLE_DIR / "scaled_solver_run_summary.csv"
    proof_table = TABLE_DIR / "scaled_proof_verification_summary.csv"
    benchmark_table = TABLE_DIR / "scaled_benchmark_summary.csv"

    for row in proof_rows:
        verify_text = read_text(BASE / row["verifier_stdout"]) + "\n" + read_text(BASE / row["verifier_stderr"])
        row["verified"] = "True" if "VERIFIED" in verify_text.upper() else "False"

    write_csv(solver_table, solver_rows, force=True)
    write_csv(proof_table, proof_rows, force=True)
    write_csv(benchmark_table, benchmark_rows, force=True)

    residue_rows = [
        {
            "benchmark": row["benchmark"],
            "solver": row["solver"],
            "status": row["status"],
            "stdout": row["stdout"],
            "stderr": row["stderr"],
            "returncode": row["returncode"],
        }
        for row in solver_rows
        if row["status"] not in {"UNSAT"}
    ]
    residue_path = RESIDUE_DIR / "scaled_solver_residues.json"
    write_json(
        residue_path,
        {
            "schema": "d20.ss_sat.scaled_solver_residues.source_drop",
            "status": "SS_SAT_SCALED_RESIDUES_RECORDED" if residue_rows else "SS_SAT_SCALED_NO_SOLVER_RESIDUES",
            "residues": residue_rows,
        },
        force=True,
    )

    report = {
        "schema": "d20.ss_sat.scaled_evidence_report.source_drop",
        "status": "SS_SAT_SCALED_EVIDENCE_CAPTURED",
        "canonical_folder": "data/evidence/ss_sat",
        "benchmark_count": len(benchmark_rows),
        "solver_runs": summarize_solver(solver_rows),
        "proof_verification": summarize_proofs(proof_rows),
        "tables": [rel(benchmark_table), rel(solver_table), rel(proof_table)],
        "residues": rel(residue_path),
        "interpretation": "Scaled tranche extends SS-SAT evidence beyond the original five fixtures while preserving raw solver logs and CaDiCaL proof certificates.",
    }
    report_path = REPORT_DIR / "ss_sat_scaled_evidence.json"
    write_json(report_path, report, force=True)
    md_path = REPORT_DIR / "ss_sat_scaled_evidence.md"
    md = [
        "# SS-SAT scaled evidence",
        "",
        f"- Benchmarks: {len(benchmark_rows)}",
        f"- Solver runs: {report['solver_runs']}",
        f"- Proof verification: {report['proof_verification']}",
        f"- Residues: {len(residue_rows)}",
        "",
        "Raw stdout/stderr logs are stored under `logs/scaled_solver_runs` and `logs/scaled_proof_runs`.",
    ]
    write_once(md_path, "\n".join(md) + "\n", force=True)

    artifacts: list[dict[str, Any]] = []
    for path in sorted(BENCH_DIR.glob("*.cnf")):
        artifacts.append(artifact_entry(path, "cnf_benchmark"))
    for path in sorted(SOLVER_LOG_DIR.glob("*")):
        artifacts.append(artifact_entry(path, "solver_log"))
    for path in sorted(PROOF_LOG_DIR.glob("*")):
        artifacts.append(artifact_entry(path, "proof_or_checker_log"))
    for path in sorted(DRAT_DIR.glob("*.drat")):
        artifacts.append(artifact_entry(path, "drat_proof"))
    for path in sorted(LRAT_DIR.glob("*.lrat")):
        artifacts.append(artifact_entry(path, "lrat_proof"))
    for path in [benchmark_table, solver_table, proof_table, residue_path, report_path, md_path]:
        artifacts.append(artifact_entry(path, "derived_summary"))

    manifest = {
        "schema": "d20.ss_sat.scaled_external_evidence_manifest.source_drop",
        "status": "SS_SAT_SCALED_EXTERNAL_EVIDENCE_MANIFEST_BUILT",
        "created_by": "data/evidence/ss_sat/scripts/run_scaled_evidence.py",
        "solver_identitys": {
            "cadical": "3.0.0",
            "kissat": "4.0.4 local-manual-build",
            "minisat": "2.0 beta",
            "drat-trim": "cadical-rel-3.0.0 build",
            "lrat-trim": "0.2.1-dev",
        },
        "command_lines_preserved_in": [rel(solver_table), rel(proof_table)],
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    manifest_path = MANIFEST_DIR / "scaled_external_evidence_manifest.json"
    write_json(manifest_path, manifest, force=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and run scaled SS-SAT evidence.")
    parser.add_argument("--force", action="store_true", help="overwrite scaled generated evidence")
    parser.add_argument("--summarize-only", action="store_true", help="refresh derived scaled tables/reports without rerunning solvers")
    args = parser.parse_args()

    ensure_tools()
    for directory in [BENCH_DIR, SOLVER_LOG_DIR, PROOF_LOG_DIR, DRAT_DIR, LRAT_DIR, TABLE_DIR, REPORT_DIR, MANIFEST_DIR, RESIDUE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    if args.summarize_only:
        report = rewrite_scaled_derivatives(
            read_csv_rows(TABLE_DIR / "scaled_benchmark_summary.csv"),
            read_csv_rows(TABLE_DIR / "scaled_solver_run_summary.csv"),
            read_csv_rows(TABLE_DIR / "scaled_proof_verification_summary.csv"),
        )
        print(json.dumps(report, indent=2, sort_keys=True), flush=True)
        return

    benchmarks: dict[str, Path] = {}
    benchmark_rows: list[dict[str, Any]] = []
    for name, (var_count, clauses, comments) in benchmark_specs().items():
        path = BENCH_DIR / f"{name}.cnf"
        write_once(path, dimacs(var_count, clauses, comments), force=args.force)
        benchmarks[name] = path
        benchmark_rows.append({
            "benchmark": f"scaled/{name}.cnf",
            "variables": var_count,
            "clauses": len(clauses),
            "path": rel(path),
            "sha256": sha_file(path),
            "size": path.stat().st_size,
        })

    solver_rows = solver_runs(benchmarks, force=args.force)
    proof_rows = proof_runs(benchmarks, force=args.force)

    solver_table = TABLE_DIR / "scaled_solver_run_summary.csv"
    proof_table = TABLE_DIR / "scaled_proof_verification_summary.csv"
    benchmark_table = TABLE_DIR / "scaled_benchmark_summary.csv"
    write_csv(solver_table, solver_rows, force=args.force)
    write_csv(proof_table, proof_rows, force=args.force)
    write_csv(benchmark_table, benchmark_rows, force=args.force)

    report = rewrite_scaled_derivatives(benchmark_rows, solver_rows, proof_rows)
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
