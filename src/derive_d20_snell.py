from __future__ import annotations

import itertools, numpy as np
from pathlib import Path
from .d20_optics_common import LABELS, WEIGHTS, triples, face_name, mu, sha_json, write_json


def derive(out_npz: Path, out_json: Path) -> dict:
    checks = []
    ok = True
    for a,b in itertools.combinations(range(6), 2):
        rest = [i for i in range(6) if i not in (a,b)]
        T = WEIGHTS[a] * WEIGHTS[b]
        for x,y in itertools.combinations(rest, 2):
            f = tuple(sorted((a,b,x)))
            g = tuple(sorted((a,b,y)))
            lhs_f = mu(f) // WEIGHTS[x]
            lhs_g = mu(g) // WEIGHTS[y]
            ratio_num = mu(g)
            ratio_den = mu(f)
            expected_num = WEIGHTS[y]
            expected_den = WEIGHTS[x]
            # Compare ratios by cross multiplication.
            ratio_ok = ratio_num * expected_den == ratio_den * expected_num
            pass_row = lhs_f == T and lhs_g == T and ratio_ok
            ok = ok and pass_row
            checks.append({
                "shared_duad": (LABELS[a], LABELS[b]),
                "face_f": face_name(f),
                "face_g": face_name(g),
                "normal_f": LABELS[x],
                "normal_g": LABELS[y],
                "T_D": T,
                "mu_f_over_normal_weight": lhs_f,
                "mu_g_over_normal_weight": lhs_g,
                "mu_g_over_mu_f": f"{ratio_num}/{ratio_den}",
                "refractive_weight_ratio": f"{expected_num}/{expected_den}",
                "passes": pass_row,
            })
    report = {
        "schema": "d20.optics.snell@1",
        "constructor_status": "D20_SNELL_PASS" if ok else "D20_SNELL_FAIL",
        "object": "d20",
        "labels": LABELS,
        "weights": dict(zip(LABELS, WEIGHTS)),
        "law": "For f={a,b,x}, g={a,b,y}, mu(f)/w_x = mu(g)/w_y = w_a w_b, and mu(g)/mu(f)=w_y/w_x.",
        "shared_duad_count": 15,
        "pair_checks": len(checks),
        "all_checks_pass": ok,
        "checks_sample": checks[:24],
        "all_checks_sha256": sha_json(checks),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, weights=np.array(WEIGHTS, dtype=np.int64), pass_flag=np.array([ok], dtype=np.bool_))
    write_json(out_json, report)
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(derive(Path("generated/d20_snell.npz"), Path("generated/d20_snell_report.json")), indent=2, sort_keys=True))
