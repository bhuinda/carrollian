from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, INTEGRITY_INVARIANTS, DATA, ROOT


THEOREM_ID = "sector33_residual_attachment"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

NONEXACT_REPORT = D20_INVARIANTS / "theorems" / "nonexact_optical_residue" / "report.json"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"

FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"
DRINFELD_BOUNDARY = DATA / "drinfeld" / "boundary.json"
LINE_SURFACE_TRACE = DATA / "modular" / "derived_line_surface_trace.json"
HESSE_TUBE_PENCIL = DATA / "modular" / "hesse_tube_character_pencil.json"
TUBE_PROJECTION_SECTION = DATA / "tube" / "projection_section.json"
TUBE_KERNEL_DESCENT_AUDIT = DATA / "tube" / "kernel_descent_audit.json"

PURE_C_NO_ESCAPE = INTEGRITY_INVARIANTS / "cvx_trace" / "reports" / "pure_c_no_escape_report.json"
X_EXTRACTOR_SEARCH = INTEGRITY_INVARIANTS / "cvx_trace" / "reports" / "x_extractor_bounded_search_report.json"
V_WALL_ACCOUNTING = INTEGRITY_INVARIANTS / "cvx_trace" / "reports" / "v_wall_crossing_accounting_report.json"
INTEGRITY_LADDER = INTEGRITY_INVARIANTS / "proof_system_integrity_ladder.csv"


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def split_ids(value: str) -> list[int]:
    return [int(part) for part in value.split()] if value else []


def parse_label(label: str) -> list[str]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label: {label!r}")
    return [part.strip() for part in body[1:-1].split(",") if part.strip()]


def load_cycle(cycle_id: int) -> dict[str, Any]:
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["cycle_id"]) == cycle_id:
                return {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "optical_action": int(row["optical_action"]),
                    "vertices": split_ids(row["vertices"]),
                    "vertex_labels": row["vertex_labels"],
                    "edge_ids": split_ids(row["edge_ids"]),
                    "turn_addresses": split_ids(row["turn_addresses"])
                    if row["turn_addresses"].replace(" ", "").isdigit()
                    else row["turn_addresses"].split(),
                }
    raise ValueError(f"cycle_id {cycle_id} not found in {rel(PRIMITIVE_CYCLES_CSV)}")


def load_cycle_edges(edge_ids: list[int]) -> list[dict[str, Any]]:
    wanted = set(edge_ids)
    rows: list[dict[str, Any]] = []
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edge_id = int(row["edge_id"])
            if edge_id in wanted:
                rows.append(
                    {
                        "edge_id": edge_id,
                        "u": int(row["u"]),
                        "v": int(row["v"]),
                        "u_label": row["u_label"],
                        "v_label": row["v_label"],
                        "shared_duad": row["shared_duad"],
                        "swapped_pair": row["swapped_pair"],
                        "interface_weight": int(row["interface_weight"]),
                        "selector_duad": row["selector_duad"],
                        "selector_choice": int(row["selector_choice"]),
                    }
                )
    return sorted(rows, key=lambda row: edge_ids.index(row["edge_id"]))


def channel_support(edge_rows: list[dict[str, Any]]) -> list[str]:
    channels: set[str] = set()
    for row in edge_rows:
        channels.update(parse_label(row["u_label"]))
        channels.update(parse_label(row["v_label"]))
        channels.update(parse_label(row["shared_duad"]))
        channels.update(parse_label(row["swapped_pair"]))
    order = ["B-", "B+", "V-", "V+", "S-", "S+"]
    return [name for name in order if name in channels]


def sector33_digest(profile: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "sector",
        "block_dimension",
        "regular_trace_block_square",
        "permutation_rank",
        "permutation_multiplicity",
        "character_support_size",
        "loop_coordinate_support_total",
        "pre_idempotent_support_size",
        "q42_nonzero_count",
        "q12_nonzero_count",
        "active_objects",
        "active_cy_sectors",
        "object_loop_coordinate_support",
        "object_pre_idempotent_counts",
        "identity_coefficients_signed",
        "spectral_signature",
    ]
    return {key: profile.get(key) for key in keys}


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    nonexact = load_json(NONEXACT_REPORT)
    full = load_json(FULL_A985_LIFT)
    boundary = load_json(DRINFELD_BOUNDARY)
    line_surface = load_json(LINE_SURFACE_TRACE)
    hesse = load_json(HESSE_TUBE_PENCIL)
    tube_section = load_json(TUBE_PROJECTION_SECTION)
    kernel_audit = load_json(TUBE_KERNEL_DESCENT_AUDIT)
    pure_c = load_json(PURE_C_NO_ESCAPE)
    x_search = load_json(X_EXTRACTOR_SEARCH)
    v_wall = load_json(V_WALL_ACCOUNTING)

    first = nonexact["derived"]["first_forced_nonzero_residual"]
    first_cycle_id = int(first["basis_cycle_ids"][0])
    cycle = load_cycle(first_cycle_id)
    cycle_edges = load_cycle_edges(cycle["edge_ids"])
    support = channel_support(cycle_edges)

    profiles = full["gluing_and_sector_profiles"]["sector_profiles"]
    sector33_rows = [profile for profile in profiles if int(profile["sector"]) == 33]
    public_zero_rows = [
        profile
        for profile in profiles
        if int(profile.get("q42_nonzero_count", -1)) == 0
        and int(profile.get("q12_nonzero_count", -1)) == 0
    ]
    sector33 = sector33_rows[0] if sector33_rows else {}
    field_prime = int(full["field"]["prime"])
    residual_integral = int(first["forced_res_A985_optical"])
    residual_mod_prime = residual_integral % field_prime

    checks = {
        "nonexact_obstruction_certified": nonexact.get("status") == "D20_NONEXACT_OPTICAL_RESIDUE_CERTIFIED"
        and bool(nonexact.get("all_checks_pass")),
        "first_obstruction_mask_is_256": int(first["mask"]) == 256,
        "first_obstruction_is_cycle_8": first["basis_cycle_ids"] == [8] and first_cycle_id == 8,
        "first_obstruction_action_is_374784": int(first["total_optical_action"]) == 374784,
        "first_residual_is_minus_action": residual_integral == -int(first["total_optical_action"]),
        "first_residual_nonzero_over_integers": residual_integral != 0,
        "first_residual_nonzero_mod_field": residual_mod_prime != 0,
        "cycle_8_table_matches_nonexact_witness": cycle["optical_action"] == int(first["total_optical_action"])
        and cycle["edge_ids"] == [11, 1, 2, 22, 21],
        "cycle_8_edges_are_present": len(cycle_edges) == len(cycle["edge_ids"]),
        "sector33_exists_once": len(sector33_rows) == 1,
        "sector33_is_unique_public_zero_sector": len(public_zero_rows) == 1
        and bool(public_zero_rows)
        and int(public_zero_rows[0]["sector"]) == 33,
        "sector33_signature_matches_public_zero_obstruction": bool(sector33)
        and int(sector33.get("block_dimension", -1)) == 2
        and int(sector33.get("permutation_rank", -1)) == 36
        and int(sector33.get("character_support_size", -1)) == 56
        and sector33.get("active_objects") == ["B+", "S+"],
        "drinfeld_boundary_certified": boundary.get("status") == "DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED",
        "half_braiding_nullity_is_39": boundary.get("half_braiding_solve", {}).get("nullity") == 39
        and boundary.get("half_braiding_solve", {}).get("nullity_matches_A985_center_dimension") is True,
        "tube_projection_section_certified": tube_section.get("section", {}).get("projection_section_identity") is True
        and tube_section.get("projection", {}).get("projection_surjective") is True
        and tube_section.get("projection", {}).get("tube_pair_basis_total") == 44521
        and tube_section.get("projection", {}).get("closed_loop_quotient_dimension") == 297
        and tube_section.get("projection", {}).get("projection_kernel_dimension") == 44224,
        "tube_kernel_descent_audit_certified": kernel_audit.get("status") == "TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED",
        "line_surface_trace_separates_all_sectors": line_surface.get("status")
        == "DERIVED_LINE_SURFACE_TRACE_OPERATOR_CERTIFIED"
        and line_surface.get("pairings", {}).get("full_relation_pairing_separates_all_39_sectors") is True
        and line_surface.get("secondary_surface_insertion", {}).get("splits_all_39_sectors") is True,
        "hesse_tube_pencil_sees_all_39_sectors": hesse.get("status") == "HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED"
        and hesse.get("pencil_cut_checks", {}).get("unique_Hesse_pencils") == 39
        and hesse.get("pencil_cut_checks", {}).get("unique_projective_cubic_points") == 39
        and hesse.get("pencil_cut_checks", {}).get("Hesse_R_residuals_all_zero") is True,
        "accepted_pure_c_traces_do_not_extract_e33": pure_c.get("status") == "PURE_C_NO_ESCAPE_WITNESS_PASS"
        and pure_c.get("accepted_antecedent_holds") is True,
        "bounded_x_search_finds_no_extractor": x_search.get("status")
        == "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND"
        and x_search.get("result", {}).get("x_extractor_present") is False,
        "visible_v_accounting_has_no_current_v_events": v_wall.get("status")
        == "V_WALL_CROSSING_ACCOUNTING_NO_V_EVENTS"
        and v_wall.get("result", {}).get("v_accounting_passed") is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR33_RESIDUAL_ATTACHMENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector33_residual_attachment.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The first non-exact D20 optical closed-return obstruction has a certified A985 sector interface: "
            "its forced scalar residual is paired with the unique public-zero Drinfeld/Wedderburn sector 33, "
            "which is invisible to A42/A12 public terminal traces but visible to the certified tube/Hesse and "
            "line-surface trace data."
        ),
        "inputs": {
            "nonexact_optical_residue_report": {
                "path": rel(NONEXACT_REPORT),
                "sha256": sha_file(NONEXACT_REPORT),
            },
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
            "d20_edges": {
                "path": rel(D20_EDGES_CSV),
                "sha256": sha_file(D20_EDGES_CSV),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "drinfeld_boundary": {
                "path": rel(DRINFELD_BOUNDARY),
                "sha256": sha_file(DRINFELD_BOUNDARY),
            },
            "line_surface_trace": {
                "path": rel(LINE_SURFACE_TRACE),
                "sha256": sha_file(LINE_SURFACE_TRACE),
            },
            "hesse_tube_pencil": {
                "path": rel(HESSE_TUBE_PENCIL),
                "sha256": sha_file(HESSE_TUBE_PENCIL),
            },
            "tube_projection_section": {
                "path": rel(TUBE_PROJECTION_SECTION),
                "sha256": sha_file(TUBE_PROJECTION_SECTION),
            },
            "tube_kernel_descent_audit": {
                "path": rel(TUBE_KERNEL_DESCENT_AUDIT),
                "sha256": sha_file(TUBE_KERNEL_DESCENT_AUDIT),
            },
            "pure_c_no_escape": {
                "path": rel(PURE_C_NO_ESCAPE),
                "sha256": sha_file(PURE_C_NO_ESCAPE),
            },
            "x_extractor_search": {
                "path": rel(X_EXTRACTOR_SEARCH),
                "sha256": sha_file(X_EXTRACTOR_SEARCH),
            },
            "v_wall_accounting": {
                "path": rel(V_WALL_ACCOUNTING),
                "sha256": sha_file(V_WALL_ACCOUNTING),
            },
            "integrity_ladder": {
                "path": rel(INTEGRITY_LADDER),
                "sha256": sha_file(INTEGRITY_LADDER),
            },
        },
        "definitions": {
            "sector_attachment": (
                "A pairing of a forced boundary residual with a certified hidden A985 sector witness. "
                "The pairing is an interface certificate, not a full internal module projection."
            ),
            "public_zero_sector": "An A985 Drinfeld/Wedderburn sector with q42_nonzero_count=q12_nonzero_count=0.",
            "tube_visible": (
                "The sector survives the 39-sector half-braiding cut and is separated by certified "
                "line-surface/full-relation and Hesse-tube character data."
            ),
        },
        "derived": {
            "first_boundary_obstruction": {
                "mask": int(first["mask"]),
                "basis_cycle_ids": first["basis_cycle_ids"],
                "cycle": cycle,
                "edges": cycle_edges,
                "boundary_channel_support": support,
                "optical_action": int(first["total_optical_action"]),
                "forced_res_A985_optical_Z": residual_integral,
                "field_prime": field_prime,
                "forced_res_A985_optical_mod_prime": residual_mod_prime,
            },
            "sector_attachment": {
                "boundary_cycle_id": first_cycle_id,
                "a985_sector": 33,
                "a985_sector_name": "Pi_33",
                "attachment_type": "unique public-zero, tube-visible A985 sector interface",
                "public_terminal_shadow": {
                    "A42": "zero",
                    "A12": "zero",
                    "q42_nonzero_count": sector33.get("q42_nonzero_count"),
                    "q12_nonzero_count": sector33.get("q12_nonzero_count"),
                },
                "residual_integral": residual_integral,
                "residual_mod_prime": residual_mod_prime,
                "why_this_sector": [
                    "sector 33 is the unique Drinfeld/Wedderburn sector with zero A42 and A12 terminal shadows",
                    "sector 33 remains visible to certified full relation, line-surface, and Hesse-tube traces",
                    "accepted pure-C integrity traces do not recover the hidden e33 obstruction",
                ],
            },
            "sector33_witness": sector33_digest(sector33) if sector33 else None,
            "tube_visibility_witness": {
                "drinfeld_half_braiding_nullity": boundary.get("half_braiding_solve", {}).get("nullity"),
                "drinfeld_sector_count": boundary.get("drinfeld_interpretation", {}).get(
                    "sector_count_at_solved_Grothendieck_level"
                ),
                "tube_pair_basis_total": tube_section.get("projection", {}).get("tube_pair_basis_total"),
                "closed_loop_quotient_dimension": tube_section.get("projection", {}).get(
                    "closed_loop_quotient_dimension"
                ),
                "projection_kernel_dimension": tube_section.get("projection", {}).get(
                    "projection_kernel_dimension"
                ),
                "projection_section_identity": tube_section.get("section", {}).get(
                    "projection_section_identity"
                ),
                "full_relation_pairing_separates_all_39_sectors": line_surface.get("pairings", {}).get(
                    "full_relation_pairing_separates_all_39_sectors"
                ),
                "secondary_surface_splits_all_39_sectors": line_surface.get(
                    "secondary_surface_insertion", {}
                ).get("splits_all_39_sectors"),
                "unique_Hesse_pencils": hesse.get("pencil_cut_checks", {}).get("unique_Hesse_pencils"),
                "unique_projective_cubic_points": hesse.get("pencil_cut_checks", {}).get(
                    "unique_projective_cubic_points"
                ),
                "Hesse_R_residuals_all_zero": hesse.get("pencil_cut_checks", {}).get(
                    "Hesse_R_residuals_all_zero"
                ),
            },
            "integrity_witness": {
                "pure_c_no_escape_status": pure_c.get("status"),
                "pure_c_antecedent_holds": pure_c.get("accepted_antecedent_holds"),
                "x_extractor_search_status": x_search.get("status"),
                "x_extractor_present": x_search.get("result", {}).get("x_extractor_present"),
                "v_wall_accounting_status": v_wall.get("status"),
                "visible_v_events_present": v_wall.get("result", {}).get("visible_v_events_present"),
            },
        },
        "checks": checks,
        "theorem": {
            "statement": (
                "The mask-256 / cycle-8 optical obstruction forces the scalar residual "
                "Res_A985^opt=-374784. In the certified A985 sector data, sector 33 is the unique "
                "q42/q12-public-zero Drinfeld/Wedderburn sector, and it is visible to the certified "
                "tube/Hesse and line-surface trace witnesses. Therefore the first obstruction has a "
                "canonical hidden-sector interface packet (gamma_8, Pi_33, -374784)."
            ),
            "proof_outline": [
                "The non-exact theorem certifies gamma_8 has positive closed optical action 374784.",
                "Closed-return balance therefore forces Res_A985^opt(gamma_8)=-374784.",
                "The full A985 lift has exactly one public-zero sector: sector 33.",
                "The Drinfeld boundary, tube projection section, line-surface trace, and Hesse-tube pencil certify that sector 33 remains a hidden but tube-visible A985 degree of freedom.",
                "The current accepted pure-C integrity traces do not extract e33, so the packet is not a public-integral cancellation.",
            ],
            "not_claimed": [
                "a full internal module projection coefficient for gamma_8 onto Pi_33",
                "a completed modular S or T matrix",
                "a proof that every future residual must be carried only by sector 33",
                "an arbitrary polynomial-time no-extractor lower bound",
            ],
        },
        "next_highest_yield_item": (
            "Compute an explicit Pi_33 projection coefficient for cycle 8 by lifting the five D20 edges "
            "through the 297-dimensional closed-loop quotient and the certified tube-pair section."
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_residual_attachment_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the first non-exact optical obstruction is mask 256 / cycle 8",
            "verify the forced residual is -374784 and nonzero over Z and F_1000003",
            "verify sector 33 is the unique q42/q12 public-zero A985 sector",
            "verify sector 33 is tube-visible through certified Drinfeld, tube, line-surface, and Hesse witnesses",
            "verify accepted pure-C integrity traces do not extract the hidden e33 obstruction",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
