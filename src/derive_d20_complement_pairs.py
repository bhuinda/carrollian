from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import numpy as np
from pathlib import Path
from .d20_optics_common import LABELS, WEIGHTS, EPSILON_0, triples, face_name, mu, complement, sha_json, write_json


def derive(out_npz: Path, out_json: Path) -> dict:
    faces = triples()
    face_to_idx = {f:i for i,f in enumerate(faces)}
    product_all = int(np.prod(np.array(WEIGHTS, dtype=object)))
    pairs = []
    seen = set()
    for f in faces:
        fc = complement(f)
        key = tuple(sorted([face_to_idx[f], face_to_idx[fc]]))
        if key in seen:
            continue
        seen.add(key)
        p = mu(f) * mu(fc)
        pairs.append({
            "face": face_name(f),
            "complement": face_name(fc),
            "mu_face": mu(f),
            "mu_complement": mu(fc),
            "product": p,
            "product_over_epsilon0_squared": p // (EPSILON_0 * EPSILON_0),
        })
    all_equal = all(p["product"] == product_all for p in pairs)
    report = {
        "schema": "d20.optics.complement_pairs@1",
        "constructor_status": "D20_COMPLEMENT_PAIR_ETENDUE_PASS" if all_equal and product_all == 6912 * EPSILON_0 * EPSILON_0 else "D20_COMPLEMENT_PAIR_ETENDUE_FAIL",
        "object": "d20",
        "labels": LABELS,
        "weights": dict(zip(LABELS, WEIGHTS)),
        "complement_pair_count": len(pairs),
        "product_all_weights": product_all,
        "product_identity": f"{product_all} = 6912 * epsilon0^2",
        "product_over_epsilon0_squared": product_all // (EPSILON_0 * EPSILON_0),
        "all_complement_products_equal": all_equal,
        "pairs": pairs,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, product=np.array([product_all], dtype=object), pairs=np.array([(p["face"], p["complement"]) for p in pairs], dtype=object))
    write_json(out_json, report)
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(derive(Path("generated/d20_complement_pairs.npz"), Path("generated/d20_complement_pairs_report.json")), indent=2, sort_keys=True))
