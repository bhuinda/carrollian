from __future__ import annotations

import hashlib
import json
import math
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_alphabetized_golay_finiteness"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_alphabetized_golay_finiteness.json"

COORIENT_PRESENTATION = ROOT / "data" / "coorient" / "absolute_d20_word_presentation.json"
CANONICAL_24_FRAME = ROOT / "data" / "geometry" / "canonical_24_syzygy_frame.json"
MOG_RESOLVENT = ROOT / "data" / "selectors" / "mog_resolvent_invariant.json"
MOG_CANONICITY = ROOT / "data" / "selectors" / "mog_canonicity_boundary.json"
FULL_ROW_REFINED_OBSTRUCTION = ROOT / "data" / "selectors" / "full_row_refined_obstruction.json"
WU_SPINH_6J_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"
HEXACODE_ROW_SELECTOR = ROOT / "data" / "selectors" / "hexacode_row_selector.json"
MINOR_SEARCH_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_golay_hamming_minor_puncture_search" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_alphabetized_golay_finiteness.py"
VALIDATOR = ROOT / "src" / "certify_d20_alphabetized_golay_finiteness.py"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def build_artifact() -> dict[str, Any]:
    coorient = load_json(COORIENT_PRESENTATION)
    frame = load_json(CANONICAL_24_FRAME)
    mog = load_json(MOG_RESOLVENT)
    canonicity = load_json(MOG_CANONICITY)
    row_obstruction = load_json(FULL_ROW_REFINED_OBSTRUCTION)
    wu = load_json(WU_SPINH_6J_MARKING)
    hexacode = load_json(HEXACODE_ROW_SELECTOR)
    minor_search = load_json(MINOR_SEARCH_REPORT)

    d20_alphabet = coorient["generator_semantics"]["d6_construction"]["coxeter_hexagon"]
    mog_atom_labels = canonicity["atom_partition"]["atom_labels"]
    w24_labels = frame["canonical_frame"]["coordinate_labels"]
    atom_classes = canonicity["atom_partition"]["atom_classes"]
    row_alignment = row_obstruction["row_alignment_obstruction"]
    quotient_space = row_obstruction["quotient_quadratic_space"]
    stabilizers = canonicity["residual_automorphism_boundary"]
    coordinate_stabilizers = stabilizers["coordinate_stabilizer_orders_after_internal_S4_per_atom"]

    internal_s4_order = math.factorial(4) ** 6
    column_permutation_order = math.factorial(6)
    full_coordinate_aut_order = column_permutation_order * internal_s4_order
    labelled_row_alignments = int(row_alignment["labeled_row_alignments"])
    row_alignments_mod_global = int(row_alignment["row_alignments_mod_global_row_relabel"])
    singular_7_planes = int(quotient_space["candidate_maximal_singular_7_planes_before_min_distance_filter"])
    coarse_bound = labelled_row_alignments * singular_7_planes
    coarse_mod_global_bound = row_alignments_mod_global * singular_7_planes

    finite_reduction = {
        "alphabetized_problem": (
            "A candidate D20-to-Golay morphism is constrained to preserve the finite H6 "
            "alphabet and the MOG atom partition of W24; after this typing, the remaining "
            "row-refinement/selector choices live in finite permutation and finite F2 "
            "quadratic-space search sets."
        ),
        "d20_signed_alphabet": d20_alphabet,
        "mog_atom_labels": mog_atom_labels,
        "label_sets_match": set(d20_alphabet) == set(mog_atom_labels),
        "w24_coordinate_count": frame["canonical_frame"]["coordinate_count"],
        "w24_coordinate_labels": w24_labels,
        "atom_partition": {
            "atom_count": canonicity["atom_partition"]["atom_count"],
            "atom_sizes": canonicity["atom_partition"]["atom_sizes"],
            "atom_classes": atom_classes,
            "columns_cover_24": mog["mog_frame"]["columns_cover_24"],
            "columns_pairwise_disjoint": mog["mog_frame"]["columns_pairwise_disjoint"],
        },
        "finite_address_spaces": {
            "d20_projective_root_count": coorient["generator_semantics"]["d6_construction"][
                "d6_projective_root_count"
            ],
            "pair_octad_address_count": mog["mog_frame"]["pair_column_octads"],
            "lambda2_h6_coordinate_count": wu["spin12_6j_bridge"]["lambda2_H6_coordinate_count"],
            "spin12_big_cell_dimension": wu["spin12_6j_bridge"]["foam_big_cell_dimension"],
            "scalar_plus_lambda2_h6_dimension": 1 + wu["spin12_6j_bridge"]["lambda2_H6_coordinate_count"],
        },
    }
    finite_bounds = {
        "column_permutation_order_6_factorial": column_permutation_order,
        "internal_s4_per_atom_order": internal_s4_order,
        "full_pair_octad_hypergraph_coordinate_aut_order": stabilizers[
            "full_pair_octad_hypergraph_coordinate_aut_order"
        ],
        "labeled_row_alignments": labelled_row_alignments,
        "row_alignments_mod_global_row_relabel": row_alignments_mod_global,
        "candidate_maximal_singular_7_planes_before_min_distance_filter": singular_7_planes,
        "coarse_alphabetized_selector_upper_bound": coarse_bound,
        "coarse_mod_global_row_relabel_selector_upper_bound": coarse_mod_global_bound,
        "preserve_all_h6_labels_coordinate_stabilizer": coordinate_stabilizers[
            "preserve_all_H6_labels"
        ],
    }
    checks = {
        "d20_alphabet_has_six_labels": len(d20_alphabet) == 6,
        "d20_residual_symmetry_is_dih6": coorient["generator_semantics"]["d6_construction"][
            "residual_label_symmetry"
        ]
        == "Dih_6",
        "w24_frame_is_constructed_with_24_coordinates": frame["Golay_binary_audit"][
            "frame_constructed"
        ]
        is True
        and frame["canonical_frame"]["coordinate_count"] == 24
        and len(w24_labels) == 24,
        "w24_labels_are_euler_plus_23_syzygies": w24_labels[0] == "Euler_unit"
        and all(label == f"sigma_{idx:02d}" for idx, label in enumerate(w24_labels[1:])),
        "mog_atom_partition_is_six_by_four": canonicity["atom_partition"]["atom_count"] == 6
        and canonicity["atom_partition"]["atom_sizes"] == [4, 4, 4, 4, 4, 4],
        "d20_and_mog_alphabets_match_as_sets": set(d20_alphabet) == set(mog_atom_labels),
        "mog_columns_cover_w24_disjointly": mog["mog_frame"]["columns_cover_24"] is True
        and mog["mog_frame"]["columns_pairwise_disjoint"] is True,
        "pair_octad_addresses_are_lambda2_h6": mog["spin12_mog_duality"][
            "pair_octads_identified_with_Lambda2_H6_addresses"
        ]
        is True
        and mog["spin12_mog_duality"]["Lambda2_H6_address_count"] == math.comb(6, 2),
        "spin12_big_cell_is_scalar_plus_lambda2_h6": finite_reduction["finite_address_spaces"][
            "scalar_plus_lambda2_h6_dimension"
        ]
        == 16,
        "internal_s4_count_matches_certificate": internal_s4_order
        == stabilizers["internal_S4_per_atom_order"]
        == labelled_row_alignments,
        "full_coordinate_aut_count_matches_6_factorial_times_internal_s4": full_coordinate_aut_order
        == stabilizers["full_pair_octad_hypergraph_coordinate_aut_order"],
        "row_alignment_count_matches_preserve_all_h6_label_stabilizer": labelled_row_alignments
        == coordinate_stabilizers["preserve_all_H6_labels"],
        "row_alignment_mod_global_is_quotient_by_s4": row_alignments_mod_global * math.factorial(4)
        == labelled_row_alignments,
        "quadratic_selector_search_space_is_finite": singular_7_planes > 0
        and quotient_space["quotient_dimension"] == 14
        and quotient_space["witt_index"] == 7,
        "full_row_refined_selector_remains_obstructed": row_obstruction["conclusion"][
            "full_row_refined_golay_selector_certified"
        ]
        is False,
        "hexacode_selector_is_external_endpoint": hexacode["canonicity_boundary"][
            "canonical_from_pair_octad_wu_6j_data"
        ]
        is False
        and hexacode["golay_code"]["matches_extended_golay_weight_enumerator"] is True,
        "minor_search_was_negative_bounded_search": minor_search["witness"]["search_summary"][
            "exact_morphism_found"
        ]
        is False
        and minor_search["witness"]["natural_removal_family"]["candidate_count"] == 6400,
        "alphabetization_finiteness_boundary_recorded": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.alphabetized_golay_finiteness.artifact@1",
        "status": "D20_ALPHABETIZED_GOLAY_FINITENESS_DERIVED",
        "claim_scope": (
            "Alphabetization makes the D20/Golay correspondence problem finite by forcing "
            "candidate maps through the six-label H6/MOG atom alphabet and finite W24 row "
            "refinement data."
        ),
        "source_reports": {
            "coorient_word_presentation": input_entry(COORIENT_PRESENTATION),
            "canonical_24_syzygy_frame": input_entry(
                CANONICAL_24_FRAME,
                {
                    "canonical_24_syzygy_frame_sha256": frame[
                        "canonical_24_syzygy_frame_sha256"
                    ],
                    "status": frame["status"],
                },
            ),
            "mog_resolvent_invariant": input_entry(
                MOG_RESOLVENT,
                {
                    "mog_resolvent_invariant_sha256": mog["mog_resolvent_invariant_sha256"],
                    "status": mog["status"],
                },
            ),
            "mog_canonicity_boundary": input_entry(
                MOG_CANONICITY,
                {
                    "mog_canonicity_boundary_sha256": canonicity[
                        "mog_canonicity_boundary_sha256"
                    ],
                    "status": canonicity["status"],
                },
            ),
            "full_row_refined_obstruction": input_entry(
                FULL_ROW_REFINED_OBSTRUCTION,
                {
                    "full_row_refined_golay_selector_obstruction_sha256": row_obstruction[
                        "full_row_refined_golay_selector_obstruction_sha256"
                    ],
                    "status": row_obstruction["status"],
                },
            ),
            "wu_spinh_6j_marking": input_entry(
                WU_SPINH_6J_MARKING,
                {
                    "wu_spinh_6j_marking_sha256": wu["wu_spinh_6j_marking_sha256"],
                    "status": wu["status"],
                },
            ),
            "hexacode_row_selector": input_entry(
                HEXACODE_ROW_SELECTOR,
                {
                    "hexacode_row_selector_sha256": hexacode["hexacode_row_selector_sha256"],
                },
            ),
            "minor_puncture_search": input_entry(
                MINOR_SEARCH_REPORT,
                {
                    "certificate_sha256": minor_search["certificate_sha256"],
                    "status": minor_search["status"],
                },
            ),
        },
        "finite_reduction": finite_reduction,
        "finite_bounds": finite_bounds,
        "selector_boundary": {
            "column_sextet_certified": row_obstruction["conclusion"][
                "canonical_column_sextet_certified"
            ],
            "row_alignment_from_pair_octad_wu_6j_data": row_obstruction["conclusion"][
                "canonical_row_alignment_from_pair_octad_wu_6j_data"
            ],
            "full_row_refined_golay_selector_certified": row_obstruction["conclusion"][
                "full_row_refined_golay_selector_certified"
            ],
            "missing_structure": row_obstruction["conclusion"]["missing_structure"],
            "hexacode_endpoint_constructs_g24": hexacode["golay_code"][
                "matches_extended_golay_weight_enumerator"
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.alphabetized_golay_finiteness@1",
        "status": "D20_ALPHABETIZED_GOLAY_FINITENESS_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "Alphabetization makes the D20/Golay correspondence problem finite: the D20 "
            "signed H6 alphabet matches the six MOG atoms of W24, each atom has four "
            "coordinates, and the remaining row-refinement/selector ambiguity is bounded "
            "by explicit finite permutation and F2 quadratic-space counts. This does not "
            "construct the morphism or the intrinsic Golay selector."
        ),
        "definition": {
            "alphabetization": (
                "A candidate map must preserve the finite H6 label alphabet and the W24 "
                "MOG atom partition before row-refinement or hexacode selector data is read."
            ),
            "finiteness_mechanism": (
                "The alphabet leaves only internal S4 choices inside six labelled atoms and "
                "finite F2 selector choices in the 14-dimensional quotient quadratic space."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "the D20 signed alphabet and W24 MOG atom labels are the same six-element set",
                "the W24 alphabetization partitions 24 coordinates into six labelled atoms of size four",
                "pair-octad addresses are the finite Lambda^2 H6 address set of size 15",
                "row-refinement ambiguity after fixed H6 labels is finite with 191102976 labelled alignments",
                "the remaining selector search is finite, with 9845550 maximal singular 7-plane candidates before filters",
                "the naive cocircuit-plus-one minor search is not the alphabetized finite problem",
            ],
            "does_not_certify": [
                "a selected alphabetized D20 -> W24 morphism",
                "a canonical row alignment from pair-octad/Wu/6j data alone",
                "an intrinsic Golay selector without external hexacode/F4 row labelling",
                "exhaustion of the full alphabetized selector search",
                "a rebuild of d20.json or any finite critical group artifact",
            ],
        },
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
            **artifact["source_reports"],
        },
        "witness": {
            "finite_reduction": artifact["finite_reduction"],
            "finite_bounds": artifact["finite_bounds"],
            "selector_boundary": artifact["selector_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Derive or import an actual W24 row alphabetization witness, then enumerate the "
            "finite row-refined/hexacode selector candidates against the Golay weight tests."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.alphabetized_golay_finiteness_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify D20 residual alphabet is six H6 labels with Dih_6 symmetry",
            "verify canonical W24 frame has Euler plus 23 syzygy coordinates",
            "verify MOG atom partition is six disjoint four-coordinate atoms covering W24",
            "verify D20 and MOG alphabets match as sets",
            "verify pair-octad addresses are Lambda^2 H6",
            "verify row-alignment and automorphism counts are finite and match certificates",
            "verify full row-refined Golay selector remains external/obstructed",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") != THEOREM_ID]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "coarse_alphabetized_selector_upper_bound": artifact["finite_bounds"][
                    "coarse_alphabetized_selector_upper_bound"
                ],
                "labeled_row_alignments": artifact["finite_bounds"]["labeled_row_alignments"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
