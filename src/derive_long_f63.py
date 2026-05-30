from __future__ import annotations

import csv
import hashlib
import json
from itertools import combinations
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_f63"
STATUS = "LONG_F63_FIXED_EXTERIOR_BOUNDARY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

RAW543_ACTION = THEOREM_ROOT / "raw543_repo_c2_kernel_action" / "report.json"
RAW543_AGDA = THEOREM_ROOT / "raw543_repo_c2_kernel_agda_bridge_data" / "report.json"
FIXED63 = (
    THEOREM_ROOT
    / "raw543_repo_c2_kernel_agda_bridge_data"
    / "actual_raw543_agda_fixed63.csv"
)
ATLAS_REPORT = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "report.json"
ATLAS_CSV = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "d20_boundary_invariant_atlas.csv"
LONG_L63 = PROOF_ROOT / "long_l63" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_f63.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_f63.py"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]

BASIS_COLUMNS = [
    "basis_id",
    "pivot_bit",
    "f2_11_mask",
    "coordinate_mask",
    "source_rank",
]
FIXED_COLUMNS = [
    "row_id",
    "lazy63_index",
    "orbit_id",
    "f2_11_mask",
    "coordinate_mask",
    "coordinate_weight",
    "grade_code",
    "d20_atom_flag",
    "atom_id",
    "complement_atom_id",
]
ATOM_COLUMNS = [
    "atom_id",
    "coordinate_mask",
    "f2_11_mask",
    "lazy63_index",
    "orbit_id",
    "complement_atom_id",
    "atlas_complement_atom_id",
    "complement_match_flag",
]
GRADE_COLUMNS = [
    "coordinate_weight",
    "fixed63_row_count",
    "binomial_count",
    "d20_atom_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "fixed63_row_count",
    "fixed63_plus_zero_count",
    "fixed63_rank",
    "coordinate_dimension",
    "coordinate_nonzero_count",
    "coordinate_coverage_flag",
    "xor_closure_flag",
    "grade1_count",
    "grade2_count",
    "grade3_count",
    "grade4_count",
    "grade5_count",
    "grade6_count",
    "d20_atom_count",
    "atlas_atom_count",
    "atom_atlas_complement_match_count",
    "atom_atlas_complement_all_match_flag",
    "gamma8_mask",
    "gamma8_in_fixed63_flag",
    "gamma8_hidden_odd_flag",
    "long_l63_row_bridge_present_flag",
    "rim_phase_selected_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def reduce_by_basis(value: int, basis: dict[int, int]) -> int:
    out = value
    for pivot, row in sorted(basis.items(), reverse=True):
        if (out >> pivot) & 1:
            out ^= row
    return out


def canonical_basis(values: list[int]) -> dict[int, int]:
    basis: dict[int, int] = {}
    for value in sorted(values):
        reduced = reduce_by_basis(value, basis)
        if reduced == 0:
            continue
        pivot = reduced.bit_length() - 1
        basis[pivot] = reduced
        for other_pivot, other_row in list(basis.items()):
            if other_pivot != pivot and ((other_row >> pivot) & 1):
                basis[other_pivot] = other_row ^ reduced
    return dict(sorted(basis.items()))


def rank_masks(values: list[int]) -> int:
    return len(canonical_basis(values))


def coordinate_maps(basis_rows: list[int]) -> tuple[dict[int, int], dict[int, int]]:
    coordinate_to_mask = {0: 0}
    for bit, row in enumerate(basis_rows):
        for coordinate, mask in list(coordinate_to_mask.items()):
            coordinate_to_mask[coordinate | (1 << bit)] = mask ^ row
    mask_to_coordinate = {mask: coordinate for coordinate, mask in coordinate_to_mask.items()}
    return coordinate_to_mask, mask_to_coordinate


def coordinate_weight(mask: int) -> int:
    return int(mask).bit_count()


def h6_combinations() -> list[tuple[int, int, int]]:
    return list(combinations(range(6), 3))


def atom_id_for_coordinate(coordinate: int) -> int:
    combo = tuple(index for index in range(6) if (coordinate >> index) & 1)
    return h6_combinations().index(combo)


def build_rows() -> dict[str, Any]:
    raw543 = load_json(RAW543_ACTION)
    agda = load_json(RAW543_AGDA)
    atlas = load_json(ATLAS_REPORT)
    l63 = load_json(LONG_L63)
    fixed_rows_raw = read_csv(FIXED63)
    atlas_rows_raw = read_csv(ATLAS_CSV)

    fixed_values = sorted(int(row["representative_mask"]) for row in fixed_rows_raw)
    basis_by_pivot = canonical_basis(fixed_values)
    basis_rows_raw = [basis_by_pivot[pivot] for pivot in sorted(basis_by_pivot)]
    coordinate_to_mask, mask_to_coordinate = coordinate_maps(basis_rows_raw)
    full_fixed_set = set(fixed_values) | {0}
    fixed_row_by_mask = {
        int(row["representative_mask"]): row for row in fixed_rows_raw
    }
    atlas_by_atom = {int(row["atom_id"]): row for row in atlas_rows_raw}

    basis_rows = [
        {
            "basis_id": index,
            "pivot_bit": pivot,
            "f2_11_mask": basis_by_pivot[pivot],
            "coordinate_mask": 1 << index,
            "source_rank": index + 1,
        }
        for index, pivot in enumerate(sorted(basis_by_pivot))
    ]

    combos = h6_combinations()
    fixed_rows = []
    grade_counts = {grade: 0 for grade in range(1, 7)}
    for row_id, coordinate in enumerate(range(1, 1 << 6)):
        mask = coordinate_to_mask[coordinate]
        source = fixed_row_by_mask[mask]
        weight = coordinate_weight(coordinate)
        grade_counts[weight] += 1
        if weight == 3:
            atom_id = atom_id_for_coordinate(coordinate)
            complement_coordinate = ((1 << 6) - 1) ^ coordinate
            complement_atom_id = atom_id_for_coordinate(complement_coordinate)
        else:
            atom_id = -1
            complement_atom_id = -1
        fixed_rows.append(
            {
                "row_id": row_id,
                "lazy63_index": int(source["lazy63_index"]),
                "orbit_id": int(source["orbit_id"]),
                "f2_11_mask": mask,
                "coordinate_mask": coordinate,
                "coordinate_weight": weight,
                "grade_code": weight,
                "d20_atom_flag": int(weight == 3),
                "atom_id": atom_id,
                "complement_atom_id": complement_atom_id,
            }
        )

    atom_rows = []
    for atom_id, combo in enumerate(combos):
        coordinate = sum(1 << bit for bit in combo)
        mask = coordinate_to_mask[coordinate]
        source = fixed_row_by_mask[mask]
        complement_coordinate = ((1 << 6) - 1) ^ coordinate
        complement_atom_id = atom_id_for_coordinate(complement_coordinate)
        atlas_complement = int(atlas_by_atom[atom_id]["complement_atom_id"])
        atom_rows.append(
            {
                "atom_id": atom_id,
                "coordinate_mask": coordinate,
                "f2_11_mask": mask,
                "lazy63_index": int(source["lazy63_index"]),
                "orbit_id": int(source["orbit_id"]),
                "complement_atom_id": complement_atom_id,
                "atlas_complement_atom_id": atlas_complement,
                "complement_match_flag": int(complement_atom_id == atlas_complement),
            }
        )

    grade_rows = [
        {
            "coordinate_weight": grade,
            "fixed63_row_count": grade_counts[grade],
            "binomial_count": len(list(combinations(range(6), grade))),
            "d20_atom_flag": int(grade == 3),
        }
        for grade in range(1, 7)
    ]

    gamma8_mask = int(
        raw543["derived"]["actual_nontrivial_c2_preserver"]["gamma8_mask"]
    )
    hidden_character_mask = int(
        raw543["derived"]["actual_nontrivial_c2_preserver"]["hidden_character_mask"]
    )
    l63_summary = summary(l63)

    xor_closure = int(
        all((left ^ right) in full_fixed_set for left in full_fixed_set for right in full_fixed_set)
    )
    coordinate_coverage = int(
        len(coordinate_to_mask) == 64
        and set(coordinate_to_mask.values()) == full_fixed_set
        and all(value in mask_to_coordinate for value in fixed_values)
    )
    atom_complement_matches = sum(row["complement_match_flag"] for row in atom_rows)
    obs = {
        "input_report_count": 4,
        "input_certified_count": sum(certified(report) for report in [raw543, agda, atlas, l63]),
        "fixed63_row_count": len(fixed_values),
        "fixed63_plus_zero_count": len(full_fixed_set),
        "fixed63_rank": rank_masks(fixed_values),
        "coordinate_dimension": len(basis_rows),
        "coordinate_nonzero_count": (1 << len(basis_rows)) - 1,
        "coordinate_coverage_flag": coordinate_coverage,
        "xor_closure_flag": xor_closure,
        "grade1_count": grade_counts[1],
        "grade2_count": grade_counts[2],
        "grade3_count": grade_counts[3],
        "grade4_count": grade_counts[4],
        "grade5_count": grade_counts[5],
        "grade6_count": grade_counts[6],
        "d20_atom_count": len(atom_rows),
        "atlas_atom_count": int(atlas["witness"]["atom_count"]),
        "atom_atlas_complement_match_count": atom_complement_matches,
        "atom_atlas_complement_all_match_flag": int(atom_complement_matches == len(atom_rows)),
        "gamma8_mask": gamma8_mask,
        "gamma8_in_fixed63_flag": int(gamma8_mask in full_fixed_set),
        "gamma8_hidden_odd_flag": int((gamma8_mask & hidden_character_mask).bit_count() & 1),
        "long_l63_row_bridge_present_flag": int(l63_summary["row_bridge_present_flag"]),
        "rim_phase_selected_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    return {
        "raw543": raw543,
        "agda": agda,
        "atlas": atlas,
        "l63": l63,
        "basis_rows": basis_rows,
        "fixed_rows": fixed_rows,
        "atom_rows": atom_rows,
        "grade_rows": grade_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    basis_table = table_from_rows(BASIS_COLUMNS, rows["basis_rows"])
    fixed_table = table_from_rows(FIXED_COLUMNS, rows["fixed_rows"])
    atom_table = table_from_rows(ATOM_COLUMNS, rows["atom_rows"])
    grade_table = table_from_rows(GRADE_COLUMNS, rows["grade_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "fixed63_is_projective_f2_6": obs["fixed63_row_count"] == 63
        and obs["fixed63_plus_zero_count"] == 64
        and obs["fixed63_rank"] == 6
        and obs["coordinate_dimension"] == 6,
        "coordinate_map_covers_fixed_space": obs["coordinate_coverage_flag"] == 1
        and obs["xor_closure_flag"] == 1
        and obs["coordinate_nonzero_count"] == 63,
        "exterior_grade_counts_match_binomial_row": [
            obs["grade1_count"],
            obs["grade2_count"],
            obs["grade3_count"],
            obs["grade4_count"],
            obs["grade5_count"],
            obs["grade6_count"],
        ]
        == [6, 15, 20, 15, 6, 1],
        "grade_three_is_d20_atom_count": obs["grade3_count"] == 20
        and obs["d20_atom_count"] == 20
        and obs["atlas_atom_count"] == 20,
        "complement_matches_atlas": obs["atom_atlas_complement_match_count"] == 20
        and obs["atom_atlas_complement_all_match_flag"] == 1,
        "gamma8_remains_hidden_odd_outside_lazy63": obs["gamma8_mask"] == 256
        and obs["gamma8_in_fixed63_flag"] == 0
        and obs["gamma8_hidden_odd_flag"] == 1,
        "rim_phase_selection_still_not_claimed": obs["long_l63_row_bridge_present_flag"] == 0
        and obs["rim_phase_selected_flag"] == 0,
        "table_shapes_match": basis_table.shape == (6, len(BASIS_COLUMNS))
        and fixed_table.shape == (63, len(FIXED_COLUMNS))
        and atom_table.shape == (20, len(ATOM_COLUMNS))
        and grade_table.shape == (6, len(GRADE_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "fixed63_exterior_d20_boundary_bridge",
        "summary": {
            "fixed63_row_count": obs["fixed63_row_count"],
            "fixed63_rank": obs["fixed63_rank"],
            "coordinate_dimension": obs["coordinate_dimension"],
            "coordinate_nonzero_count": obs["coordinate_nonzero_count"],
            "grade_counts": [
                obs["grade1_count"],
                obs["grade2_count"],
                obs["grade3_count"],
                obs["grade4_count"],
                obs["grade5_count"],
                obs["grade6_count"],
            ],
            "d20_atom_count": obs["d20_atom_count"],
            "atom_atlas_complement_match_count": obs[
                "atom_atlas_complement_match_count"
            ],
            "gamma8_in_fixed63_flag": obs["gamma8_in_fixed63_flag"],
            "gamma8_hidden_odd_flag": obs["gamma8_hidden_odd_flag"],
            "long_l63_row_bridge_present_flag": obs[
                "long_l63_row_bridge_present_flag"
            ],
            "rim_phase_selected_flag": obs["rim_phase_selected_flag"],
        },
        "h6_labels": H6_LABELS,
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "basis_table_sha256": sha_array(basis_table),
        "basis_text_sha256": sha_text(csv_text(BASIS_COLUMNS, rows["basis_rows"])),
        "fixed_table_sha256": sha_array(fixed_table),
        "fixed_text_sha256": sha_text(csv_text(FIXED_COLUMNS, rows["fixed_rows"])),
        "atom_table_sha256": sha_array(atom_table),
        "atom_text_sha256": sha_text(csv_text(ATOM_COLUMNS, rows["atom_rows"])),
        "grade_table_sha256": sha_array(grade_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    f63 = {
        "schema": "long.f63@1",
        "object": "fixed63_exterior_d20_boundary_bridge",
        "status": STATUS if all(checks.values()) else "LONG_F63_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.f63.report@1",
        "status": f63["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_f63 promotes the valid part of the lazy63 coincidence: the "
            "63 lazy fixed rows are the nonzero vectors of a finite F2^6 "
            "coordinate spine, and the grade-three slice has exactly the 20 "
            "Lambda^3 H6 atoms with the certified d20 complement pairing."
        ),
        "stage_protocol": {
            "draft": "read raw543 C2 kernel action, Agda fixed63 bridge data, d20 atom atlas, and long_l63",
            "witness": "emit fixed-space basis, fixed63 coordinate rows, grade counts, and the 20 grade-three atom bridge rows",
            "coherence": "check F2^6 closure, coordinate coverage, binomial grade counts, atom complement match, gamma8 exclusion, and table hashes",
            "closure": "certify the fixed63 exterior boundary bridge while preserving the rim-selection obstruction",
            "emit": "write long_f63 artifacts and verifier hook",
        },
        "inputs": {
            "raw543_action": input_entry(
                RAW543_ACTION,
                {
                    "status": rows["raw543"].get("status"),
                    "certificate_sha256": rows["raw543"].get("certificate_sha256"),
                },
            ),
            "raw543_agda": input_entry(
                RAW543_AGDA,
                {
                    "status": rows["agda"].get("status"),
                    "certificate_sha256": rows["agda"].get("certificate_sha256"),
                },
            ),
            "fixed63": input_entry(FIXED63),
            "atlas": input_entry(
                ATLAS_REPORT,
                {
                    "status": rows["atlas"].get("status"),
                    "certificate_sha256": rows["atlas"].get("certificate_sha256"),
                },
            ),
            "atlas_csv": input_entry(ATLAS_CSV),
            "long_l63": input_entry(
                LONG_L63,
                {
                    "status": rows["l63"].get("status"),
                    "certificate_sha256": rows["l63"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "f63": relpath(OUT_DIR / "f63.json"),
            "basis_csv": relpath(OUT_DIR / "basis.csv"),
            "fixed_csv": relpath(OUT_DIR / "fixed.csv"),
            "atom_csv": relpath(OUT_DIR / "atom.csv"),
            "grade_csv": relpath(OUT_DIR / "grade.csv"),
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
                "lazy63/fixed63 plus zero is a six-dimensional F2 vector space at the current raw543 boundary",
                "a deterministic coordinate basis identifies the 63 lazy rows with nonzero F2^6 coordinates",
                "the exterior grade distribution is 6, 15, 20, 15, 6, 1",
                "the grade-three slice has 20 rows and matches the certified D20 atom complement pairing",
                "gamma8 is fixed by the C2 action but hidden-odd and outside the lazy63 fixed kernel",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the deterministic F2^6 basis is the unique physical H6 basis",
                "a semantic row map from lazy63 rows to rim defect classes",
                "selection of the golden rim phase",
                "a physical selector axiom",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Use the certified grade-three fixed63 atom bridge to test whether "
            "any C20 rim, stress graph, or transition surface can be lifted to "
            "a coordinate-basis-independent selector on the F2^6 exterior spine."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.f63.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.f63.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "f63": f63,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "fixed_csv": csv_text(FIXED_COLUMNS, rows["fixed_rows"]),
        "atom_csv": csv_text(ATOM_COLUMNS, rows["atom_rows"]),
        "grade_csv": csv_text(GRADE_COLUMNS, rows["grade_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": basis_table,
        "fixed_table": fixed_table,
        "atom_table": atom_table,
        "grade_table": grade_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "f63.json", payloads["f63"])
    (OUT_DIR / "basis.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "fixed.csv").write_text(payloads["fixed_csv"], encoding="utf-8")
    (OUT_DIR / "atom.csv").write_text(payloads["atom_csv"], encoding="utf-8")
    (OUT_DIR / "grade.csv").write_text(payloads["grade_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        fixed_table=payloads["fixed_table"],
        atom_table=payloads["atom_table"],
        grade_table=payloads["grade_table"],
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
