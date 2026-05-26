from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.derive_canonical_flux_balance_gauge_theorem import (
    canonical_oriented_edges,
    load_edges,
    vertex_charges,
    vertex_labels,
)
from src.paths import D20_INVARIANTS, DATA, ROOT


THEOREM_ID = "canonical_loop_pi33_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_FLUX_BALANCE_GAUGE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_flux_balance_gauge" / "report.json"
)
BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
SECTOR33_BOUNDARY_ANNIHILATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
)
SECTOR33_HEIGHT_COHERENT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
TUBE_PROJECTION_SECTION = DATA / "tube" / "projection_section.json"
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"
WEDDERBURN_TRACE = DATA / "drinfeld" / "wedderburn_trace.json"

FIELD_PRIME = 1000003
GAMMA8_CYCLE_ID = 8
GAMMA8_EDGES = [11, 1, 2, 22, 21]
CANONICAL_ROOT_VERTEX = 0
CANONICAL_ROOT_EDGE = 2


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
        index = load_json(index_path)
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def has_any_key(obj: dict[str, Any], keys: set[str]) -> bool:
    return any(key in obj for key in keys)


def cycle_step_orientation_records(
    cycle_steps: list[dict[str, Any]],
    canonical_edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    canonical_by_edge = {int(edge["edge_id"]): edge for edge in canonical_edges}
    records = []
    for step_index, step in enumerate(cycle_steps):
        edge_id = int(step["edge_id"])
        canonical_edge = canonical_by_edge[edge_id]
        source = int(step["source_vertex"])
        target = int(step["target_vertex"])
        canonical_source = int(canonical_edge["source"])
        canonical_target = int(canonical_edge["target"])
        if [source, target] == [canonical_source, canonical_target]:
            sign = 1
        elif [source, target] == [canonical_target, canonical_source]:
            sign = -1
        else:
            raise ValueError(f"cycle step {step_index} is not on canonical edge {edge_id}")
        records.append(
            {
                "step_index": step_index,
                "edge_id": edge_id,
                "cycle_source": source,
                "cycle_target": target,
                "canonical_source": canonical_source,
                "canonical_target": canonical_target,
                "canonical_orientation_sign": sign,
                "is_canonical_root_edge": edge_id == CANONICAL_ROOT_EDGE,
                "step_vector_sha256": step["step_vector_sha256"],
                "loop_base_object": step["loop_base_object"],
                "removed": step["removed"],
                "added": step["added"],
            }
        )
    return records


def build_theorem() -> dict[str, Any]:
    canonical_gauge = load_json(CANONICAL_FLUX_BALANCE_GAUGE_REPORT)
    boundary_to_loop = load_json(BOUNDARY_TO_LOOP_REPORT)
    annihilation = load_json(SECTOR33_BOUNDARY_ANNIHILATION_REPORT)
    height_transport = load_json(SECTOR33_HEIGHT_COHERENT_TRANSPORT_REPORT)
    tube_section = load_json(TUBE_PROJECTION_SECTION)
    full_lift = load_json(FULL_A985_LIFT)
    wedderburn = load_json(WEDDERBURN_TRACE)

    edges = load_edges()
    labels = vertex_labels(edges)
    charges = vertex_charges(labels)
    canonical_edges = canonical_oriented_edges(edges, charges)

    canonical_marking = canonical_gauge["derived"]["canonical_marking"]
    cycle8_lift = boundary_to_loop["derived"]["cycle8_lift"]
    cycle8 = cycle8_lift["cycle"]
    lift_vector = cycle8_lift["vector"]
    orientation_records = cycle_step_orientation_records(cycle8_lift["steps"], canonical_edges)
    root_edge_records = [record for record in orientation_records if record["is_canonical_root_edge"]]

    annihilation_cycle8 = annihilation["derived"]["cycle8"]["variants"]
    height_pi33 = height_transport["derived"]["pi33_tube_character"]
    height_edge_residual = height_transport["derived"]["edge_derived_residual"]
    public_shadows = height_transport["derived"]["public_shadows"]

    character = full_lift.get("irreducible_character_table", {})
    idempotent_validation = full_lift.get("full_A985_idempotent_validation", {})
    wedderburn_source = wedderburn.get("idempotent_source", {})
    section = tube_section.get("section", {})
    character_values_materialized = has_any_key(
        character,
        {"values", "matrix", "rows", "table", "character_table", "central_character_matrix"},
    )
    idempotent_matrix_materialized = has_any_key(
        idempotent_validation,
        {"values", "matrix", "rows", "embedded_idempotent_matrix", "idempotents"},
    ) or has_any_key(
        wedderburn_source,
        {"values", "matrix", "rows", "embedded_idempotent_matrix", "idempotents"},
    )
    complete_section_materialized = has_any_key(
        section,
        {"entries", "section_entries", "matrix", "coefficients", "complete_section"},
    )

    bare_coefficients = {
        name: variant["pi33_tube_character"]["coefficient_signed"]
        for name, variant in annihilation_cycle8.items()
    }
    bare_supports = {
        name: variant["pi33_tube_character"]["left_action"]["support"]
        for name, variant in annihilation_cycle8.items()
    }
    corrected_coefficient = height_pi33["corrected_transport"]["coefficient_signed"]
    height_coefficient = height_pi33["height_transport"]["coefficient_signed"]
    lambda_boundary_coefficient = height_pi33["lambda_boundary_gamma8"]["coefficient_signed"]
    residual_integral = height_edge_residual["residual_integral"]

    checks = {
        "canonical_flux_balance_gauge_is_certified": canonical_gauge.get("status")
        == "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED"
        and canonical_gauge.get("all_checks_pass") is True,
        "boundary_to_loop_is_certified": boundary_to_loop.get("status")
        == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary_to_loop.get("all_checks_pass") is True,
        "sector33_boundary_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "sector33_height_transport_is_certified": height_transport.get("status")
        == "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and height_transport.get("all_checks_pass") is True,
        "canonical_root_and_root_edge_match_cycle8": canonical_marking["canonical_root_vertex"]
        == CANONICAL_ROOT_VERTEX
        and canonical_marking["canonical_root_edge"]["edge_id"] == CANONICAL_ROOT_EDGE
        and CANONICAL_ROOT_VERTEX in cycle8["vertices"]
        and CANONICAL_ROOT_EDGE in cycle8["edge_ids"],
        "cycle8_root_edge_is_traversed_in_canonical_direction": len(root_edge_records) == 1
        and root_edge_records[0]["canonical_orientation_sign"] == 1
        and root_edge_records[0]["cycle_source"] == CANONICAL_ROOT_VERTEX,
        "cycle8_boundary_lift_matches_canonical_obstruction_target": cycle8["cycle_id"]
        == GAMMA8_CYCLE_ID
        and cycle8["edge_ids"] == GAMMA8_EDGES
        and lift_vector["support"] == 193
        and lift_vector["coefficient_sum"] == 53952
        and cycle8_lift["object_summary"].get("B+", {}).get("support", 0) > 0,
        "bare_pi33_coefficients_are_zero_for_all_recorded_variants": bare_coefficients
        == {"optical_weighted": 0, "signed_orientation": 0, "unweighted": 0}
        and bare_supports == {"optical_weighted": 0, "signed_orientation": 0, "unweighted": 0},
        "height_corrected_pi33_obstruction_is_nonzero_and_canonical": lambda_boundary_coefficient == 0
        and height_coefficient == residual_integral == corrected_coefficient == -374784
        and height_transport["derived"]["active_circuit"]["height_dot_active_row"] == 374784,
        "height_corrected_obstruction_has_zero_public_shadow": public_shadows[
            "height_transport_q12"
        ]["nonzero_count"]
        == 0
        and public_shadows["height_transport_q42"]["nonzero_count"] == 0,
        "tube_section_is_hash_only_right_inverse": tube_section.get("projection", {}).get(
            "closed_loop_quotient_dimension"
        )
        == 297
        and tube_section.get("projection", {}).get("tube_pair_basis_total") == 44521
        and section.get("projection_section_identity") is True
        and section.get("section_hash_root") is not None
        and not complete_section_materialized,
        "full_drinfeld_idempotent_matrix_remains_hash_only": not idempotent_matrix_materialized
        and (
            idempotent_validation.get("embedded_idempotent_matrix_sha256") is not None
            or wedderburn_source.get("embedded_idempotent_matrix_sha256") is not None
        ),
        "full_character_table_remains_hash_only": not character_values_materialized
        and character.get("character_table_sha256") is not None
        and character.get("shape") == [39, 985],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CANONICAL_LOOP_PI33_OBSTRUCTION_CERTIFIED"
        if all_checks_pass
        else "D20_CANONICAL_LOOP_PI33_OBSTRUCTION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.canonical_loop_pi33_obstruction",
        "status": status,
        "object": "d20",
        "claim": (
            "The canonical finite flux-balance gauge pushes through the certified boundary-to-Loop_297 lift "
            "for gamma_8. The cycle contains the canonical root and traverses the canonical root edge in the "
            "canonical direction. The bare lambda_boundary Loop_297 lift remains Pi_33-annihilated, while the "
            "height-coherent correction gives the canonical sector-33 obstruction -374784 with zero public "
            "A42/A12 shadow. This certification uses the tube-visible Pi_33 functional and hash-only Drinfeld "
            "metadata; it does not materialize the full 39 x 985 idempotent matrix."
        ),
        "definition": {
            "canonical_pushforward": (
                "Apply the canonical root/edge orientation from canonical_flux_balance_gauge to the certified "
                "gamma_8 boundary cycle, then read its existing lambda_boundary image in Loop_297."
            ),
            "bare_loop_obstruction": (
                "The tube-visible Pi_33 character of lambda_boundary(gamma_8); this is zero for the certified "
                "unweighted, signed-orientation, and optical-weighted variants."
            ),
            "height_corrected_obstruction": (
                "Lambda_hc(gamma_8)=lambda_boundary(gamma_8)-(A_h(gamma_8)/dim(Pi_33))e_33, whose Pi_33 "
                "coefficient is the edge-derived residual -374784."
            ),
        },
        "inputs": {
            "canonical_flux_balance_gauge_report": {
                "path": rel(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
                "sha256": sha_file(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
            },
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT),
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(SECTOR33_BOUNDARY_ANNIHILATION_REPORT),
                "sha256": sha_file(SECTOR33_BOUNDARY_ANNIHILATION_REPORT),
            },
            "sector33_height_coherent_transport_report": {
                "path": rel(SECTOR33_HEIGHT_COHERENT_TRANSPORT_REPORT),
                "sha256": sha_file(SECTOR33_HEIGHT_COHERENT_TRANSPORT_REPORT),
            },
            "tube_projection_section": {
                "path": rel(TUBE_PROJECTION_SECTION),
                "sha256": sha_file(TUBE_PROJECTION_SECTION),
            },
            "full_a985_lift": {"path": rel(FULL_A985_LIFT), "sha256": sha_file(FULL_A985_LIFT)},
            "wedderburn_trace": {
                "path": rel(WEDDERBURN_TRACE),
                "sha256": sha_file(WEDDERBURN_TRACE),
            },
        },
        "derived": {
            "canonical_boundary_cycle": {
                "canonical_root_vertex": canonical_marking["canonical_root_vertex"],
                "canonical_root_edge": canonical_marking["canonical_root_edge"],
                "cycle8_vertices": cycle8["vertices"],
                "cycle8_edge_ids": cycle8["edge_ids"],
                "cycle8_visits_canonical_root": CANONICAL_ROOT_VERTEX in cycle8["vertices"],
                "cycle8_contains_canonical_root_edge": CANONICAL_ROOT_EDGE in cycle8["edge_ids"],
                "cycle_step_orientation_records": orientation_records,
            },
            "loop297_lift": {
                "vector": {
                    key: value for key, value in lift_vector.items() if key != "entries"
                },
                "object_summary": cycle8_lift["object_summary"],
                "steps": cycle8_lift["steps"],
                "vector_entries_sha256": sha_json(lift_vector.get("entries", [])),
            },
            "pi33_obstruction": {
                "bare_lambda_coefficients_by_variant": bare_coefficients,
                "bare_lambda_left_action_supports_by_variant": bare_supports,
                "lambda_boundary_gamma8_coefficient": lambda_boundary_coefficient,
                "height_corrected_coefficient": corrected_coefficient,
                "height_action": height_transport["derived"]["active_circuit"]["height_dot_active_row"],
                "residual_integral": residual_integral,
                "public_shadow_nonzero_counts": {
                    "q12": public_shadows["height_transport_q12"]["nonzero_count"],
                    "q42": public_shadows["height_transport_q42"]["nonzero_count"],
                },
            },
            "hash_only_metadata": {
                "tube_section": {
                    "projection_section_identity": section.get("projection_section_identity"),
                    "section_hash_root": section.get("section_hash_root"),
                    "complete_section_materialized": complete_section_materialized,
                },
                "full_drinfeld_projection": {
                    "character_table_materialized": character_values_materialized,
                    "character_table_sha256": character.get("character_table_sha256"),
                    "idempotent_matrix_materialized": idempotent_matrix_materialized,
                    "embedded_idempotent_matrix_sha256": idempotent_validation.get(
                        "embedded_idempotent_matrix_sha256"
                    )
                    or wedderburn_source.get("embedded_idempotent_matrix_sha256"),
                    "embedded_idempotent_matrix_shape": idempotent_validation.get(
                        "embedded_idempotent_matrix_shape"
                    )
                    or wedderburn_source.get("embedded_idempotent_matrix_shape"),
                },
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the canonical finite gauge fixes the boundary representative used by the gamma_8 lift",
                "the certified Loop_297 lift remains nonzero and tube-visible Pi_33-annihilated before height correction",
                "the height-coherent correction recovers the canonical nonzero Pi_33 residual -374784",
                "the proof avoids materializing the full Drinfeld idempotent matrix and character table",
            ],
            "what_this_does_not_prove": (
                "This does not compute the full A985 Drinfeld projection coordinates. It certifies the "
                "canonical tube-visible obstruction path using existing hash-only full-Drinfeld metadata."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Turn the canonical Loop_297 obstruction into an explicit finite Ward identity: exact public "
            "flux gauge term zero, bare Pi_33 term zero, height-corrected R33 term -374784."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.canonical_loop_pi33_obstruction_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify canonical flux gauge, boundary-to-loop lift, Pi_33 annihilation, and height transport inputs",
            "verify gamma_8 contains the canonical root and canonical root edge",
            "verify the canonical root edge is traversed in canonical orientation",
            "verify the bare Loop_297 lift is Pi_33-annihilated for all recorded variants",
            "verify the height-corrected Pi_33 coefficient is -374784 with zero public shadow",
            "verify full Drinfeld idempotent and character data remain hash-only",
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
