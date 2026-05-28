from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen as neighborhood
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen as neighborhood
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = neighborhood.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_2114_TRIPLE_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NEIGHBORHOOD_REPORT = neighborhood.OUT_DIR / "report.json"
NEIGHBORHOOD_CERTIFICATE = (
    neighborhood.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_certificate.json"
)
NEIGHBORHOOD_TABLES = (
    neighborhood.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen.py"
)

TARGET_BLOCK = neighborhood.TARGET_BLOCK
BEST_LOCAL_BLOCK = (5, 2, 5, 5)
BEST_NONLOCAL_BLOCK = (1, 1, 4, 5)

TRIPLE_COLUMNS = [
    "triple_id",
    "triple_kind",
    "block_code_a",
    "block_code_b",
    "block_code_c",
    "state_count",
    "new_state_count",
    "edge_count",
    "new_edge_count",
    "cut_edge_count",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
    "promoted_cut_edge_count",
    "promoted_only_cut_edge_count",
    "lambda_2_x1e12",
    "cut_conductance_x1e12",
    "conductance_reduction_x1e12",
    "support_changed_flag",
    "selected_best_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "closed_metric_word_count": 0,
    "base_state_count": 1,
    "base_edge_count": 2,
    "base_cut_edge_count": 3,
    "base_cut_conductance_x1e12": 4,
    "target_block_code": 5,
    "best_local_block_code": 6,
    "best_nonlocal_block_code": 7,
    "near_nonlocal_partner_count": 8,
    "local_partner_count": 9,
    "triple_intervention_count": 10,
    "support_changing_triple_count": 11,
    "best_block_code_a": 12,
    "best_block_code_b": 13,
    "best_block_code_c": 14,
    "best_state_count": 15,
    "best_edge_count": 16,
    "best_cut_edge_count": 17,
    "best_old_cut_edge_still_cut_count": 18,
    "best_lambda_2_x1e12": 19,
    "best_cut_conductance_x1e12": 20,
    "best_conductance_reduction_x1e12": 21,
    "max_cut_edge_count": 22,
}


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def evaluate_triple(
    triple_id: int,
    triple_kind: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    base_conductance: int,
) -> dict[str, int]:
    rows_by_word = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS) | set(blocks))
    graph = pair.parent.build_graph(rows_by_word)
    automaton = pair.parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    return {
        "triple_id": triple_id,
        "triple_kind": triple_kind,
        "block_code_a": pair.block_code(blocks[0]),
        "block_code_b": pair.block_code(blocks[1]),
        "block_code_c": pair.block_code(blocks[2]),
        "state_count": len(automaton["state_rows"]),
        "new_state_count": len(automaton["state_rows"]) - geometry["state_count"],
        "edge_count": len(automaton["edge_rows"]),
        "new_edge_count": len(automaton["edge_rows"]) - geometry["edge_count"],
        "cut_edge_count": spectral["cut_edge_count"],
        "old_cut_edge_still_cut_count": spectral["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": spectral["old_cut_edge_same_side_count"],
        "promoted_cut_edge_count": spectral["promoted_cut_edge_count"],
        "promoted_only_cut_edge_count": spectral["promoted_only_cut_edge_count"],
        "lambda_2_x1e12": spectral["lambda_2_x1e12"],
        "cut_conductance_x1e12": spectral["cut_conductance_x1e12"],
        "conductance_reduction_x1e12": base_conductance
        - spectral["cut_conductance_x1e12"],
        "support_changed_flag": int(
            spectral["old_cut_edge_still_cut_count"] < 6
            or spectral["old_cut_edge_same_side_count"] > 0
        ),
        "selected_best_flag": 0,
    }


def build_triples(
    near_nonlocal_partners: list[tuple[int, int, int, int]],
    local_partners: list[tuple[int, int, int, int]],
) -> list[tuple[int, tuple[tuple[int, int, int, int], ...]]]:
    triples: list[tuple[int, tuple[tuple[int, int, int, int], ...]]] = []
    seen: set[tuple[int, int, int]] = set()

    def add(kind: int, blocks: tuple[tuple[int, int, int, int], ...]) -> None:
        key = tuple(sorted(pair.block_code(block) for block in blocks))
        if key in seen:
            return
        seen.add(key)
        triples.append((kind, blocks))

    for partner in near_nonlocal_partners:
        add(1, (TARGET_BLOCK, BEST_LOCAL_BLOCK, partner))
    for partner in local_partners:
        add(2, (TARGET_BLOCK, BEST_NONLOCAL_BLOCK, partner))
    return triples


def build_payload_rows() -> dict[str, Any]:
    neighborhood_report = load_json(NEIGHBORHOOD_REPORT)
    neighborhood_certificate = load_json(NEIGHBORHOOD_CERTIFICATE)
    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    neighborhood_rows = neighborhood.build_payload_rows()
    near_nonlocal_partners = neighborhood_rows["near_nonlocal_partners"]
    local_partners = neighborhood_rows["local_partners"]
    base_spectral = pair.parent.table_rows(
        np.asarray(
            np.load(pair.SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        pair.parent.SPECTRAL_CUT_COLUMNS,
    )[0]
    triples = build_triples(near_nonlocal_partners, local_partners)
    triple_rows = [
        evaluate_triple(
            triple_id,
            triple_kind,
            blocks,
            records,
            geometry,
            base_spectral["cut_conductance_x1e12"],
        )
        for triple_id, (triple_kind, blocks) in enumerate(triples)
    ]
    best = min(
        triple_rows,
        key=lambda row: (
            row["support_changed_flag"],
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["block_code_a"],
            row["block_code_b"],
            row["block_code_c"],
        ),
    )
    best["selected_best_flag"] = 1
    observable_values = {
        "closed_metric_word_count": len(records),
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_spectral["cut_conductance_x1e12"],
        "target_block_code": pair.block_code(TARGET_BLOCK),
        "best_local_block_code": pair.block_code(BEST_LOCAL_BLOCK),
        "best_nonlocal_block_code": pair.block_code(BEST_NONLOCAL_BLOCK),
        "near_nonlocal_partner_count": len(near_nonlocal_partners),
        "local_partner_count": len(local_partners),
        "triple_intervention_count": len(triple_rows),
        "support_changing_triple_count": sum(
            row["support_changed_flag"] for row in triple_rows
        ),
        "best_block_code_a": best["block_code_a"],
        "best_block_code_b": best["block_code_b"],
        "best_block_code_c": best["block_code_c"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best[
            "old_cut_edge_still_cut_count"
        ],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best[
            "conductance_reduction_x1e12"
        ],
        "max_cut_edge_count": max(row["cut_edge_count"] for row in triple_rows),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return {
        "neighborhood_report": neighborhood_report,
        "neighborhood_certificate": neighborhood_certificate,
        "near_nonlocal_partners": near_nonlocal_partners,
        "local_partners": local_partners,
        "triple_rows": triple_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    triple_table = table_from_rows(TRIPLE_COLUMNS, rows["triple_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(row for row in rows["triple_rows"] if row["selected_best_flag"])
    near_nonlocal_codes = [
        pair.block_code(block) for block in rows["near_nonlocal_partners"]
    ]
    local_partner_codes = [pair.block_code(block) for block in rows["local_partners"]]

    checks = {
        "neighborhood_screen_report_certified": rows["neighborhood_report"].get(
            "status"
        )
        == neighborhood.STATUS,
        "neighborhood_screen_certificate_certified": rows[
            "neighborhood_certificate"
        ].get("status")
        == neighborhood.STATUS,
        "triple_scope_matches_2114_centered_anchors": (
            observable_values["target_block_code"],
            observable_values["best_local_block_code"],
            observable_values["best_nonlocal_block_code"],
            observable_values["near_nonlocal_partner_count"],
            observable_values["local_partner_count"],
            observable_values["triple_intervention_count"],
        )
        == (2114, 5255, 1145, 14, 13, 26),
        "no_2114_centered_triple_changes_old_cut_support": observable_values[
            "support_changing_triple_count"
        ]
        == 0,
        "best_2114_centered_triple_is_2114_5255_1521": (
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
            observable_values["best_block_code_c"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_lambda_2_x1e12"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (2114, 5255, 1521, 957, 3_063, 6, 6, 1_967_643_000, 2_610_966_000, 1_718_038_000),
        "table_shapes_match_codebooks": (
            tuple(triple_table.shape),
            tuple(observable_table.shape),
        )
        == ((26, len(TRIPLE_COLUMNS)), (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS))),
    }

    witness = {
        "target_block_code": pair.block_code(TARGET_BLOCK),
        "best_local_block_code": pair.block_code(BEST_LOCAL_BLOCK),
        "best_nonlocal_block_code": pair.block_code(BEST_NONLOCAL_BLOCK),
        "near_nonlocal_partner_codes": near_nonlocal_codes,
        "local_partner_codes": local_partner_codes,
        "triple_intervention_count": observable_values["triple_intervention_count"],
        "support_changing_triple_count": observable_values[
            "support_changing_triple_count"
        ],
        "best_triple": best,
        "triple_table_sha256": pair.parent.sha_array(triple_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    screen_payload = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen@1",
        "object": "C985->d20",
        "parent": NEIGHBORHOOD_REPORT.relative_to(ROOT).as_posix(),
        "search_scope": {
            "target_block_code": pair.block_code(TARGET_BLOCK),
            "fixed_local_anchor": pair.block_code(BEST_LOCAL_BLOCK),
            "fixed_nonlocal_anchor": pair.block_code(BEST_NONLOCAL_BLOCK),
            "near_nonlocal_partner_codes": near_nonlocal_codes,
            "local_partner_codes": local_partner_codes,
            "interventions": (
                "2114+5255 plus every two-hop nonlocal partner, and "
                "2114+1145 plus every local cut-touch partner, deduplicated"
            ),
        },
        "summary": {
            "best_block_codes": [
                best["block_code_a"],
                best["block_code_b"],
                best["block_code_c"],
            ],
            "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
            "best_old_cut_edge_still_cut_count": best[
                "old_cut_edge_still_cut_count"
            ],
            "support_changing_triple_count": observable_values[
                "support_changing_triple_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_NONLOCAL_2114_TRIPLE_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The bounded 2114-centered triple screen tests 26 triples anchored "
            "on 2114+5255 and 2114+1145. The best triple is 2114+5255+1521, "
            "which lowers conductance to 2610966000/1e12 while preserving all "
            "six old cut edges."
        ),
        "stage_protocol": {
            "draft": "start from the certified focused 2114 pair neighborhood",
            "witness": "construct triples using the best local and best adjacent nonlocal anchors",
            "coherence": "rebuild the promoted grammar and fresh spectral cut for each bounded triple",
            "closure": "certify the bounded 2114-centered triple screen and selected non-opening best triple",
            "emit": "emit triple, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "neighborhood_report": pair.parent.input_entry(
                NEIGHBORHOOD_REPORT,
                {
                    "status": rows["neighborhood_report"].get("status"),
                    "certificate_sha256": rows["neighborhood_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "neighborhood_certificate": pair.parent.input_entry(
                NEIGHBORHOOD_CERTIFICATE
            ),
            "neighborhood_tables": pair.parent.input_entry(NEIGHBORHOOD_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "triple_screen": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen.json"
            ),
            "triple_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_2114_triple_screen_interventions.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_nonlocal_2114_triple_screen_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "bounded 2114-centered triple screen anchored on 5255 and 1145",
                "fresh spectral-cut comparison for every tested triple",
                "2114+5255+1521 is the best bounded triple and still preserves old six-edge support",
            ],
            "does_not_certify_because_not_required": [
                "all 2114 triples over the full partner set",
                "quadruple or larger 2114-centered recouplings",
                "all nonlocal windows beyond the focused 2114 neighborhood",
                "compiler integration of the screened recoupling rule",
            ],
        },
        "next_highest_yield_item": (
            "Escalate around the new best triple 2114+5255+1521: test one "
            "additional local/nonlocal layer or derive why the old six-edge "
            "aperture is invariant under this conductance-decreasing chain."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "2114+5255+1521 is the current best bounded 2114-centered triple",
            "the conductance keeps decreasing while the six old cut edges remain invariant",
            "the next test should either add one layer or extract the invariant mechanism",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified 2114 neighborhood screen",
            "construct 2114-centered triples anchored on 5255 and 1145",
            "test every bounded triple against fresh spectral cuts",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "triple_screen": screen_payload,
        "triple_csv": pair.csv_text(TRIPLE_COLUMNS, rows["triple_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "triple_table": triple_table,
        "observable_table": observable_table,
        "certificate": certificate,
        "report": report,
        "manifest": manifest,
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen.json",
        payloads["triple_screen"],
    )
    (OUT_DIR / "sixj_nonlocal_2114_triple_screen_interventions.csv").write_text(
        payloads["triple_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_nonlocal_2114_triple_screen_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_tables.npz",
        triple_table=payloads["triple_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_certificate.json",
        payloads["certificate"],
    )
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
