#!/usr/bin/env python3
"""
Verifier skeleton for Height-Coherent Action-Return Intertwining.

This is intentionally not a proof by itself. It checks the exact identity

    pi_Foam33 @ R_hc[g] == R_Foam[g] @ pi_Foam33

once the projection matrix and action-return generator matrices are supplied.
"""
from __future__ import annotations
import argparse
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pi", required=True, help="33x56 projection matrix .npy")
    ap.add_argument("--r-hc", required=True, nargs="+", help="56x56 R_hc generator matrices .npy")
    ap.add_argument("--r-foam", required=True, nargs="+", help="33x33 R_Foam generator matrices .npy")
    ap.add_argument("--prime", type=int, default=1000003)
    args = ap.parse_args()
    if len(args.r_hc) != len(args.r_foam):
        raise SystemExit("R_hc and R_Foam generator counts differ")
    p = args.prime
    pi = np.load(args.pi) % p
    if pi.shape != (33,56):
        raise SystemExit(f"bad pi shape: {pi.shape}")
    failures = []
    for i, (hc_path, foam_path) in enumerate(zip(args.r_hc, args.r_foam)):
        Rhc = np.load(hc_path) % p
        Rf = np.load(foam_path) % p
        if Rhc.shape != (56,56):
            raise SystemExit(f"bad R_hc shape for {hc_path}: {Rhc.shape}")
        if Rf.shape != (33,33):
            raise SystemExit(f"bad R_Foam shape for {foam_path}: {Rf.shape}")
        diff = (pi @ Rhc - Rf @ pi) % p
        nz = int(np.count_nonzero(diff))
        if nz:
            failures.append((i, hc_path, foam_path, nz))
    if failures:
        print("FAIL", failures[:10], "total", len(failures))
        raise SystemExit(1)
    print("PASS: height-coherent action-return intertwining verified for", len(args.r_hc), "generators")

if __name__ == "__main__":
    main()
