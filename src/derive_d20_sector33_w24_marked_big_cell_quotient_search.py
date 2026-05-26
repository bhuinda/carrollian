from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_golay_hamming_minor_puncture_search import (
        mod2_matrix,
        rref_mod2,
        rows_to_masks,
        self_orthogonal,
        weight_histogram,
    )
    from .derive_d20_oriented_matroid_contour import edge_table
    from .derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_golay_hamming_minor_puncture_search import (
        mod2_matrix,
        rref_mod2,
        rows_to_masks,
        self_orthogonal,
        weight_histogram,
    )
    from derive_d20_oriented_matroid_contour import edge_table
    from derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_marked_big_cell_quotient_search"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_sector33_w24_marked_big_cell_quotient_search.json"

D20_JSON = ROOT / "d20.json"
W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
PER_EDGE_ROWSPACE_PRUNE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_per_edge_rowspace_prune"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
WU_SPINH_6J_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_marked_big_cell_quotient_search.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_marked_big_cell_quotient_search.py"

MODE_DESCRIPTIONS = {
    "duplicate_xor_collapse": (
        "For each selector duad, xor the two public sector33 edge columns and append e33 "
        "as the scalar big-cell coordinate."
    ),
    "first_edge_selector": (
        "For each selector duad, keep the lower-numbered public sector33 edge column and "
        "append e33 as the scalar big-cell coordinate."
    ),
    "second_edge_selector": (
        "For each selector duad, keep the higher-numbered public sector33 edge column and "
        "append e33 as the scalar big-cell coordinate."
    ),
}
MODE_NAMES = tuple(MODE_DESCRIPTIONS)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def parse_pair(text: str) -> tuple[str, str]:
    pair = tuple(part.strip() for part in text.strip("{}").split(",") if part.strip())
    if len(pair) != 2:
        raise ValueError(f"not a pair: {text}")
    return pair  # type: ignore[return-value]


def pair_label(pair: tuple[str, str]) -> str:
    return "{" + ",".join(pair) + "}"


def selector_duad_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    by_string: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        pair = parse_pair(str(row["selector_duad"]))
        edge_id = int(row["edge_id"])
        by_string[str(row["selector_duad"])].append(edge_id)
        if pair not in by_pair:
            by_pair[pair] = {
                "selector_duad": pair_label(pair),
                "selector_duad_index": int(row["selector_duad_index"]),
                "pair": list(pair),
                "edge_ids": [],
            }
        by_pair[pair]["edge_ids"].append(edge_id)

    ordered = sorted(by_pair.values(), key=lambda record: record["selector_duad_index"])
    for record in ordered:
        record["edge_ids"] = sorted(record["edge_ids"])
    return {
        "selector_duad_count": len(ordered),
        "selector_duads": ordered,
        "all_selector_duads_have_two_edges": all(
            len(record["edge_ids"]) == 2 for record in ordered
        ),
        "selector_duad_index_set": [record["selector_duad_index"] for record in ordered],
        "edge_id_multiset_by_selector_duad": {
            key: sorted(value) for key, value in sorted(by_string.items())
        },
    }


def marked_big_cell_profile(
    marking: dict[str, Any],
    d20_selector_duads: list[dict[str, Any]],
) -> dict[str, Any]:
    bridge = marking["spin12_6j_bridge"]
    coordinate_map = sorted(bridge["big_cell_coordinate_map"], key=lambda row: row["coordinate"])
    scalar = [row for row in coordinate_map if row["type"] == "scalar"]
    two_forms = [row for row in coordinate_map if row["type"] == "two_form"]
    two_form_pairs = [tuple(row["pair"]) for row in two_forms]
    d20_pairs = [tuple(row["pair"]) for row in d20_selector_duads]
    return {
        "status": marking["status"],
        "golay_selector_constructed": marking["selector_status"]["golay_selector_constructed"],
        "golay_selector_status": marking["selector_status"]["golay_selector_status"],
        "h6_labels": bridge["H6_labels"],
        "ambient_even_half_spin_dimension": bridge["ambient_even_half_spin_dimension"],
        "foam_big_cell_dimension": bridge["foam_big_cell_dimension"],
        "lambda2_H6_coordinate_count": bridge["lambda2_H6_coordinate_count"],
        "coordinate_count": len(coordinate_map),
        "scalar_coordinate_count": len(scalar),
        "scalar_coordinates": [row["coordinate"] for row in scalar],
        "two_form_coordinate_count": len(two_forms),
        "two_form_coordinates": [
            {
                "coordinate": row["coordinate"],
                "foam_coordinate": row["foam_coordinate"],
                "pair": row["pair"],
            }
            for row in two_forms
        ],
        "two_form_pairs": [list(pair) for pair in two_form_pairs],
        "pair_set_matches_d20_selector_duads": {tuple(pair) for pair in two_form_pairs}
        == {tuple(pair) for pair in d20_pairs},
        "pair_order_matches_d20_selector_duad_index": two_form_pairs == d20_pairs,
        "d20_selector_duad_labels_in_marked_order": [pair_label(pair) for pair in d20_pairs],
    }


def quotient_row(
    row: list[int],
    selector_duads: list[dict[str, Any]],
    mode: str,
) -> list[int]:
    out: list[int] = []
    for record in selector_duads:
        first, second = record["edge_ids"]
        if mode == "duplicate_xor_collapse":
            out.append(row[first] ^ row[second])
        elif mode == "first_edge_selector":
            out.append(row[first])
        elif mode == "second_edge_selector":
            out.append(row[second])
        else:
            raise ValueError(f"unknown quotient mode: {mode}")
    out.append(row[30])
    return out


def summarize_quotient_mode(
    source_matrix: list[list[int]],
    selector_duads: list[dict[str, Any]],
    mode: str,
) -> dict[str, Any]:
    quotient = [quotient_row(row, selector_duads, mode) for row in source_matrix]
    reduced, pivots = rref_mod2(quotient, 16)
    row_masks = rows_to_masks(reduced)
    hist = weight_histogram(row_masks)
    nonzero_weights = [weight for weight, count in hist.items() if weight and count]
    return {
        "mode": mode,
        "description": MODE_DESCRIPTIONS[mode],
        "output_length": 16,
        "source_row_count": len(source_matrix),
        "reduced_rank": len(reduced),
        "pivot_columns": pivots,
        "basis_masks": row_masks,
        "basis_masks_sha256": sha_json(row_masks),
        "weight_histogram": {str(weight): count for weight, count in hist.items()},
        "minimum_nonzero_weight": min(nonzero_weights) if nonzero_weights else None,
        "self_orthogonal": self_orthogonal(row_masks),
        "doubly_even": all(weight % 4 == 0 for weight in hist),
        "rank12_precondition_pass": len(reduced) == 12,
        "self_orthogonal_precondition_pass": self_orthogonal(row_masks),
    }


def quotient_search(rows: list[dict[str, Any]]) -> dict[str, Any]:
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    primal_mod2 = mod2_matrix(primal_integer_matrix)
    profile = selector_duad_profile(rows)
    selector_duads = profile["selector_duads"]
    modes = [summarize_quotient_mode(primal_mod2, selector_duads, mode) for mode in MODE_NAMES]
    rank_histogram = Counter(mode["reduced_rank"] for mode in modes)
    return {
        "source_matrix": "sector33_primal_mod2",
        "source_shape": {"rows": len(primal_mod2), "cols": len(primal_mod2[0])},
        "sector33_attachment": attachment,
        "d20_selector_duad_profile": profile,
        "quotient_column_order": [
            {
                "kind": "two_form",
                "selector_duad_index": record["selector_duad_index"],
                "selector_duad": record["selector_duad"],
                "pair": record["pair"],
                "source_edge_ids": record["edge_ids"],
            }
            for record in selector_duads
        ]
        + [{"kind": "scalar", "label": "e33", "source_element_id": 30}],
        "quotient_mode_count": len(modes),
        "modes": modes,
        "mode_rank_histogram": {
            str(rank): count for rank, count in sorted(rank_histogram.items())
        },
        "rank12_mode_count": sum(1 for mode in modes if mode["reduced_rank"] == 12),
        "self_orthogonal_mode_count": sum(1 for mode in modes if mode["self_orthogonal"]),
        "all_modes_fail_rank12_precondition": all(
            not mode["rank12_precondition_pass"] for mode in modes
        ),
        "all_modes_fail_self_orthogonal_precondition": all(
            not mode["self_orthogonal_precondition_pass"] for mode in modes
        ),
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    per_edge = load_json(PER_EDGE_ROWSPACE_PRUNE)
    dual = load_json(SECTOR33_DUAL_REPORT)
    marking = load_json(WU_SPINH_6J_MARKING)

    rows = edge_table(d20)
    target_golay = w24["witness"]["golay_code"]
    search = quotient_search(rows)
    big_cell = marked_big_cell_profile(
        marking, search["d20_selector_duad_profile"]["selector_duads"]
    )
    mode_by_name = {mode["mode"]: mode for mode in search["modes"]}

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "per_edge_rowspace_prune_input_is_certified": per_edge["status"]
        == "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_CERTIFIED"
        and per_edge["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "wu_marking_is_certified_external_boundary": marking["status"]
        == "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL"
        and marking["selector_status"]["golay_selector_constructed"] is False,
        "source_matrix_shape_is_21_by_31": search["source_shape"] == {"rows": 21, "cols": 31},
        "d20_selector_duad_profile_has_15_pairs": search["d20_selector_duad_profile"][
            "selector_duad_count"
        ]
        == 15,
        "d20_selector_duads_have_two_edges_each": search["d20_selector_duad_profile"][
            "all_selector_duads_have_two_edges"
        ],
        "big_cell_has_scalar_plus_15_two_forms": big_cell["foam_big_cell_dimension"] == 16
        and big_cell["coordinate_count"] == 16
        and big_cell["scalar_coordinate_count"] == 1
        and big_cell["two_form_coordinate_count"] == 15
        and big_cell["lambda2_H6_coordinate_count"] == 15,
        "big_cell_pair_set_matches_d20_selector_duads": big_cell[
            "pair_set_matches_d20_selector_duads"
        ],
        "big_cell_pair_order_matches_d20_selector_duad_index": big_cell[
            "pair_order_matches_d20_selector_duad_index"
        ],
        "quotient_mode_count_is_3": search["quotient_mode_count"] == 3,
        "all_quotient_lengths_are_16": all(
            mode["output_length"] == 16 for mode in search["modes"]
        ),
        "duplicate_xor_collapse_rank_is_11": mode_by_name["duplicate_xor_collapse"][
            "reduced_rank"
        ]
        == 11,
        "first_edge_selector_rank_is_16": mode_by_name["first_edge_selector"][
            "reduced_rank"
        ]
        == 16,
        "second_edge_selector_rank_is_14": mode_by_name["second_edge_selector"][
            "reduced_rank"
        ]
        == 14,
        "mode_rank_histogram_is_11_14_16": search["mode_rank_histogram"]
        == {"11": 1, "14": 1, "16": 1},
        "no_mode_has_rank_12": search["rank12_mode_count"] == 0
        and search["all_modes_fail_rank12_precondition"],
        "no_mode_is_self_orthogonal": search["self_orthogonal_mode_count"] == 0
        and search["all_modes_fail_self_orthogonal_precondition"],
        "natural_marked_quotients_fail_candidate_gate": search["rank12_mode_count"] == 0
        and search["self_orthogonal_mode_count"] == 0,
        "explicit_morphism_remains_open": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search.artifact@1",
        "status": "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_DERIVED",
        "claim_scope": (
            "Test the three natural rank-changing maps from sector33 primal edge data into "
            "the Wu/Spin12 marked big cell: duplicate xor collapse, first-edge selector, "
            "and second-edge selector."
        ),
        "source_reports": {
            "d20_json": input_entry(D20_JSON, {"status": d20.get("status")}),
            "w24_row_alphabetization": input_entry(
                W24_ROW_ALPHABETIZATION,
                {
                    "certificate_sha256": w24["certificate_sha256"],
                    "status": w24["status"],
                },
            ),
            "per_edge_rowspace_prune": input_entry(
                PER_EDGE_ROWSPACE_PRUNE,
                {
                    "certificate_sha256": per_edge["certificate_sha256"],
                    "status": per_edge["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual["certificate_sha256"],
                    "status": dual["status"],
                },
            ),
            "wu_spinh_6j_marking": input_entry(
                WU_SPINH_6J_MARKING,
                {
                    "status": marking["status"],
                    "recorded_selector_status": marking["selector_status"][
                        "golay_selector_status"
                    ],
                },
            ),
        },
        "target_golay_profile": {
            "length": target_golay["length"],
            "rank": target_golay["rank"],
            "weight_histogram": target_golay["weight_histogram"],
            "generator_basis_masks_sha256": sha_json(target_golay["generator_basis_masks"]),
        },
        "marked_big_cell_profile": big_cell,
        "quotient_search": search,
        "candidate_gate": {
            "tested_modes": list(MODE_NAMES),
            "rank_precondition": "candidate must have binary rank 12 before any W24 basis comparison",
            "orthogonality_precondition": (
                "candidate should at least be self-orthogonal before Type-II/Golay comparison"
            ),
            "rank12_mode_count": search["rank12_mode_count"],
            "self_orthogonal_mode_count": search["self_orthogonal_mode_count"],
            "basis_compare_attempted": False,
            "basis_compare_blocked_reason": (
                "none of the three natural marked big-cell quotient modes has rank 12 or "
                "self-orthogonal rowspace"
            ),
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    search = artifact["quotient_search"]
    mode_ranks = {
        mode["mode"]: mode["reduced_rank"]
        for mode in search["modes"]
    }
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search@1",
        "status": "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The obvious marked Spin12 big-cell quotient routes do not produce a Golay-rank "
            "candidate. Duplicate edge collapse has rank 11, the lower-edge selector has "
            "rank 16, and the upper-edge selector has rank 14; all three are also not "
            "self-orthogonal."
        ),
        "definition": {
            "marked_big_cell": (
                "the Wu/spin^h 6j Foam16 chart with one scalar coordinate and the 15 "
                "Lambda^2 H6 two-form coordinates"
            ),
            "duplicate_xor_collapse": MODE_DESCRIPTIONS["duplicate_xor_collapse"],
            "first_edge_selector": MODE_DESCRIPTIONS["first_edge_selector"],
            "second_edge_selector": MODE_DESCRIPTIONS["second_edge_selector"],
            "candidate_gate": artifact["candidate_gate"],
        },
        "closure_boundary": {
            "certifies": [
                "the Wu/Spin12 big-cell two-form coordinate order matches the D20 selector-duad order",
                f"duplicate xor collapse has binary rank {mode_ranks['duplicate_xor_collapse']}",
                f"first-edge selector has binary rank {mode_ranks['first_edge_selector']}",
                f"second-edge selector has binary rank {mode_ranks['second_edge_selector']}",
                "none of the three natural marked big-cell quotient modes has rank 12",
                "none of the three natural marked big-cell quotient modes is self-orthogonal",
            ],
            "does_not_certify": [
                "absence of a morphism using mixed per-duad first/second/xor choices",
                "absence of a morphism using a general 30-to-16 linear quotient",
                "absence of a morphism using the Wu octad together with the Spin12 complement",
                "an intrinsic Golay selector independent of the external Wu/hexacode marking data",
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
            "target_golay_profile": artifact["target_golay_profile"],
            "marked_big_cell_profile": artifact["marked_big_cell_profile"],
            "quotient_search": search,
            "candidate_gate": artifact["candidate_gate"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Scan the finite mixed selector family where each H6 duad independently chooses "
            "first edge, second edge, or xor collapse, using rank 12 and self-orthogonality "
            "as early pruning."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify D20, W24 row-alphabetization, per-edge prune, sector33 dual, and Wu/Spin12 marking inputs",
            "verify the marked big cell has one scalar and 15 Lambda^2 H6 two-form coordinates",
            "verify the D20 selector-duad order matches the marked two-form coordinate order",
            "compute the duplicate-xor-collapse quotient rowspace",
            "compute the lower-edge selector quotient rowspace",
            "compute the upper-edge selector quotient rowspace",
            "verify the three quotient ranks are 11, 16, and 14",
            "verify no tested quotient has rank 12",
            "verify no tested quotient is self-orthogonal",
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
                "mode_rank_histogram": artifact["quotient_search"]["mode_rank_histogram"],
                "rank12_mode_count": artifact["quotient_search"]["rank12_mode_count"],
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
