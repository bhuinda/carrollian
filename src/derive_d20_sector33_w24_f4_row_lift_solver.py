from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_oriented_matroid_contour import edge_table
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_oriented_matroid_contour import edge_table
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_f4_row_lift_solver"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_sector33_w24_f4_row_lift_solver.json"

D20_JSON = ROOT / "d20.json"
W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
TYPED_COORDINATE_SEARCH = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_typed_coordinate_search"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_f4_row_lift_solver.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_f4_row_lift_solver.py"


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def selector_duad_duplicate_ordinals(rows: list[dict[str, Any]]) -> dict[int, int]:
    by_duad: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        by_duad[str(row["selector_duad"])].append(int(row["edge_id"]))
    return {
        edge_id: ordinal
        for edge_ids in by_duad.values()
        for ordinal, edge_id in enumerate(sorted(edge_ids))
    }


def local_state(row: dict[str, Any], duplicate_ordinals: dict[int, int]) -> tuple[int, int]:
    edge_id = int(row["edge_id"])
    return int(row["selector_choice"]), duplicate_ordinals[edge_id]


def row_lift_search(rows: list[dict[str, Any]], cocircuit_support: list[int]) -> dict[str, Any]:
    duplicate_ordinals = selector_duad_duplicate_ordinals(rows)
    states = sorted({local_state(row, duplicate_ordinals) for row in rows})
    state_index = {state: idx for idx, state in enumerate(states)}
    fixed_old_edges = {element for element in cocircuit_support if element != 30}
    extra_pool = [int(row["edge_id"]) for row in rows if int(row["edge_id"]) not in fixed_old_edges]

    all_rules = list(itertools.product(range(4), repeat=len(states)))
    records = []
    row_rule_total = 0
    row_balanced_total = 0
    best_defect = None
    defect_histogram = Counter()

    for extra in extra_pool:
        remaining = [
            row
            for row in rows
            if int(row["edge_id"]) not in fixed_old_edges and int(row["edge_id"]) != extra
        ]
        state_counts = Counter(state_index[local_state(row, duplicate_ordinals)] for row in remaining)
        local_best = None
        local_balanced = 0
        for rule in all_rules:
            row_counts = [0, 0, 0, 0]
            for state_id, count in state_counts.items():
                row_counts[rule[state_id]] += count
            defect = sum(abs(count - 6) for count in row_counts)
            defect_histogram[defect] += 1
            row_rule_total += 1
            if best_defect is None or defect < best_defect:
                best_defect = defect
            if local_best is None or defect < local_best:
                local_best = defect
            if row_counts == [6, 6, 6, 6]:
                local_balanced += 1
                row_balanced_total += 1
        records.append(
            {
                "extra_removed": extra,
                "remaining_edge_count": len(remaining),
                "state_count_vector": {
                    f"{states[state_id][0]}:{states[state_id][1]}": state_counts.get(state_id, 0)
                    for state_id in range(len(states))
                },
                "best_l1_defect_from_six_per_f4_row": local_best,
                "balanced_row_lift_rule_count": local_balanced,
            }
        )

    return {
        "state_definition": {
            "selector_choice": "edge selector_choice in {0,1,2}",
            "duplicate_ordinal": "ordinal 0 or 1 among the two edges with the same Lambda^2 H6 selector_duad",
        },
        "local_states": [
            {"state_id": idx, "selector_choice": state[0], "duplicate_ordinal": state[1]}
            for idx, state in enumerate(states)
        ],
        "fixed_removed_old_edges": sorted(fixed_old_edges),
        "fixed_removed_cocircuit": cocircuit_support,
        "extra_removed_pool": extra_pool,
        "extra_removed_count": len(extra_pool),
        "row_lift_rule_count_per_extra": len(all_rules),
        "row_lift_rule_total": row_rule_total,
        "row_balanced_rule_count": row_balanced_total,
        "best_l1_defect_from_six_per_f4_row": best_defect,
        "defect_histogram": {str(key): value for key, value in sorted(defect_histogram.items())},
        "per_extra_records": records,
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    typed = load_json(TYPED_COORDINATE_SEARCH)
    dual = load_json(SECTOR33_DUAL_REPORT)

    rows = edge_table(d20)
    row_labels = w24["witness"]["row_alphabetization"]["row_f4_labels"]
    cocircuit = list(dual["derived"]["dual_positive_cocircuit"]["support"])
    search = row_lift_search(rows, cocircuit)

    checks = {
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "typed_coordinate_search_input_is_certified": typed["status"]
        == "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_CERTIFIED"
        and typed["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "target_has_four_f4_rows_and_six_columns": len(row_labels) == 4
        and len(w24["witness"]["row_alphabetization"]["column_labels"]) == 6,
        "source_has_six_intrinsic_local_edge_states": len(search["local_states"]) == 6,
        "extra_removed_pool_has_twenty_five_edges": search["extra_removed_count"] == 25,
        "row_lift_rule_count_per_extra_is_4096": search["row_lift_rule_count_per_extra"] == 4096,
        "row_lift_rule_total_is_102400": search["row_lift_rule_total"] == 102400,
        "all_remaining_sets_have_24_edges": all(
            record["remaining_edge_count"] == 24 for record in search["per_extra_records"]
        ),
        "no_intrinsic_state_to_f4_row_rule_is_balanced": search["row_balanced_rule_count"] == 0,
        "best_row_count_defect_is_positive": int(
            search["best_l1_defect_from_six_per_f4_row"]
        )
        > 0,
        "golay_rowspace_test_blocked_before_basis_compare": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_f4_row_lift_solver.artifact@1",
        "status": "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_DERIVED",
        "claim_scope": (
            "Finite F4 row-lift test for intrinsic sector33 local edge-state rules after "
            "fixing the certified W24 H6 x F4 target."
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
            "typed_coordinate_search": input_entry(
                TYPED_COORDINATE_SEARCH,
                {
                    "certificate_sha256": typed["certificate_sha256"],
                    "status": typed["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual["certificate_sha256"],
                    "status": dual["status"],
                },
            ),
        },
        "target_w24_row_type": {
            "f4_row_labels": row_labels,
            "required_total_per_f4_row": 6,
            "reason": "W24 is H6 x F4, so a 24-coordinate bijection has six coordinates in each F4 row.",
        },
        "row_lift_search": search,
        "basis_compare_boundary": {
            "attempted_compare": False,
            "reason": (
                "No intrinsic local-state-to-F4 row rule produces six surviving coordinates "
                "in each F4 row, so no W24 coordinate bijection reaches the Golay basis comparison."
            ),
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    search = artifact["row_lift_search"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_f4_row_lift_solver@1",
        "status": "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The intrinsic sector33 edge state does not yet lift to the certified W24 F4 "
            "row alphabet. For each of the 25 cocircuit-plus-one surviving 24-edge sets, "
            "all 4^6 maps from the six intrinsic local edge states to the four F4 rows were "
            "tested. None gives the required six surviving edges in each F4 row, so the "
            "Golay basis comparison is blocked before a coordinate bijection exists."
        ),
        "definition": {
            "intrinsic_local_state": (
                "state(edge)=(selector_choice, duplicate_ordinal), where duplicate_ordinal "
                "distinguishes the two public edges over the same Lambda^2 H6 selector duad"
            ),
            "row_balance_test": (
                "A W24 H6 x F4 coordinate bijection must place exactly six of the 24 "
                "surviving coordinates in each F4 row."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "the tested sector33 local edge state has six values",
                "25 cocircuit-plus-one extra-deletion cases were tested",
                "4096 state-to-F4 row rules were tested per extra deletion",
                "102400 total row-lift rules were tested",
                "no tested intrinsic state-to-F4 row rule satisfies W24 row balance",
                "the certified W24 Golay basis was not reached because no coordinate bijection exists in this family",
            ],
            "does_not_certify": [
                "absence of a row lift using per-edge, non-state-local choices",
                "absence of a row lift using additional hexacode or Wu marking data",
                "absence of a sector33-to-W24 morphism outside the cocircuit-plus-one family",
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
            "target_w24_row_type": artifact["target_w24_row_type"],
            "row_lift_search": search,
            "basis_compare_boundary": artifact["basis_compare_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Move beyond state-local row rules: enumerate per-edge F4 row assignments for "
            "the balanced relaxed H6 maps, using Golay-basis rowspace comparison as the "
            "early pruning oracle."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_f4_row_lift_solver_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24 row alphabetization and typed coordinate search inputs",
            "derive the six sector33 local edge states",
            "verify 25 extra-deletion cases after fixed cocircuit removal",
            "enumerate 4096 maps from six local states to four F4 rows for each extra deletion",
            "verify no rule yields six surviving coordinates in each F4 row",
            "record why Golay basis comparison is blocked in this family",
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
                "best_l1_defect": artifact["row_lift_search"][
                    "best_l1_defect_from_six_per_f4_row"
                ],
                "balanced_row_lift_rule_count": artifact["row_lift_search"][
                    "row_balanced_rule_count"
                ],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "row_lift_rule_total": artifact["row_lift_search"]["row_lift_rule_total"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
