from __future__ import annotations

import numpy as np
from pathlib import Path
from .d20_optics_common import LABELS, WEIGHTS, EPSILON_0, triples, face_name, mu, sha_json, write_json


def derive(out_npz: Path, out_json: Path) -> dict:
    faces = triples()
    face_mu = np.array([mu(f) for f in faces], dtype=np.int64)
    total = int(face_mu.sum())
    star = []
    for i, lab in enumerate(LABELS):
        s = int(sum(mu(f) for f in faces if i in f))
        star.append({"index": i, "label": lab, "mass": s, "mass_over_epsilon0": s // EPSILON_0})
    report = {
        "schema": "d20.optics.etendue@1",
        "constructor_status": "D20_ETENDUE_PASS" if total == 2275 * EPSILON_0 else "D20_ETENDUE_FAIL",
        "object": "d20",
        "normalization": "d20 is the public finite wavefront shell; Code(d20)=A985 is the hidden tensor body.",
        "labels": LABELS,
        "weights": dict(zip(LABELS, WEIGHTS)),
        "face_count": len(faces),
        "epsilon0": EPSILON_0,
        "epsilon0_factorization": "2^16 * 3^2",
        "E_d20": total,
        "E_d20_over_epsilon0": total // EPSILON_0,
        "E_d20_identity": f"{total} = {total // EPSILON_0} * epsilon0",
        "face_measure_definition": "mu({i,j,k}) = w_i w_j w_k",
        "star_masses": star,
        "star_mass_sum_over_epsilon0": int(sum(s["mass_over_epsilon0"] for s in star)),
        "star_mass_sum_identity": f"{sum(s['mass_over_epsilon0'] for s in star)} = 3 * {total // EPSILON_0}",
        "face_table": [
            {"face_index": n, "face": face_name(f), "mu": int(face_mu[n]), "mu_over_epsilon0": float(face_mu[n] / EPSILON_0)}
            for n, f in enumerate(faces)
        ],
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_npz,
        labels=np.array(LABELS, dtype=object),
        weights=np.array(WEIGHTS, dtype=np.int64),
        faces=np.array(faces, dtype=np.int64),
        face_mu=face_mu,
        epsilon0=np.array([EPSILON_0], dtype=np.int64),
        total=np.array([total], dtype=np.int64),
    )
    write_json(out_json, report)
    return report


if __name__ == "__main__":
    import json
    print(json.dumps(derive(Path("generated/d20_etendue.npz"), Path("generated/d20_etendue_report.json")), indent=2, sort_keys=True))
