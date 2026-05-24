import argparse, subprocess, sys, json
from pathlib import Path

SCRIPTS = [
    "01_packet_idempotents_peirce.py",
    "02_wedderburn_from_d20json.py",
    "03_rho20_scalar_representation.py",
    "04_rho20_kernel_quotient.py",
    "05_rho20_residue_intersections.py",
    "06_pentagon_sample.py",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True)
    ap.add_argument("--t985", required=True)
    ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample", type=int, default=10000)
    args = ap.parse_args()
    src = Path(__file__).resolve().parent
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    logs = []
    for s in SCRIPTS:
        cmd = [sys.executable, str(src/s), "--d20", args.d20, "--t985", args.t985, "--quotients", args.quotients, "--out", str(out)]
        if s == "06_pentagon_sample.py":
            cmd += ["--sample", str(args.sample)]
        proc = subprocess.run(cmd, text=True, capture_output=True)
        logs.append({"script": s, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
        if proc.returncode != 0:
            (out/"run_all_log.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
            raise SystemExit(proc.returncode)
    (out/"run_all_log.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
    print(json.dumps({"status": "RUN_ALL_PASS", "out": str(out)}, indent=2))

if __name__ == "__main__":
    main()
