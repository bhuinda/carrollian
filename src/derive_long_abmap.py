from __future__ import annotations

import csv
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


THEOREM_ID = "long_abmap"
STATUS = "LONG_ABMAP_ATOM_BASIS_FUNCTOR_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_GCLK_CLOCK = PROOF_ROOT / "long_gclk" / "clock.csv"
LONG_TLIFT = PROOF_ROOT / "long_tlift" / "report.json"
LONG_BINC = PROOF_ROOT / "long_binc" / "report.json"
LOOP_INCIDENCE = THEOREM_ROOT / "d20_boundary_loop_step_atom_incidence" / "report.json"
LOOP_INCIDENCE_CSV = (
    THEOREM_ROOT
    / "d20_boundary_loop_step_atom_incidence"
    / "boundary_atom_step_incidence.csv"
)
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_abmap.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_abmap.py"

ORIENTATION_NAMES = ["directed", "undirected"]
ORIENTATION_CODES = {name: index for index, name in enumerate(ORIENTATION_NAMES)}

DOMAIN_COLUMNS = [
    "domain_row_id",
    "atom_id",
    "step_atom_id",
    "incidence_value",
    "candidate_basis_id",
    "identity_step_basis_flag",
]
EDGE_COLUMNS = [
    "edge_row_id",
    "orientation_code",
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "candidate_pair_count",
    "covered_flag",
    "sample_left_basis_id",
    "sample_right_basis_id",
    "sample_transition_id",
]
MATCH_COLUMNS = [
    "match_id",
    "orientation_code",
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "left_step_atom_id",
    "right_step_atom_id",
    "left_basis_id",
    "right_basis_id",
    "transition_id",
    "semantic_transition_flag",
]
PRUNE_COLUMNS = [
    "prune_row_id",
    "orientation_code",
    "iteration",
    "removed_domain_count",
    "remaining_domain_count",
    "empty_atom_count",
]
CSP_COLUMNS = [
    "orientation_code",
    "initial_domain_count",
    "edge_covered_count",
    "candidate_pair_count",
    "max_pair_multiplicity",
    "prune_iteration_count",
    "final_domain_count",
    "empty_atom_count",
    "functorial_map_exists_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "atom_count",
    "loop_step_atom_count",
    "domain_row_count",
    "affine_tick_count",
    "transition_row_count",
    "directed_edge_covered_count",
    "directed_candidate_pair_count",
    "directed_functorial_map_exists_flag",
    "directed_final_domain_count",
    "undirected_edge_covered_count",
    "undirected_candidate_pair_count",
    "undirected_max_pair_multiplicity",
    "undirected_relation_cover_flag",
    "undirected_functorial_map_exists_flag",
    "undirected_final_domain_count",
    "atom_to_basis_function_certified_flag",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "gr_source_ready_flag",
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


def support_domains(incidence_rows: list[dict[str, str]]) -> dict[int, dict[int, int]]:
    domains: dict[int, dict[int, int]] = {}
    for row in incidence_rows:
        atom_id = int(row["public_atom_id"])
        entries: dict[int, int] = {}
        for key, value in row.items():
            if not key.startswith("step_atom_"):
                continue
            step_id = int(key.split("_")[-1])
            incidence = int(value)
            if incidence != 0:
                entries[step_id] = incidence
        domains[atom_id] = entries
    return domains


def transition_maps(
    transition_rows: list[dict[str, str]],
) -> tuple[dict[tuple[int, int], dict[str, str]], dict[tuple[int, int], dict[str, str]]]:
    directed: dict[tuple[int, int], dict[str, str]] = {}
    undirected: dict[tuple[int, int], dict[str, str]] = {}
    for row in transition_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        directed[(left, right)] = row
        undirected[tuple(sorted((left, right)))] = row
    return directed, undirected


def clock_edges(clock_rows: list[dict[str, str]]) -> list[tuple[int, int, int]]:
    return [
        (int(row["visible_index"]), int(row["source_atom_id"]), int(row["target_atom_id"]))
        for row in clock_rows
    ]


def candidate_matches(
    edges: list[tuple[int, int, int]],
    domains: dict[int, dict[int, int]],
    transitions: dict[tuple[int, int], dict[str, str]],
    *,
    orientation: str,
) -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    edge_rows: list[dict[str, int]] = []
    match_rows: list[dict[str, int]] = []
    for edge_row_id, (visible_index, source_atom, target_atom) in enumerate(edges):
        matches: list[tuple[int, int, dict[str, str]]] = []
        for left in sorted(domains[source_atom]):
            for right in sorted(domains[target_atom]):
                key = (left, right)
                if orientation == "undirected":
                    key = tuple(sorted(key))
                transition = transitions.get(key)
                if transition is not None:
                    matches.append((left, right, transition))
        if matches:
            sample_left, sample_right, sample_transition = matches[0]
            sample_transition_id = int(sample_transition["transition_id"])
        else:
            sample_left = -1
            sample_right = -1
            sample_transition_id = -1
        orientation_code = ORIENTATION_CODES[orientation]
        edge_rows.append(
            {
                "edge_row_id": edge_row_id,
                "orientation_code": orientation_code,
                "visible_index": visible_index,
                "source_atom_id": source_atom,
                "target_atom_id": target_atom,
                "candidate_pair_count": len(matches),
                "covered_flag": int(bool(matches)),
                "sample_left_basis_id": sample_left,
                "sample_right_basis_id": sample_right,
                "sample_transition_id": sample_transition_id,
            }
        )
        for left, right, transition in matches:
            match_rows.append(
                {
                    "match_id": len(match_rows),
                    "orientation_code": orientation_code,
                    "visible_index": visible_index,
                    "source_atom_id": source_atom,
                    "target_atom_id": target_atom,
                    "left_step_atom_id": left,
                    "right_step_atom_id": right,
                    "left_basis_id": left,
                    "right_basis_id": right,
                    "transition_id": int(transition["transition_id"]),
                    "semantic_transition_flag": int(transition["semantic_transition_flag"]),
                }
            )
    return edge_rows, match_rows


def arc_consistency(
    edges: list[tuple[int, int, int]],
    domains_source: dict[int, dict[int, int]],
    transitions: dict[tuple[int, int], dict[str, str]],
    *,
    orientation: str,
) -> tuple[list[dict[str, int]], dict[int, set[int]]]:
    domains = {atom: set(entries) for atom, entries in domains_source.items()}
    rows: list[dict[str, int]] = []
    iteration = 0
    while True:
        iteration += 1
        removed = 0
        changed = False
        for _, source_atom, target_atom in edges:
            source_domain = set(domains[source_atom])
            target_domain = set(domains[target_atom])
            new_source = {
                left
                for left in source_domain
                if any(
                    (
                        (left, right)
                        if orientation == "directed"
                        else tuple(sorted((left, right)))
                    )
                    in transitions
                    for right in target_domain
                )
            }
            new_target = {
                right
                for right in target_domain
                if any(
                    (
                        (left, right)
                        if orientation == "directed"
                        else tuple(sorted((left, right)))
                    )
                    in transitions
                    for left in source_domain
                )
            }
            removed += len(source_domain) - len(new_source)
            removed += len(target_domain) - len(new_target)
            if new_source != source_domain:
                domains[source_atom] = new_source
                changed = True
            if new_target != target_domain:
                domains[target_atom] = new_target
                changed = True
        rows.append(
            {
                "prune_row_id": len(rows),
                "orientation_code": ORIENTATION_CODES[orientation],
                "iteration": iteration,
                "removed_domain_count": removed,
                "remaining_domain_count": sum(len(domain) for domain in domains.values()),
                "empty_atom_count": sum(int(not domain) for domain in domains.values()),
            }
        )
        if not changed:
            break
    return rows, domains


def build_rows() -> dict[str, Any]:
    gclk = load_json(LONG_GCLK)
    tlift = load_json(LONG_TLIFT)
    binc = load_json(LONG_BINC)
    loop_incidence = load_json(LOOP_INCIDENCE)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    clock_rows_raw = read_csv(LONG_GCLK_CLOCK)
    incidence_rows_raw = read_csv(LOOP_INCIDENCE_CSV)
    transition_rows_raw = read_csv(LONG_TRANSITION_CSV)
    transition_s = summary(transition_sem)

    domains = support_domains(incidence_rows_raw)
    edges = clock_edges(clock_rows_raw)
    directed_transitions, undirected_transitions = transition_maps(transition_rows_raw)

    domain_rows = []
    for atom_id in sorted(domains):
        for step_id, incidence in sorted(domains[atom_id].items()):
            domain_rows.append(
                {
                    "domain_row_id": len(domain_rows),
                    "atom_id": atom_id,
                    "step_atom_id": step_id,
                    "incidence_value": incidence,
                    "candidate_basis_id": step_id,
                    "identity_step_basis_flag": 1,
                }
            )

    all_edge_rows = []
    all_match_rows = []
    all_prune_rows = []
    csp_rows = []
    for orientation, transition_map in [
        ("directed", directed_transitions),
        ("undirected", undirected_transitions),
    ]:
        edge_rows, match_rows = candidate_matches(
            edges, domains, transition_map, orientation=orientation
        )
        prune_rows, final_domains = arc_consistency(
            edges, domains, transition_map, orientation=orientation
        )
        all_edge_rows.extend(edge_rows)
        for row in match_rows:
            row["match_id"] = len(all_match_rows)
            all_match_rows.append(row)
        for row in prune_rows:
            row["prune_row_id"] = len(all_prune_rows)
            all_prune_rows.append(row)
        csp_rows.append(
            {
                "orientation_code": ORIENTATION_CODES[orientation],
                "initial_domain_count": len(domain_rows),
                "edge_covered_count": sum(row["covered_flag"] for row in edge_rows),
                "candidate_pair_count": sum(
                    row["candidate_pair_count"] for row in edge_rows
                ),
                "max_pair_multiplicity": max(
                    row["candidate_pair_count"] for row in edge_rows
                ),
                "prune_iteration_count": len(prune_rows),
                "final_domain_count": sum(len(domain) for domain in final_domains.values()),
                "empty_atom_count": sum(int(not domain) for domain in final_domains.values()),
                "functorial_map_exists_flag": int(
                    all(bool(domain) for domain in final_domains.values())
                ),
            }
        )

    directed_csp = csp_rows[ORIENTATION_CODES["directed"]]
    undirected_csp = csp_rows[ORIENTATION_CODES["undirected"]]
    obs = {
        "input_report_count": 5,
        "input_certified_count": sum(
            certified(report)
            for report in [gclk, tlift, binc, loop_incidence, transition_sem]
        ),
        "atom_count": len(domains),
        "loop_step_atom_count": 25,
        "domain_row_count": len(domain_rows),
        "affine_tick_count": len(edges),
        "transition_row_count": len(transition_rows_raw),
        "directed_edge_covered_count": directed_csp["edge_covered_count"],
        "directed_candidate_pair_count": directed_csp["candidate_pair_count"],
        "directed_functorial_map_exists_flag": directed_csp[
            "functorial_map_exists_flag"
        ],
        "directed_final_domain_count": directed_csp["final_domain_count"],
        "undirected_edge_covered_count": undirected_csp["edge_covered_count"],
        "undirected_candidate_pair_count": undirected_csp["candidate_pair_count"],
        "undirected_max_pair_multiplicity": undirected_csp["max_pair_multiplicity"],
        "undirected_relation_cover_flag": int(undirected_csp["edge_covered_count"] == len(edges)),
        "undirected_functorial_map_exists_flag": undirected_csp[
            "functorial_map_exists_flag"
        ],
        "undirected_final_domain_count": undirected_csp["final_domain_count"],
        "atom_to_basis_function_certified_flag": 0,
        "semantic_transition_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "physical_selector_axiom_flag": 0,
        "gr_source_ready_flag": 0,
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
        "gclk": gclk,
        "tlift": tlift,
        "binc": binc,
        "loop_incidence": loop_incidence,
        "transition_sem": transition_sem,
        "domain_rows": domain_rows,
        "edge_rows": all_edge_rows,
        "match_rows": all_match_rows,
        "prune_rows": all_prune_rows,
        "csp_rows": csp_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    domain_table = table_from_rows(DOMAIN_COLUMNS, rows["domain_rows"])
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    match_table = table_from_rows(MATCH_COLUMNS, rows["match_rows"])
    prune_table = table_from_rows(PRUNE_COLUMNS, rows["prune_rows"])
    csp_table = table_from_rows(CSP_COLUMNS, rows["csp_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "loop_support_domain_coheres": obs["atom_count"] == 20
        and obs["loop_step_atom_count"] == 25
        and obs["domain_row_count"] == 90,
        "transition_and_clock_counts_match": obs["affine_tick_count"] == 20
        and obs["transition_row_count"] == 642,
        "directed_relation_is_incomplete": obs["directed_edge_covered_count"] == 15
        and obs["directed_candidate_pair_count"] == 24
        and obs["directed_functorial_map_exists_flag"] == 0
        and obs["directed_final_domain_count"] == 0,
        "undirected_relation_covers_but_is_not_functorial": obs[
            "undirected_edge_covered_count"
        ]
        == 20
        and obs["undirected_candidate_pair_count"] == 59
        and obs["undirected_max_pair_multiplicity"] == 6
        and obs["undirected_relation_cover_flag"] == 1
        and obs["undirected_functorial_map_exists_flag"] == 0
        and obs["undirected_final_domain_count"] == 0,
        "semantic_and_physical_promotion_absent": obs[
            "atom_to_basis_function_certified_flag"
        ]
        == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": domain_table.shape == (90, len(DOMAIN_COLUMNS))
        and edge_table.shape == (40, len(EDGE_COLUMNS))
        and match_table.shape == (83, len(MATCH_COLUMNS))
        and prune_table.shape == (6, len(PRUNE_COLUMNS))
        and csp_table.shape == (2, len(CSP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "atom_to_endpoint_basis_functor_obstruction",
        "summary": {
            "domain_row_count": obs["domain_row_count"],
            "directed_edge_covered_count": obs["directed_edge_covered_count"],
            "directed_candidate_pair_count": obs["directed_candidate_pair_count"],
            "undirected_edge_covered_count": obs["undirected_edge_covered_count"],
            "undirected_candidate_pair_count": obs["undirected_candidate_pair_count"],
            "undirected_max_pair_multiplicity": obs[
                "undirected_max_pair_multiplicity"
            ],
            "undirected_relation_cover_flag": obs["undirected_relation_cover_flag"],
            "undirected_functorial_map_exists_flag": obs[
                "undirected_functorial_map_exists_flag"
            ],
            "atom_to_basis_function_certified_flag": obs[
                "atom_to_basis_function_certified_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "orientation_code_map": {
            str(value): key for key, value in ORIENTATION_CODES.items()
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "domain_table_sha256": sha_array(domain_table),
        "domain_text_sha256": sha_text(csv_text(DOMAIN_COLUMNS, rows["domain_rows"])),
        "edge_table_sha256": sha_array(edge_table),
        "match_table_sha256": sha_array(match_table),
        "prune_table_sha256": sha_array(prune_table),
        "csp_table_sha256": sha_array(csp_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    abmap = {
        "schema": "long.abmap@1",
        "object": "atom_to_endpoint_basis_functor_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_ABMAP_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.abmap.report@1",
        "status": abmap["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_abmap tests the strongest current public-atom-to-endpoint "
            "candidate: use the certified 20x25 public atom to Loop-step "
            "incidence support, then identify Loop step ids with endpoint "
            "basis ids 0..24 as a finite candidate. This gives relation-level "
            "undirected coverage of all 20 affine golden ticks, but the global "
            "single-valued atom-to-basis CSP has no surviving domain after "
            "arc-consistency pruning. The bridge is therefore a non-functorial "
            "relation witness, not a certified atom-to-basis map."
        ),
        "stage_protocol": {
            "draft": "read long_gclk, long_tlift, long_binc, boundary Loop-step incidence, and long_transition_sem",
            "witness": "emit atom-step domains, per-tick relation covers, all relation matches, arc-consistency pruning rows, CSP summary rows, and observables",
            "coherence": "check Loop-support domain count, directed/undirected relation coverage, CSP domain collapse, semantic transition absence, and table hashes",
            "closure": "certify relation-level coverage but no functorial atom-to-endpoint-basis map under the identity step-to-basis candidate",
            "emit": "write long_abmap artifacts and verifier hook",
        },
        "inputs": {
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_gclk_clock": input_entry(LONG_GCLK_CLOCK),
            "long_tlift": input_entry(
                LONG_TLIFT,
                {
                    "status": rows["tlift"].get("status"),
                    "certificate_sha256": rows["tlift"].get("certificate_sha256"),
                },
            ),
            "long_binc": input_entry(
                LONG_BINC,
                {
                    "status": rows["binc"].get("status"),
                    "certificate_sha256": rows["binc"].get("certificate_sha256"),
                },
            ),
            "loop_incidence": input_entry(
                LOOP_INCIDENCE,
                {
                    "status": rows["loop_incidence"].get("status"),
                    "certificate_sha256": rows["loop_incidence"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "loop_incidence_csv": input_entry(LOOP_INCIDENCE_CSV),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "abmap": relpath(OUT_DIR / "abmap.json"),
            "domain_csv": relpath(OUT_DIR / "domain.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "match_csv": relpath(OUT_DIR / "match.csv"),
            "prune_csv": relpath(OUT_DIR / "prune.csv"),
            "csp_csv": relpath(OUT_DIR / "csp.csv"),
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
                "the certified public atom to Loop-step incidence gives 90 nonzero atom-step support memberships",
                "the directed identity step-to-basis relation covers only 15 of 20 affine golden ticks",
                "the undirected identity step-to-basis relation covers all 20 affine golden ticks with 59 candidate transition pairs",
                "the undirected cover is nonunique, with maximum tick multiplicity 6",
                "arc-consistency pruning eliminates every atom domain for both directed and undirected single-valued atom-to-basis CSPs",
                "the current evidence gives a relation-level atom/Loop-step/transition cover, not a functorial atom-to-endpoint-basis map",
                "no semantic A985 transition operation rows are materialized for this relation cover",
            ],
            "does_not_certify_because_out_of_scope": [
                "a certified Loop-step-to-endpoint-basis identification beyond the tested identity candidate",
                "a single-valued atom-to-basis functor",
                "semantic A985 transition-operation realization for the affine clock",
                "a physical selector axiom",
                "that the affine golden clock is physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Promote the relation cover into a real bridge only by supplying a "
            "certified Loop-step-to-endpoint-basis map or a multi-valued "
            "transition semantics that explicitly allows relation-valued time "
            "ticks."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.abmap.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.abmap.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "abmap": abmap,
        "domain_csv": csv_text(DOMAIN_COLUMNS, rows["domain_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "match_csv": csv_text(MATCH_COLUMNS, rows["match_rows"]),
        "prune_csv": csv_text(PRUNE_COLUMNS, rows["prune_rows"]),
        "csp_csv": csv_text(CSP_COLUMNS, rows["csp_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "domain_table": domain_table,
        "edge_table": edge_table,
        "match_table": match_table,
        "prune_table": prune_table,
        "csp_table": csp_table,
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
    write_json(OUT_DIR / "abmap.json", payloads["abmap"])
    (OUT_DIR / "domain.csv").write_text(payloads["domain_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "match.csv").write_text(payloads["match_csv"], encoding="utf-8")
    (OUT_DIR / "prune.csv").write_text(payloads["prune_csv"], encoding="utf-8")
    (OUT_DIR / "csp.csv").write_text(payloads["csp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        domain_table=payloads["domain_table"],
        edge_table=payloads["edge_table"],
        match_table=payloads["match_table"],
        prune_table=payloads["prune_table"],
        csp_table=payloads["csp_table"],
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
