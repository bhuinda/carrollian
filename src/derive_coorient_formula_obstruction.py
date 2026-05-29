from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.generate_source import build_source_code

ROOT = Path(__file__).resolve().parents[1]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def dodecad_masks() -> np.ndarray:
    dodecads = build_source_code()["dodecads"]
    masks = []
    for v in dodecads:
        m = 0
        for i, b in enumerate(v):
            if b:
                m |= 1 << i
        masks.append(m)
    return np.array(masks, dtype=object)


def pc(x: int) -> int:
    return int(x).bit_count()


def derive_obstruction(
    coorient_npz: Path,
    out_json: Path | None = None,
    sample_window: int = 96,
) -> dict[str, Any]:
    z = np.load(coorient_npz, allow_pickle=True)
    gens = np.asarray(z["generator_permutations"], dtype=np.int64)
    masks = dodecad_masks()
    rows: list[dict[str, Any]] = []
    all_obstructed = True
    for gi, g in enumerate(gens):
        witness = None
        limit = min(sample_window, masks.size)
        for a in range(limit):
            for b in range(limit):
                before = pc(masks[a] & masks[b])
                after = pc(masks[int(g[a])] & masks[int(g[b])])
                if before != after:
                    witness = {
                        "source_pair": [int(a), int(b)],
                        "image_pair": [int(g[a]), int(g[b])],
                        "intersection_before": int(before),
                        "intersection_after": int(after),
                    }
                    break
            if witness is not None:
                break
        rows.append({
            "generator": gi,
            "is_coordinate_permutation_candidate": witness is None,
            "intersection_obstruction_witness": witness,
        })
        if witness is None:
            all_obstructed = False

    result: dict[str, Any] = {
        "schema": "d20.constructor.coorient_formula_obstruction@1",
        "constructor_status": "COORIENT_GENERATORS_NOT_M24_COORDINATE_PERMUTATIONS_PASS" if all_obstructed else "COORIENT_GENERATORS_COORDINATE_TEST_INCONCLUSIVE",
        "predicate": "is integral",
        "claim": "The fixed coorient Gamma generators are not induced by ordinary coordinate permutations of the 24 Golay coordinates; they require an additional coorient action on the dodecad shell.",
        "test": "A coordinate permutation preserves pairwise dodecad intersection cardinalities. Each supplied coorient generator violates this invariant on an explicit pair of generated dodecads.",
        "coorient_npz": str(coorient_npz.relative_to(ROOT)) if coorient_npz.is_relative_to(ROOT) else str(coorient_npz),
        "degree": int(gens.shape[1]),
        "generator_count": int(gens.shape[0]),
        "sample_window": int(sample_window),
        "rows": rows,
        "remaining_boundary_sharpened": [
            "do not search only inside M24/sextet coordinate stabilizers for Gamma; the missing formula must include a lifted coorient action on the dodecad shell",
            "derive the four coorient generator permutations from that typed lifted action rather than storing them as 2576-point permutations",
        ],
    }
    result["constructor_result_sha256"] = hashlib.sha256(canonical({k: v for k, v in result.items() if k != "constructor_result_sha256"})).hexdigest()
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Show that the fixed coorient Gamma generators are not ordinary M24 coordinate permutations.")
    ap.add_argument("--coorient", default="data/coorient/be3_coorient_generators.npz")
    ap.add_argument("--out-json", default="generated/coorient_formula_obstruction_report.json")
    ap.add_argument("--sample-window", type=int, default=96)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = derive_obstruction(ROOT / args.coorient, ROOT / args.out_json, args.sample_window)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    if not str(result.get("constructor_status", "")).endswith("PASS"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
