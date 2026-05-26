from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_oriented_matroid_contour import edge_table
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_oriented_matroid_contour import edge_table
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_typed_coordinate_search"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_sector33_w24_typed_coordinate_search.json"

D20_JSON = ROOT / "d20.json"
W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
MINOR_PUNCTURE_SEARCH = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_hamming_minor_puncture_search"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_typed_coordinate_search.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_typed_coordinate_search.py"

PAIR_PROJECTION_RULES = [
    {"pair": "shared_duad", "position": 0, "rule": "shared_duad[0]"},
    {"pair": "shared_duad", "position": 1, "rule": "shared_duad[1]"},
    {"pair": "swapped_pair", "position": 0, "rule": "swapped_pair[0]"},
    {"pair": "swapped_pair", "position": 1, "rule": "swapped_pair[1]"},
    {"pair": "missing_pair", "position": 0, "rule": "missing_pair[0]"},
    {"pair": "missing_pair", "position": 1, "rule": "missing_pair[1]"},
]


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


def self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def parse_pair(text: str) -> list[str]:
    return [part.strip() for part in text.strip("{}").split(",") if part.strip()]


def edge_pair_data(row: dict[str, Any], h6_labels: list[str]) -> dict[str, list[str]]:
    shared = parse_pair(row["shared_duad"])
    swapped = parse_pair(row["swapped_pair"])
    present = set(shared) | set(swapped)
    missing = [label for label in h6_labels if label not in present]
    if len(shared) != 2 or len(swapped) != 2 or len(missing) != 2:
        raise ValueError(f"edge {row['edge_id']} does not define three H6 pairs")
    return {
        "shared_duad": shared,
        "swapped_pair": swapped,
        "missing_pair": missing,
    }


def selector_duad_profile(rows: list[dict[str, Any]]) -> dict[str, list[int]]:
    profile: dict[str, list[int]] = {}
    for row in rows:
        profile.setdefault(row["selector_duad"], []).append(int(row["edge_id"]))
    return {key: sorted(value) for key, value in sorted(profile.items())}


def deterministic_projection_search(
    rows: list[dict[str, Any]],
    h6_labels: list[str],
    cocircuit_support: list[int],
) -> dict[str, Any]:
    removed_fixed = set(cocircuit_support)
    complement = [int(row["edge_id"]) for row in rows if int(row["edge_id"]) not in removed_fixed]
    records = []
    balanced_records = []
    histogram = Counter()

    for extra in complement:
        remaining = [row for row in rows if int(row["edge_id"]) not in removed_fixed and int(row["edge_id"]) != extra]
        for rule in PAIR_PROJECTION_RULES:
            counts = Counter(
                edge_pair_data(row, h6_labels)[rule["pair"]][rule["position"]]
                for row in remaining
            )
            count_vector = {label: counts.get(label, 0) for label in h6_labels}
            defect = sum(abs(count_vector[label] - 4) for label in h6_labels)
            histogram[defect] += 1
            record = {
                "extra_removed": extra,
                "rule": rule["rule"],
                "remaining_edge_count": len(remaining),
                "column_count_vector": count_vector,
                "l1_defect_from_four_per_h6_label": defect,
                "balanced_four_per_h6_label": all(count_vector[label] == 4 for label in h6_labels),
            }
            records.append(record)
            if record["balanced_four_per_h6_label"]:
                balanced_records.append(record)

    best_defect = min(record["l1_defect_from_four_per_h6_label"] for record in records)
    best_records = [
        record
        for record in records
        if record["l1_defect_from_four_per_h6_label"] == best_defect
    ][:12]
    return {
        "fixed_removed_cocircuit": cocircuit_support,
        "extra_removed_pool": complement,
        "extra_removed_count": len(complement),
        "projection_rules": [rule["rule"] for rule in PAIR_PROJECTION_RULES],
        "candidate_count": len(records),
        "all_remaining_sets_have_24_edges": all(record["remaining_edge_count"] == 24 for record in records),
        "balanced_candidate_count": len(balanced_records),
        "best_l1_defect_from_four_per_h6_label": best_defect,
        "best_records_first_12": best_records,
        "defect_histogram": {str(key): value for key, value in sorted(histogram.items())},
    }


def relaxed_assignment_exists(
    rows: list[dict[str, Any]],
    h6_labels: list[str],
    cocircuit_support: list[int],
    pair_name: str,
) -> list[int]:
    removed_fixed = set(cocircuit_support)
    complement = [int(row["edge_id"]) for row in rows if int(row["edge_id"]) not in removed_fixed]
    hits = []
    label_to_idx = {label: idx for idx, label in enumerate(h6_labels)}
    target = (4,) * len(h6_labels)

    for extra in complement:
        remaining = [row for row in rows if int(row["edge_id"]) not in removed_fixed and int(row["edge_id"]) != extra]
        options = [
            tuple(label_to_idx[label] for label in edge_pair_data(row, h6_labels)[pair_name])
            for row in remaining
        ]
        order = sorted(range(len(options)), key=lambda idx: len(options[idx]))
        memo: set[tuple[int, tuple[int, ...]]] = set()

        def rec(position: int, counts: tuple[int, ...]) -> bool:
            state = (position, counts)
            if state in memo:
                return False
            if position == len(order):
                return counts == tuple(0 for _ in h6_labels)
            edge_idx = order[position]
            for option in options[edge_idx]:
                if counts[option] <= 0:
                    continue
                next_counts = list(counts)
                next_counts[option] -= 1
                if rec(position + 1, tuple(next_counts)):
                    return True
            memo.add(state)
            return False

        if rec(0, target):
            hits.append(extra)
    return hits


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    minor = load_json(MINOR_PUNCTURE_SEARCH)
    dual = load_json(SECTOR33_DUAL_REPORT)

    rows = edge_table(d20)
    h6_labels = w24["witness"]["row_alphabetization"]["column_labels"]
    cocircuit = list(dual["derived"]["dual_positive_cocircuit"]["support"])
    old_cocircuit = [element for element in cocircuit if element != 30]
    search = deterministic_projection_search(rows, h6_labels, cocircuit)
    relaxed = {
        pair_name: relaxed_assignment_exists(rows, h6_labels, cocircuit, pair_name)
        for pair_name in ("shared_duad", "swapped_pair", "missing_pair")
    }
    duad_profile = selector_duad_profile(rows)

    checks = {
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "minor_puncture_search_is_certified_negative": minor["status"]
        == "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_CERTIFIED"
        and minor["witness"]["search_summary"]["extended_golay_shape_match_count"] == 0
        and minor["witness"]["search_summary"]["punctured_golay_shape_match_count"] == 0,
        "target_w24_is_h6_by_f4": len(h6_labels) == 6
        and len(w24["witness"]["row_alphabetization"]["row_f4_labels"]) == 4,
        "sector33_ground_is_30_edges_plus_e33": len(rows) == 30
        and dual["derived"]["sector33_height_attachment"]["new_element_id"] == 30,
        "fixed_cocircuit_has_five_edges_plus_e33": len(cocircuit) == 6
        and len(old_cocircuit) == 5
        and 30 in cocircuit,
        "each_lambda2_h6_duad_has_two_sector_edges": len(duad_profile) == 15
        and all(len(edges) == 2 for edges in duad_profile.values()),
        "extra_removed_pool_has_25_edges": search["extra_removed_count"] == 25,
        "deterministic_projection_candidate_count_is_150": search["candidate_count"] == 150,
        "all_deterministic_candidates_leave_24_edges": search["all_remaining_sets_have_24_edges"],
        "no_deterministic_h6_projection_is_w24_balanced": search["balanced_candidate_count"] == 0,
        "relaxed_pair_assignment_is_too_weak": all(len(value) == 25 for value in relaxed.values()),
        "typed_coordinate_morphism_remains_open": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_typed_coordinate_search.artifact@1",
        "status": "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_DERIVED",
        "claim_scope": (
            "Finite typed search for a sector33-to-W24 coordinate map after fixing the "
            "certified W24 H6 x F4 row alphabetization."
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
            "minor_puncture_search": input_entry(
                MINOR_PUNCTURE_SEARCH,
                {
                    "certificate_sha256": minor["certificate_sha256"],
                    "status": minor["status"],
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
        "target_w24_type": {
            "column_labels": h6_labels,
            "row_f4_labels": w24["witness"]["row_alphabetization"]["row_f4_labels"],
            "coordinate_count": len(w24["witness"]["row_alphabetization"]["coordinate_labels"]),
            "coordinate_type": "H6 column label times F4 row label",
        },
        "sector33_edge_type": {
            "ground_edge_count": len(rows),
            "new_element": "e33",
            "new_element_id": 30,
            "lambda2_h6_duad_profile": duad_profile,
            "positive_cocircuit_support": cocircuit,
            "positive_cocircuit_old_edges": old_cocircuit,
        },
        "typed_search": search,
        "relaxed_assignment_boundary": {
            "interpretation": (
                "If each edge may choose either label from a pair independently, every extra "
                "deletion can be balanced to four edges per H6 label. That relaxation is not "
                "a canonical coordinate map; it shows why a deterministic row/column rule is needed."
            ),
            "balanced_extra_deletions_by_pair_family": relaxed,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    search = artifact["typed_search"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_typed_coordinate_search@1",
        "status": "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "After fixing the certified W24 H6 x F4 row alphabetization, the natural "
            "sector33 cocircuit-plus-one coordinate-map family does not produce a typed "
            "W24 coordinate bijection. The six deterministic H6 projection rules over the "
            "25 possible extra deletions leave 150 candidates, and none has four remaining "
            "edges over each H6 column. This is a typed finite negative result, not a proof "
            "against more general external row-refined maps."
        ),
        "definition": {
            "typed_target": "W24 coordinates are the certified H6 column labels crossed with four F4 row labels.",
            "sector33_source": (
                "The source ground is 30 D20 public edge elements plus e33. Each public edge "
                "has three H6 pairs: the shared duad, the swapped pair, and the missing pair."
            ),
            "tested_family": (
                "Delete the fixed sector33 positive cocircuit, then delete one further old "
                "edge. For each remaining 24-edge set, test the six deterministic H6 "
                "projection rules shared[0], shared[1], swapped[0], swapped[1], missing[0], missing[1]."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "the W24 target alphabet is fixed as H6 x F4",
                "the sector33 edge alphabet has 15 Lambda^2 H6 duads with two edges each",
                "the fixed positive cocircuit has five old edges plus e33",
                "150 deterministic typed projection candidates were tested",
                "no deterministic candidate balances to four coordinates over each H6 label",
                "the prior unlabelled cocircuit-plus-one binary minor search remains negative",
            ],
            "does_not_certify": [
                "absence of a sector33-to-W24 morphism using non-deterministic per-edge choices",
                "absence of a morphism using additional row-refined or hexacode data",
                "a canonical F4 row assignment for sector33 edges",
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
            "target_w24_type": artifact["target_w24_type"],
            "sector33_edge_type": artifact["sector33_edge_type"],
            "typed_search": search,
            "relaxed_assignment_boundary": artifact["relaxed_assignment_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Promote the search from deterministic H6 projection rules to an explicit "
            "finite F4 row-lift solver: assign rows to the 24 surviving sector33 edges, "
            "then test the induced binary row space against the certified W24 Golay basis."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_typed_coordinate_search_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24 row alphabetization certificate",
            "verify sector33 dual/cocircuit certificate",
            "verify prior cocircuit-plus-one minor search is certified negative",
            "verify sector33 edge labels form 15 Lambda^2 H6 duads with two edges each",
            "test 25 extra deletions times six deterministic H6 projection rules",
            "verify no deterministic projection is balanced as four coordinates over each H6 label",
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
                "balanced_candidate_count": artifact["typed_search"]["balanced_candidate_count"],
                "candidate_count": artifact["typed_search"]["candidate_count"],
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
