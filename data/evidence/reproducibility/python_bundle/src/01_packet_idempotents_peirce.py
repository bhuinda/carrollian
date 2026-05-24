import argparse, json, numpy as np
from pathlib import Path
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out) / "01_packet_idempotents_peirce"
    d20, tz, qz = load_inputs(args.d20, args.t985, args.quotients)
    triples = tz["triples"].astype(np.int64); M = tz["M"].astype(np.int64)
    block_i = qz["block_i"].astype(np.int16); block_j = qz["block_j"].astype(np.int16)
    pairmap = build_pairmap(triples)
    ids = [6, 163, 227, 349, 618, 893]

    local_rows = []
    for obj, e in enumerate(ids):
        left = np.where(block_i == obj)[0]; right = np.where(block_j == obj)[0]
        left_bad = right_bad = 0
        for r in left:
            prod = pairmap.get((e, int(r)), [])
            left_bad += not (len(prod) == 1 and prod[0] == (int(r), 1))
        for r in right:
            prod = pairmap.get((int(r), e), [])
            right_bad += not (len(prod) == 1 and prod[0] == (int(r), 1))
        local_rows.append({"object": obj, "idempotent": e, "left_checked": len(left), "left_bad": int(left_bad), "right_checked": len(right), "right_bad": int(right_bad), "pass": left_bad == 0 and right_bad == 0})

    orth_rows = []
    for i, ei in enumerate(ids):
        for j, ej in enumerate(ids):
            prod = pairmap.get((ei, ej), [])
            exp = [(ei, 1)] if i == j else []
            orth_rows.append({"i": i, "j": j, "product": str(prod), "expected": str(exp), "pass": prod == exp})

    block_count = np.zeros((6,6), dtype=int)
    for r in range(985):
        block_count[block_i[r], block_j[r]] += 1

    noncomp = outviol = 0
    comp = {(i,j,k): {"i": i, "j": j, "k": k, "entries": 0, "mass": 0} for i in range(6) for j in range(6) for k in range(6)}
    for a, b, c, p in triples:
        i, j = int(block_i[a]), int(block_j[a])
        j2, k = int(block_i[b]), int(block_j[b])
        ci, cj = int(block_i[c]), int(block_j[c])
        if j != j2:
            noncomp += 1
            continue
        if (ci, cj) != (i, k):
            outviol += 1
        comp[(i,j,k)]["entries"] += 1
        comp[(i,j,k)]["mass"] += int(p)

    write_csv(out / "local_unit_idempotents.csv", local_rows)
    write_csv(out / "orthogonal_idempotents.csv", orth_rows)
    write_csv(out / "peirce_block_matrix.csv", [{"i":i,"j":j,"count":int(block_count[i,j]),"M":int(M[i,j])} for i in range(6) for j in range(6)])
    write_csv(out / "peirce_composition_table.csv", list(comp.values()))
    cert = {
        "status": "PASS" if all(r["pass"] for r in local_rows) and all(r["pass"] for r in orth_rows) and np.all(block_count == M) and noncomp == 0 and outviol == 0 else "FAIL",
        "local_units_pass": all(r["pass"] for r in local_rows),
        "orthogonal_idempotents_pass": all(r["pass"] for r in orth_rows),
        "block_count_matrix_matches_M": bool(np.all(block_count == M)),
        "noncomposable_violations": noncomp,
        "output_block_violations": outviol,
    }
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
