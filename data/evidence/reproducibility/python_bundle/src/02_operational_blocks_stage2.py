from pathlib import Path
import argparse, json, random
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=20000)
    args = ap.parse_args()
    out = Path(args.out) / "02_operational_blocks_stage2"; out.mkdir(parents=True, exist_ok=True)

    d20, tz, qz = load_inputs(Path(args.d20), Path(args.t985), Path(args.quotients))
    triples = tz["triples"].astype("int64"); M = tz["M"].astype("int64")
    block_i = qz["block_i"].astype("int16"); block_j = qz["block_j"].astype("int16")
    pairmap = build_pairmap(triples)
    identity_candidates = [6,163,227,349,618,893]

    identity_rows, violations = [], []
    for obj, e in enumerate(identity_candidates):
        left_targets = np.where(block_i == obj)[0]
        right_targets = np.where(block_j == obj)[0]
        left_ok = left_bad = right_ok = right_bad = 0
        for r in left_targets:
            prod = pairmap.get((e, int(r)), [])
            ok = len(prod) == 1 and prod[0][0] == int(r) and prod[0][1] == 1
            left_ok += int(ok); left_bad += int(not ok)
            if not ok and len(violations) < 50: violations.append({"object": obj, "side": "left", "relation": int(r), "product": str(prod[:5])})
        for r in right_targets:
            prod = pairmap.get((int(r), e), [])
            ok = len(prod) == 1 and prod[0][0] == int(r) and prod[0][1] == 1
            right_ok += int(ok); right_bad += int(not ok)
            if not ok and len(violations) < 50: violations.append({"object": obj, "side": "right", "relation": int(r), "product": str(prod[:5])})
        identity_rows.append({"object": obj, "idempotent": e, "left_ok": left_ok, "left_bad": left_bad, "right_ok": right_ok, "right_bad": right_bad, "pass": left_bad == 0 and right_bad == 0})

    idemp_rows = []
    for a in range(6):
        for b in range(6):
            ea, eb = identity_candidates[a], identity_candidates[b]
            prod = pairmap.get((ea, eb), [])
            expected = [(ea, 1)] if a == b else []
            idemp_rows.append({"i": a, "j": b, "product": str(prod), "expected": str(expected), "pass": prod == expected})

    block_count = np.zeros((6,6), dtype=int)
    for r in range(985): block_count[block_i[r], block_j[r]] += 1

    noncomp = outviol = 0
    comp_rows = []
    comp = {(i,j,k): {"i": i, "j": j, "k": k, "tensor_entries": 0, "coefficient_mass": 0} for i in range(6) for j in range(6) for k in range(6)}
    for a,b,c,p in triples:
        i,j = int(block_i[a]), int(block_j[a]); j2,k = int(block_i[b]), int(block_j[b])
        ci,cj = int(block_i[c]), int(block_j[c])
        if j != j2: noncomp += 1; continue
        if (ci,cj) != (i,k): outviol += 1
        comp[(i,j,k)]["tensor_entries"] += 1
        comp[(i,j,k)]["coefficient_mass"] += int(p)
    comp_rows = list(comp.values())

    write_csv(out / "local_unit_idempotents.csv", identity_rows)
    write_csv(out / "local_unit_violations.csv", violations)
    write_csv(out / "orthogonal_idempotent_products.csv", idemp_rows)
    write_csv(out / "peirce_block_matrix.csv", [{"i": i, "j": j, "count": int(block_count[i,j]), "M": int(M[i,j])} for i in range(6) for j in range(6)])
    write_csv(out / "peirce_composition_table.csv", comp_rows)

    cert = {
        "schema": "repro.operational_blocks_stage2@1",
        "status": "PASS",
        "local_units_pass": all(r["pass"] for r in identity_rows),
        "orthogonal_idempotents_pass": all(r["pass"] for r in idemp_rows),
        "block_count_matrix_matches_M": bool(np.all(block_count == M)),
        "noncomposable_violations": noncomp,
        "output_block_violations": outviol,
    }
    cert["status"] = "PASS" if all([cert["local_units_pass"], cert["orthogonal_idempotents_pass"], cert["block_count_matrix_matches_M"], noncomp == 0, outviol == 0]) else "FAIL"
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
