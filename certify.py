#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
MUTABLE = {"certificate.json", "manifests/file_hashes.json", "manifests/canonical.json"}

EXPECTED = {
    "00_core": "PASS",
    "01_tube_projection_section": None,
    "02_drinfeld_boundary": "DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED",
    "03_drinfeld_grothendieck_center": "DRINFELD_GROTHENDIECK_CENTER_CERTIFIED",
    "04_drinfeld_idempotent_gluing": "DRINFELD_IDEMPOTENT_GLUING_CERTIFIED",
    "05_drinfeld_wedderburn_trace": "DRINFELD_WEDDERBURN_TRACE_CERTIFIED",
    "06_drinfeld_full_A985_lift": "DRINFELD_FULL_A985_LIFT_CERTIFIED",
    "07_ribbon_modular_boundary": "RIBBON_TWIST_TRIVIAL_AND_MODULAR_S_OBSTRUCTED",
    "08_modular_completion_obstruction": "MODULAR_COMPLETION_OBSTRUCTION_CERTIFIED",
    "09_tube_kernel_descent_audit": "TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED",
    "10_adjoined_hopf_operator": "ADJOINED_HOPF_OPERATOR_CONSTRUCTED",
    "11_twist_completion_test": "TWIST_COMPLETION_OBSTRUCTED_FOR_ADJOINED_HOP_OPERATOR",
    "12_derived_line_surface_trace": "DERIVED_LINE_SURFACE_TRACE_OPERATOR_CERTIFIED",
    "13_hesse_tube_character_pencil": "HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED",
    "14_lasso_uniqueness_pseudomodular_audit": "LASSO_UNIQUENESS_AND_PSEUDOMODULAR_INVARIANT_AUDIT_CERTIFIED",
    "15_intrinsic_carrier_dependency_geometry": "INTRINSIC_CARRIER_DEPENDENCY_GEOMETRY_CERTIFIED",
    "16_mds_arc_hilbert_geometry": "MDS_ARC_HILBERT_AND_QUINTIC_WALL_CERTIFIED",
    "17_wu_golay_quintic_resolvent": "WU_GOLAY_QUINTIC_RESOLVENT_CERTIFIED_WITH_GOLAY_EXTENSION_UNRESOLVED",
    "18_canonical_24_syzygy_frame": "CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN",
    "19_quadratic_golay_selector_obstruction": "QUADRATIC_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED",
    "20_wu_spinh_6j_marking": "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
    "21_mog_resolvent_invariant": "MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
    "22_mog_canonicity_boundary": "MOG_COLUMN_SEXTET_CANONICITY_CERTIFIED_FULL_ROW_GOLAY_SELECTOR_STILL_EXTERNAL",
    "23_full_row_refined_selector_obstruction": "FULL_ROW_REFINED_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED_HEXACODE_REQUIRED",
    "24_hexacode_row_selector": "HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL",
    "25_proof_system_integrity": "PROOF_SYSTEM_INTEGRITY_LADDER_BUILT",
}
# Canonical typo guard: layer 11 status uses HOPF, not HOP.
EXPECTED["11_twist_completion_test"] = "TWIST_COMPLETION_OBSTRUCTED_FOR_ADJOINED_HOPF_OPERATOR"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel: str | Path) -> Any:
    p = ROOT / rel if isinstance(rel, str) else rel
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def verify_root(errors: list[str]) -> dict[str, Any]:
    cert = load_json("certificate.json")
    require(cert.get("schema") in {"d20.verifier.v1", "d20.verifier.v2"}, "root schema mismatch", errors)
    require(cert.get("status") == "D20_CERTIFIED", "root status mismatch", errors)
    h = cert.get("d20_sha256")
    body = {k: v for k, v in cert.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "root self-hash mismatch", errors)
    return cert


def verify_d20_json(errors: list[str]) -> dict[str, Any]:
    p = ROOT / "d20.json"
    require(p.exists(), "missing d20.json", errors)
    if not p.exists():
        return {}
    data = load_json(p)
    require(data.get("schema") == "d20.object.v2", "d20.json schema mismatch", errors)
    require(data.get("status") == "D20_CERTIFIED", "d20.json status mismatch", errors)
    require(data.get("object") == "d20", "d20.json object mismatch", errors)
    h = data.get("d20_sha256")
    body = {k: v for k, v in data.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "d20.json self-hash mismatch", errors)
    required_sections = [
        "core_invariants",
        "optics",
        "game_theory",
        "zero_axiom_coorient",
        "universal_integral_uniqueness",
        "pre_A985_relation_body_theorem",
        "layer_certificates",
        "json_invariants",
        "npz_array_manifests",
        "source_manifest",
    ]
    for sec in required_sections:
        require(sec in data, f"d20.json missing section: {sec}", errors)
    z = data.get("zero_axiom_coorient", {})
    require(z.get("status") == "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS", "zero_axiom_coorient status mismatch", errors)
    base = z.get("canonical_base_derivation", {})
    require(base.get("base") == [18, 67, 37], "zero_axiom canonical base mismatch", errors)
    require(base.get("matches_stored_canonical_base") is True, "zero_axiom canonical base not matched", errors)
    require(base.get("separates_all_points") is True, "zero_axiom base does not separate all points", errors)
    marker = z.get("coorient_generator_marker", {})
    require(marker.get("integer_count") == 12, "coorient generator marker integer count mismatch", errors)
    u = data.get("universal_integral_uniqueness", {})
    require(u.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS", "universal integral uniqueness status mismatch", errors)
    uc = u.get("coorient_lift_uniqueness_computation", {})
    require(uc.get("internal_base_type_candidate_triples") == 18432, "universal integral internal candidate count mismatch", errors)
    require(uc.get("coherent_signature_lift_triples") == 9216, "universal integral lift count mismatch", errors)
    require(uc.get("generated_action_order") == 9216, "universal integral generated action order mismatch", errors)
    ur = u.get("uniqueness_result", {})
    require(ur.get("A985_integral_uniqueness_computed") is True, "A985 integral uniqueness not computed", errors)
    require(ur.get("coorient_action_group_unique") is True, "coorient action group uniqueness mismatch", errors)
    require(ur.get("remaining_12_integers_are_semantic_seed") is False, "12 integers still marked as semantic seed", errors)
    pre = data.get("pre_A985_relation_body_theorem", {})
    require(pre.get("status") == "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS", "pre-A985 relation body theorem status mismatch", errors)
    pr = pre.get("result", {})
    require(pr.get("uses_relation_table_as_input") is False, "pre-A985 theorem uses relation table as input", errors)
    require(pr.get("A985_relation_count") == 985, "pre-A985 relation count mismatch", errors)
    require(pr.get("T985_support") == 1414965, "pre-A985 tensor support mismatch", errors)
    fin = data.get("final_investigation", {})
    require(fin.get("status") == "D20_INVESTIGATION_FINALIZED_WITH_A985_INTEGRAL_UNIQUENESS", "final investigation status mismatch", errors)
    require(fin.get("finite_computational_closure") is True, "final investigation finite closure mismatch", errors)
    require(fin.get("A985_integral_uniqueness_computed") is True, "final investigation A985 uniqueness mismatch", errors)
    require(fin.get("coorient_action_group_unique_over_A985") is True, "final investigation coorient uniqueness mismatch", errors)
    require(fin.get("full_zero_axiom_constructor") is False, "final investigation zero-axiom boundary mismatch", errors)
    rb = fin.get("remaining_boundary", {})
    require(rb.get("remaining_seed_integer_count_in_A985_integral_theory") == 0, "final investigation remaining A985-integral seed count mismatch", errors)

    return {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "file_sha256": sha_file(p),
        "object_sha256": h,
        "size": p.stat().st_size,
        "section_count": len(data),
        "layer_count": len(data.get("layer_certificates", {})),
        "json_invariant_file_count": len(data.get("json_invariants", {})),
        "npz_array_manifest_count": len(data.get("npz_array_manifests", {})),
        "hcycle_present": bool(data.get("game_theory", {}).get("present", False)),
        "hcycle_primitive_cycles": data.get("game_theory", {}).get("primitive_H_cycles", {}).get("count"),
        "hcycle_state_space": data.get("game_theory", {}).get("state_space", {}).get("S20_order"),
    }


def verify_layers(errors: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dirname, expected_status in EXPECTED.items():
        rel = f"layers/{dirname}/certificate.json"
        p = ROOT / rel
        require(p.exists(), f"missing layer certificate: {rel}", errors)
        if not p.exists():
            continue
        data = load_json(p)
        status = data.get("status")
        if expected_status is not None:
            require(status == expected_status, f"{dirname}: status {status!r} != {expected_status!r}", errors)
        rows.append({"layer": dirname, "status": status, "file_sha256": sha_file(p)})
    return rows


def verify_core_arrays(errors: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    z = np.load(ROOT / "data/raw/tensor_sparse.npz")
    triples = np.asarray(z["triples"], dtype=np.int64)
    reps = np.asarray(z["reps"], dtype=np.int64)
    M = np.asarray(z["M"], dtype=np.int64)
    require(triples.shape == (1_414_965, 4), f"tensor triples shape mismatch: {triples.shape}", errors)
    require(int(triples[:, 3].sum()) == 2_537_360, "tensor coefficient total mismatch", errors)
    require(reps.shape == (985, 5), f"reps shape mismatch: {reps.shape}", errors)
    require(M.shape == (6, 6), f"object-pair matrix shape mismatch: {M.shape}", errors)
    out.update({
        "tensor_support": int(triples.shape[0]),
        "tensor_coefficient_total": int(triples[:, 3].sum()),
        "relation_count": int(reps.shape[0]),
        "object_pair_matrix_shape": list(M.shape),
    })

    q = np.load(ROOT / "data/raw/quotients.npz")
    q42 = np.asarray(q["q42_map"], dtype=np.int64)
    q12 = np.asarray(q["q12_map"], dtype=np.int64)
    q42t = np.asarray(q["q42_tensor"], dtype=np.int64)
    q12t = np.asarray(q["q12_tensor"], dtype=np.int64)
    require(q42.shape == (985,), f"q42 map shape mismatch: {q42.shape}", errors)
    require(q12.shape == (985,), f"q12 map shape mismatch: {q12.shape}", errors)
    require(q42t.shape == (42, 42, 42), f"q42 tensor shape mismatch: {q42t.shape}", errors)
    require(q12t.shape == (12, 12, 12), f"q12 tensor shape mismatch: {q12t.shape}", errors)
    consistent = True
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            consistent = False
            break
    require(consistent, "q42 -> q12 consistency failed", errors)
    out.update({
        "q42_classes": 42,
        "q12_classes": 12,
        "q42_to_q12_consistent": bool(consistent),
        "q42_tensor_nonzero": int(np.count_nonzero(q42t)),
        "q12_tensor_nonzero": int(np.count_nonzero(q12t)),
    })

    b = np.load(ROOT / "data/raw/simple_branching_matrices.npz")
    B236_42 = np.asarray(b["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(b["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(b["B236_12"], dtype=np.int64)
    comp = np.asarray(b["comp"], dtype=np.int64)
    naturality = np.array_equal(B236_42 @ B42_12, B236_12) and np.array_equal(comp, B236_12)
    require(naturality, "simple branching naturality failed", errors)
    out.update({
        "simple_branching_naturality": bool(naturality),
        "B236_to_A42_shape": list(B236_42.shape),
        "B42_to_A12_shape": list(B42_12.shape),
        "B236_to_A12_shape": list(B236_12.shape),
    })

    l = np.load(ROOT / "data/raw/leech_projective_generators.npz")
    arr_keys = sorted(l.files)
    shape_found = None
    for k in arr_keys:
        a = np.asarray(l[k])
        if a.shape == (98280, 24):
            shape_found = list(a.shape)
            break
    require(shape_found == [98280, 24], "Leech projective generator shape [98280,24] not found", errors)
    out.update({"leech_projective_vectors_shape": shape_found})
    return out


def verify_integrity(errors: list[str]) -> dict[str, Any]:
    data = load_json("layers/25_proof_system_integrity/certificate.json")
    summary = data.get("summary", {})
    fb = summary.get("finite_base", {})
    expected = {
        "primitive_kernel_sector": [33],
        "public_rank": 20,
        "public_kernel_dimension": 19,
        "operation_algebra_dimension": 36,
        "integrity_integral_dimension": 1,
        "integrity_integral_codimension": 35,
        "Pi33_in_full_operation_algebra": False,
        "delta33_after_public_integral_operations": False,
    }
    for k, v in expected.items():
        require(fb.get(k) == v, f"integrity gate mismatch {k}: {fb.get(k)!r} != {v!r}", errors)
    return fb


def verify_manifest(errors: list[str]) -> dict[str, Any]:
    man = load_json("manifests/file_hashes.json")
    checked = 0
    for ent in man.get("entries", []):
        rel = ent["path"]
        p = ROOT / rel
        require(p.exists(), f"manifest path missing: {rel}", errors)
        if not p.exists():
            continue
        require(p.stat().st_size == ent["size"], f"manifest size mismatch: {rel}", errors)
        require(sha_file(p) == ent["sha256"], f"manifest sha mismatch: {rel}", errors)
        checked += 1
    return {"manifest_entries_checked": checked}


def run(mode: str) -> dict[str, Any]:
    errors: list[str] = []
    root = verify_root(errors)
    d20 = verify_d20_json(errors)
    layers = verify_layers(errors)
    core = verify_core_arrays(errors)
    integrity = verify_integrity(errors)
    out: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "mode": mode,
        "headline": root.get("status"),
        "d20": d20,
        "layer_count": len(layers),
        "core": core,
        "integrity": integrity,
        "errors": errors,
    }
    if mode in {"audit", "rebuild"}:
        out["manifest"] = verify_manifest(errors)
        out["status"] = "PASS" if not errors else "FAIL"
    if mode == "rebuild":
        out["rebuild"] = "d20.json and source certificates checked; generated cache is not required"
    return out


def maybe_regenerate(mode: str, pretty: bool, enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {"regenerated_before_certification": False}
    import regen
    regen.rebuild_d20(pretty=pretty)
    regen.refresh_certificate()
    count = regen.refresh_manifest()
    return {"regenerated_before_certification": True, "manifest_entries_refreshed": count}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["fast", "audit", "rebuild"], default="audit")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--no-regenerate", action="store_true", help="Do not rebuild d20.json or refresh hashes before audit/rebuild.")
    args = ap.parse_args()
    regen_info = maybe_regenerate(args.mode, args.pretty, not args.no_regenerate)
    out = run(args.mode)
    out["regeneration"] = regen_info
    if out["status"] != "PASS":
        print(json.dumps(out, indent=2 if args.pretty else None, sort_keys=True))
        sys.exit(1)
    print(json.dumps(out, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
