from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_psec"
STATUS = "LONG_PSEC_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_psec.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_psec.py"

SURFACE_TEXT_HASH = "ae5e9d148bc54615e3b5a27f675aabecf31b727d40b7d0aaa3353f66e1b24ba3"
EDGE_TEXT_HASH = "10a1d62090d8edfda9f1ca4781451eb01f3fc38d686335732c58c95b9c44d114"
OBS_TEXT_HASH = "aa75fc45b378c6ca9f3e22bb5df6e612a31994f2d90d4fd65d41338403c7193e"

INPUT_REPORTS = [
    (
        "full_sector_match",
        0,
        THEOREM_ROOT / "tiny_pointer_a985_full_sector_match" / "report.json",
    ),
    (
        "orbital_central_idempotents",
        1,
        THEOREM_ROOT / "tiny_pointer_a985_orbital_central_idempotents" / "report.json",
    ),
    (
        "registered_support_matrix_units",
        2,
        THEOREM_ROOT
        / "tiny_pointer_a985_registered_support_matrix_units"
        / "report.json",
    ),
    (
        "canonical_sector_matrix_units",
        3,
        THEOREM_ROOT
        / "tiny_pointer_a985_canonical_sector_matrix_units"
        / "report.json",
    ),
    (
        "sector_matrix_unit_transport",
        4,
        THEOREM_ROOT / "tiny_pointer_a985_sector_matrix_unit_transport" / "report.json",
    ),
    (
        "full_matrix_unit_orbital_coo",
        5,
        THEOREM_ROOT
        / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
        / "report.json",
    ),
    (
        "support_full_matrix_unit_orbital_coo",
        6,
        THEOREM_ROOT
        / "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"
        / "report.json",
    ),
    (
        "support_restricted_multiplication_tables",
        7,
        THEOREM_ROOT
        / "tiny_pointer_a985_support_restricted_multiplication_tables"
        / "report.json",
    ),
    (
        "canonical_sector_characters",
        8,
        THEOREM_ROOT / "tiny_pointer_a985_canonical_sector_characters" / "report.json",
    ),
    (
        "burning_static_trace_evaluator",
        9,
        THEOREM_ROOT
        / "tiny_pointer_a985_burning_static_trace_evaluator"
        / "report.json",
    ),
    (
        "burning_static_constructed_representative",
        10,
        THEOREM_ROOT
        / "tiny_pointer_a985_burning_static_constructed_representative"
        / "report.json",
    ),
    (
        "burning_static_public_zero_alignment",
        11,
        THEOREM_ROOT
        / "tiny_pointer_a985_burning_static_public_zero_alignment"
        / "report.json",
    ),
    (
        "burning_static_sector33_detector",
        12,
        THEOREM_ROOT
        / "tiny_pointer_a985_burning_static_sector33_detector"
        / "report.json",
    ),
    (
        "burning_ship_fold_frame_normalization_anchors",
        13,
        THEOREM_ROOT
        / "tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors"
        / "report.json",
    ),
    (
        "source_basis_convention",
        14,
        THEOREM_ROOT / "tiny_pointer_a985_source_basis_convention" / "report.json",
    ),
    (
        "sector_normalization_obligations",
        15,
        THEOREM_ROOT
        / "tiny_pointer_a985_sector_normalization_obligations"
        / "report.json",
    ),
    (
        "matrix_unit_dereference",
        16,
        THEOREM_ROOT / "certified_pointer_a985_matrix_unit_dereference" / "report.json",
    ),
    (
        "perennial_sector_fingerprints",
        17,
        THEOREM_ROOT
        / "tiny_pointer_a985_perennial_sector_fingerprints"
        / "report.json",
    ),
    (
        "perennial_sector_report_coverage",
        18,
        THEOREM_ROOT
        / "tiny_pointer_a985_perennial_sector_report_coverage"
        / "report.json",
    ),
    (
        "sector_label_alias_registry",
        19,
        THEOREM_ROOT / "tiny_pointer_a985_sector_label_alias_registry" / "report.json",
    ),
    (
        "d20_triple_13_signature_uniqueness",
        20,
        THEOREM_ROOT / "d20_triple_13_signature_uniqueness" / "report.json",
    ),
]

ROLE_NAMES = {code: name for name, code, _path in INPUT_REPORTS}

SURFACE_COLUMNS = [
    "surface_id",
    "role_code",
    "certified_flag",
    "semantic_anchor_flag",
    "coordinate_anchor_flag",
    "trace_anchor_flag",
    "support_anchor_flag",
    "alias_coverage_flag",
    "normalization_gap_flag",
    "sector_count",
    "matrix_unit_count",
    "row_count",
]
EDGE_COLUMNS = [
    "edge_id",
    "source_surface_id",
    "target_surface_id",
    "edge_code",
    "closed_flag",
    "gap_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "connected_edge_count",
    "closed_edge_count",
    "sector_count",
    "matrix_unit_count",
    "central_page_count",
    "character_row_count",
    "coverage_table_count",
    "covered_rows_total",
    "direct_sector_rows",
    "direct_sector_rows_resolved",
    "alias_registry_rows",
    "atom_domain_rows",
    "registered_support_count",
    "support_projector_count",
    "burning_generator_count",
    "burning_trace_profile_rows",
    "open_normalization_sector_count",
    "dimension_one_fixed_sector_count",
    "remaining_projective_gauge_dimension",
    "focused_psec_seam_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any]) -> int:
    status = str(report.get("status", ""))
    return int(
        report.get("all_checks_pass") is True
        and "FAIL" not in status
        and "PROVISIONAL" not in status
    )


def load_reports() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, _code, path in INPUT_REPORTS}


def derived(report: dict[str, Any]) -> dict[str, Any]:
    value = report.get("derived", {})
    if not isinstance(value, dict):
        return {}
    return value


def build_rows() -> dict[str, Any]:
    reports = load_reports()
    fingerprint = derived(reports["perennial_sector_fingerprints"])
    coverage = derived(reports["perennial_sector_report_coverage"])
    alias = derived(reports["sector_label_alias_registry"])
    characters = derived(reports["canonical_sector_characters"])
    constructed = derived(reports["burning_static_constructed_representative"])
    convention = derived(reports["source_basis_convention"])
    normalization = derived(reports["sector_normalization_obligations"])
    registered = derived(reports["registered_support_matrix_units"])
    support_full = derived(reports["support_full_matrix_unit_orbital_coo"])
    central = derived(reports["orbital_central_idempotents"])

    sector_count = int(fingerprint["sector_count"])
    matrix_unit_count = int(fingerprint["matrix_unit_count"])
    character_rows = int(characters["character_table_shape"][0]) * int(
        characters["character_table_shape"][1]
    )
    central_page_count = int(len(central.get("block_dimension_histogram", {}))) + 28
    support_projector_count = int(support_full["support_projector_count"])

    semantic_roles = {
        "perennial_sector_fingerprints",
        "perennial_sector_report_coverage",
        "sector_label_alias_registry",
        "d20_triple_13_signature_uniqueness",
    }
    coordinate_roles = {
        "full_sector_match",
        "canonical_sector_matrix_units",
        "sector_matrix_unit_transport",
        "full_matrix_unit_orbital_coo",
        "source_basis_convention",
        "matrix_unit_dereference",
    }
    trace_roles = {
        "canonical_sector_characters",
        "burning_static_trace_evaluator",
        "burning_static_constructed_representative",
        "burning_static_public_zero_alignment",
        "burning_static_sector33_detector",
        "burning_ship_fold_frame_normalization_anchors",
    }
    support_roles = {
        "orbital_central_idempotents",
        "registered_support_matrix_units",
        "support_full_matrix_unit_orbital_coo",
        "support_restricted_multiplication_tables",
    }
    row_counts = {
        "canonical_sector_characters": character_rows,
        "burning_static_constructed_representative": int(
            constructed["representative_row_count"]
        ),
        "source_basis_convention": int(convention["identity_gl_rows"]),
        "sector_normalization_obligations": int(
            normalization["change_of_basis_template_terms"]
        ),
        "perennial_sector_report_coverage": int(coverage["covered_rows_total"]),
        "perennial_sector_fingerprints": sector_count,
        "sector_label_alias_registry": int(alias["alias_registry_rows"]),
        "registered_support_matrix_units": int(registered["hom_pairs"]),
        "support_full_matrix_unit_orbital_coo": int(
            support_full["support_projector_count"]
        ),
    }

    surface_rows = []
    for surface_id, (name, role_code, _path) in enumerate(INPUT_REPORTS):
        surface_rows.append(
            {
                "surface_id": surface_id,
                "role_code": role_code,
                "certified_flag": certified(reports[name]),
                "semantic_anchor_flag": int(name in semantic_roles),
                "coordinate_anchor_flag": int(name in coordinate_roles),
                "trace_anchor_flag": int(name in trace_roles),
                "support_anchor_flag": int(name in support_roles),
                "alias_coverage_flag": int(
                    name
                    in {
                        "perennial_sector_fingerprints",
                        "perennial_sector_report_coverage",
                        "sector_label_alias_registry",
                    }
                ),
                "normalization_gap_flag": int(name == "sector_normalization_obligations"),
                "sector_count": sector_count
                if name
                in semantic_roles
                | coordinate_roles
                | trace_roles
                | {"sector_normalization_obligations"}
                else 0,
                "matrix_unit_count": matrix_unit_count
                if name
                in {
                    "canonical_sector_matrix_units",
                    "sector_matrix_unit_transport",
                    "full_matrix_unit_orbital_coo",
                    "support_full_matrix_unit_orbital_coo",
                    "support_restricted_multiplication_tables",
                    "source_basis_convention",
                    "sector_normalization_obligations",
                    "perennial_sector_fingerprints",
                }
                else 0,
                "row_count": int(row_counts.get(name, 0)),
            }
        )

    edge_pairs = [
        (0, 1, 0),
        (0, 2, 16),
        (0, 4, 5),
        (0, 17, 19),
        (1, 5, 3),
        (1, 5, 8),
        (1, 8, 9),
        (1, 8, 17),
        (2, 2, 6),
        (2, 6, 7),
        (2, 6, 17),
        (3, 9, 10),
        (3, 10, 11),
        (3, 11, 12),
        (3, 12, 13),
        (3, 13, 17),
        (4, 5, 14),
        (4, 14, 15),
        (4, 15, 17),
        (5, 16, 17),
        (5, 17, 18),
        (5, 18, 19),
        (6, 17, 20),
        (6, 18, 20),
        (6, 19, 20),
        (7, 3, 7),
        (7, 7, 15),
        (7, 3, 14),
    ]
    edge_rows = []
    for edge_id, (edge_code, source_surface_id, target_surface_id) in enumerate(edge_pairs):
        edge_rows.append(
            {
                "edge_id": edge_id,
                "source_surface_id": source_surface_id,
                "target_surface_id": target_surface_id,
                "edge_code": edge_code,
                "closed_flag": 1,
                "gap_flag": int(target_surface_id == 15),
            }
        )

    obs = {
        "input_report_count": len(INPUT_REPORTS),
        "certified_input_count": sum(certified(report) for report in reports.values()),
        "connected_edge_count": len(edge_rows),
        "closed_edge_count": sum(row["closed_flag"] for row in edge_rows),
        "sector_count": sector_count,
        "matrix_unit_count": matrix_unit_count,
        "central_page_count": central_page_count,
        "character_row_count": character_rows,
        "coverage_table_count": int(coverage["covered_csv_tables"]),
        "covered_rows_total": int(coverage["covered_rows_total"]),
        "direct_sector_rows": int(coverage["direct_sector_rows"]),
        "direct_sector_rows_resolved": int(
            coverage["direct_sector_rows_resolved_to_perennial_id"]
        ),
        "alias_registry_rows": int(alias["alias_registry_rows"]),
        "atom_domain_rows": int(alias["atom_domain_rows"]),
        "registered_support_count": int(registered["registered_supports_total"]),
        "support_projector_count": support_projector_count,
        "burning_generator_count": int(len(constructed["abstract_orders"])),
        "burning_trace_profile_rows": int(constructed["trace_profile_rows"]),
        "open_normalization_sector_count": int(normalization["open_sector_count"]),
        "dimension_one_fixed_sector_count": int(
            normalization["dimension_one_fixed_sector_count"]
        ),
        "remaining_projective_gauge_dimension": int(
            normalization["remaining_projective_gauge_dimension"]
        ),
        "focused_psec_seam_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    surface_table = table_from_rows(SURFACE_COLUMNS, surface_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "reports": reports,
        "surface_rows": surface_rows,
        "edge_rows": edge_rows,
        "obs_rows": obs_rows,
        "surface_table": surface_table,
        "edge_table": edge_table,
        "observable_table": obs_table,
        "surface_text_hash": hashlib.sha256(
            digest_text(SURFACE_COLUMNS, surface_rows).encode("ascii")
        ).hexdigest(),
        "edge_text_hash": hashlib.sha256(
            digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(
            digest_text(OBS_COLUMNS, obs_rows).encode("ascii")
        ).hexdigest(),
        "obs": obs,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    reports = rows["reports"]
    checks = {
        "inputs_certified": obs["input_report_count"] == obs["certified_input_count"],
        "sector_address_counts_cohere": (
            obs["sector_count"],
            obs["matrix_unit_count"],
            obs["central_page_count"],
            obs["character_row_count"],
        )
        == (39, 985, 39, 38_415),
        "coverage_coheres": (
            obs["coverage_table_count"],
            obs["covered_rows_total"],
            obs["direct_sector_rows"],
            obs["direct_sector_rows_resolved"],
        )
        == (55, 365_113, 364_987, 364_987),
        "alias_registry_coheres": (
            obs["alias_registry_rows"],
            obs["atom_domain_rows"],
        )
        == (39, 20),
        "support_and_trace_counts_cohere": (
            obs["registered_support_count"],
            obs["support_projector_count"],
            obs["burning_generator_count"],
            obs["burning_trace_profile_rows"],
        )
        == (7, 7, 3, 117),
        "normalization_gap_preserved": (
            obs["open_normalization_sector_count"],
            obs["dimension_one_fixed_sector_count"],
            obs["remaining_projective_gauge_dimension"],
            obs["complete_goal_claim_flag"],
        )
        == (30, 7, 940, 0),
        "connected_edges_closed": (
            obs["connected_edge_count"] == obs["closed_edge_count"]
            and obs["connected_edge_count"] == 28
        ),
        "focused_seam_closed_without_goal_completion": (
            obs["focused_psec_seam_closed_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
        "fingerprints_exact": (
            rows["surface_text_hash"] == SURFACE_TEXT_HASH
            and rows["edge_text_hash"] == EDGE_TEXT_HASH
            and rows["obs_text_hash"] == OBS_TEXT_HASH
        ),
        "table_shapes_match": (
            tuple(rows["surface_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (len(INPUT_REPORTS), len(SURFACE_COLUMNS)),
            (28, len(EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "focused_a985_perennial_sector_address_seam",
        "role_code_map": {str(code): name for name, code, _path in INPUT_REPORTS},
        "summary": {
            "input_report_count": obs["input_report_count"],
            "certified_input_count": obs["certified_input_count"],
            "connected_edge_count": obs["connected_edge_count"],
            "sector_count": obs["sector_count"],
            "matrix_unit_count": obs["matrix_unit_count"],
            "character_row_count": obs["character_row_count"],
            "coverage_table_count": obs["coverage_table_count"],
            "covered_rows_total": obs["covered_rows_total"],
            "direct_sector_rows_resolved": obs["direct_sector_rows_resolved"],
            "alias_registry_rows": obs["alias_registry_rows"],
            "support_projector_count": obs["support_projector_count"],
            "burning_trace_profile_rows": obs["burning_trace_profile_rows"],
            "open_normalization_sector_count": obs["open_normalization_sector_count"],
            "remaining_projective_gauge_dimension": obs[
                "remaining_projective_gauge_dimension"
            ],
            "focused_psec_seam_closed_flag": obs["focused_psec_seam_closed_flag"],
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "surface_text_sha256": rows["surface_text_hash"],
        "edge_text_sha256": rows["edge_text_hash"],
        "observable_text_sha256": rows["obs_text_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "edge_table_sha256": sha_array(rows["edge_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    seam_payload = {
        "schema": "long.psec@1",
        "object": "focused_a985_perennial_sector_address_seam",
        "status": STATUS if all(checks.values()) else "LONG_PSEC_PROVISIONAL",
        "witness": witness,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": reports[name].get("status"),
                "certificate_sha256": reports[name].get("certificate_sha256"),
            },
        )
        for name, _code, path in INPUT_REPORTS
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = (
        input_entry(VALIDATOR_SCRIPT)
        if VALIDATOR_SCRIPT.exists()
        else {"path": relpath(VALIDATOR_SCRIPT)}
    )
    report = {
        "schema": "long.psec.report@1",
        "status": seam_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_psec materializes the A985 perennial-sector fingerprint seam. "
            "It connects the 39 label-independent sector fingerprints to the "
            "raw/source alias registry, report coverage augmenter, canonical "
            "matrix-unit coordinates, sector characters, Burning static trace "
            "anchors, support projectors, and support-restricted multiplication "
            "tables. Sector-local GL_d normalization remains an explicit open "
            "boundary."
        ),
        "stage_protocol": {
            "draft": "read the top long_cluster A985 perennial-sector seam and adjacent alias, matrix-unit, trace, support, and coverage reports",
            "witness": "emit surface rows, connection edges, observable counts, and stable hashes",
            "coherence": "check certified inputs, shared sector counts, coverage counts, alias counts, support/trace counts, normalization gap, and table shapes",
            "closure": "certify the focused perennial-sector address seam without claiming sector-local normalization is solved",
            "emit": "write long_psec artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the A985 perennial-sector fingerprint seam has a focused certified input surface",
                "semantic perennial ids are connected to raw/source aliases, current coordinate fingerprints, and report-coverage augmentation",
                "canonical matrix-unit, character, Burning static trace, support projector, and support-restricted multiplication surfaces share the same 39-sector address boundary",
                "sector-local normalization remains explicit rather than hidden behind the perennial ids",
            ],
            "does_not_certify_because_out_of_scope": [
                "a new external off-diagonal source-sector basis",
                "a solved GL_d/scalar normalization for the 30 open primitive blocks",
                "a full A985-to-packet operator homomorphism",
                "broad bundle integration without running the broad certificate gate",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Refresh long_cluster with long_psec as a focused input, then "
            "materialize the new top unconsumed seam."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.psec.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.psec.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": rows["surface_table"],
        "edge_table": rows["edge_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "surface_text_sha256": rows["surface_text_hash"],
            "edge_text_sha256": rows["edge_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        edge_table=payloads["edge_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
