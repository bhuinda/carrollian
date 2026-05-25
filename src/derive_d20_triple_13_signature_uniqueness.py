from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_triple_13_signature_uniqueness"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
EXCLUDED_CORPUS_THEOREMS = {
    THEOREM_ID,
    "d20_raw_transport_3x3_discriminant13_search",
}

EXPECTED_TRIPLE = ["R33", "K_mixed_S", "K_pure_Sminus"]
EXPECTED_MATRIX = [[4, 0, 0], [0, 5, 1], [0, 1, 2]]
EXPECTED_LINE_HASH = "0ce6e1ef7287469a948e04d9a095fc12dd744746b5cea0b93378f65612e0ff1a"


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def theorem_id_from_report(path: Path) -> str:
    return path.parent.name


def pointer(parts: tuple[str, ...]) -> str:
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def is_certified_report(report: dict[str, Any]) -> bool:
    status = str(report.get("status", ""))
    if report.get("all_checks_pass") is True:
        return True
    return status.endswith("_CERTIFIED") or status.endswith("_PASS")


def is_matrix3(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(row, list) and len(row) == 3 for row in value)
    )


def normalize_matrix(value: list[list[Any]]) -> list[list[int]]:
    return [[int(entry) for entry in row] for row in value]


def find_descendant_discriminant_13(obj: Any) -> bool:
    if isinstance(obj, dict):
        if obj.get("discriminant") == 13 or obj.get("composite_block_discriminant") == 13:
            return True
        return any(find_descendant_discriminant_13(value) for value in obj.values())
    if isinstance(obj, list):
        return any(find_descendant_discriminant_13(value) for value in obj)
    return False


def find_descendant_order13(obj: Any) -> bool:
    if isinstance(obj, dict):
        if obj.get("strict_weak_order_count") == 13:
            return True
        if obj.get("finite_row_subgroup_order") == 13:
            return True
        if obj.get("composite_block_discriminant") == 13:
            return True
        if obj.get("anti_diagonal_line_hash") == EXPECTED_LINE_HASH:
            return True
        return any(find_descendant_order13(value) for value in obj.values())
    if isinstance(obj, list):
        return any(find_descendant_order13(value) for value in obj)
    return False


def scan_report(path: Path, report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    theorem_id = theorem_id_from_report(path)
    status = str(report.get("status", ""))
    certified = is_certified_report(report)
    records: dict[str, list[dict[str, Any]]] = {
        "triple_records": [],
        "discriminant13_records": [],
        "order13_records": [],
    }

    def walk(obj: Any, parts: tuple[str, ...]) -> None:
        if isinstance(obj, dict):
            if obj.get("discriminant") == 13 or obj.get("composite_block_discriminant") == 13:
                records["discriminant13_records"].append(
                    {
                        "theorem_id": theorem_id,
                        "report": rel(path),
                        "status": status,
                        "certified": certified,
                        "pointer": pointer(parts),
                        "basis_order": obj.get("basis_order"),
                        "key": "discriminant"
                        if obj.get("discriminant") == 13
                        else "composite_block_discriminant",
                    }
                )
            if obj.get("strict_weak_order_count") == 13:
                records["order13_records"].append(
                    {
                        "theorem_id": theorem_id,
                        "report": rel(path),
                        "status": status,
                        "certified": certified,
                        "pointer": pointer(parts),
                        "kind": "strict_weak_order_count",
                    }
                )
            if obj.get("finite_row_subgroup_order") == 13:
                records["order13_records"].append(
                    {
                        "theorem_id": theorem_id,
                        "report": rel(path),
                        "status": status,
                        "certified": certified,
                        "pointer": pointer(parts),
                        "kind": "finite_row_subgroup_order",
                    }
                )
            if obj.get("anti_diagonal_line_hash") == EXPECTED_LINE_HASH:
                records["order13_records"].append(
                    {
                        "theorem_id": theorem_id,
                        "report": rel(path),
                        "status": status,
                        "certified": certified,
                        "pointer": pointer(parts),
                        "kind": "anti_diagonal_line_hash",
                    }
                )
            basis_order = obj.get("basis_order")
            matrix = obj.get("matrix")
            if (
                isinstance(basis_order, list)
                and len(basis_order) == 3
                and is_matrix3(matrix)
            ):
                normalized_basis = [str(label) for label in basis_order]
                normalized_matrix = normalize_matrix(matrix)
                records["triple_records"].append(
                    {
                        "theorem_id": theorem_id,
                        "report": rel(path),
                        "status": status,
                        "certified": certified,
                        "pointer": pointer(parts),
                        "basis_order": normalized_basis,
                        "matrix": normalized_matrix,
                        "signature_sha256": sha_json(
                            {
                                "basis_order": normalized_basis,
                                "matrix": normalized_matrix,
                            }
                        ),
                        "has_descendant_discriminant_13": find_descendant_discriminant_13(obj),
                        "has_descendant_order13_signature": find_descendant_order13(obj),
                    }
                )
            for key, value in obj.items():
                walk(value, parts + (str(key),))
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, parts + (str(index),))

    walk(report, ())
    return records


def collect_report_paths() -> list[Path]:
    paths = sorted((D20_INVARIANTS / "theorems").glob("*/report.json"))
    return [path for path in paths if path.parent.name not in EXCLUDED_CORPUS_THEOREMS]


def build_theorem() -> dict[str, Any]:
    report_paths = collect_report_paths()
    corpus_rows = []
    triple_records = []
    discriminant13_records = []
    order13_records = []
    for path in report_paths:
        report = load_json(path)
        corpus_rows.append(
            {
                "theorem_id": theorem_id_from_report(path),
                "report": rel(path),
                "status": report.get("status"),
                "all_checks_pass": report.get("all_checks_pass"),
                "certified": is_certified_report(report),
                "sha256": sha_file(path),
            }
        )
        scanned = scan_report(path, report)
        triple_records.extend(scanned["triple_records"])
        discriminant13_records.extend(scanned["discriminant13_records"])
        order13_records.extend(scanned["order13_records"])

    certified_triple_records = [row for row in triple_records if row["certified"]]
    signature_map: dict[str, dict[str, Any]] = {}
    for row in certified_triple_records:
        entry = signature_map.setdefault(
            row["signature_sha256"],
            {
                "signature_sha256": row["signature_sha256"],
                "basis_order": row["basis_order"],
                "matrix": row["matrix"],
                "occurrence_count": 0,
                "theorem_ids": [],
                "pointers": [],
                "has_discriminant_13": False,
                "has_order13_signature": False,
            },
        )
        entry["occurrence_count"] += 1
        entry["theorem_ids"].append(row["theorem_id"])
        entry["pointers"].append(row["pointer"])
        entry["has_discriminant_13"] = (
            entry["has_discriminant_13"] or row["has_descendant_discriminant_13"]
        )
        entry["has_order13_signature"] = (
            entry["has_order13_signature"] or row["has_descendant_order13_signature"]
        )

    unique_triple_signatures = sorted(
        signature_map.values(), key=lambda row: (row["basis_order"], row["matrix"])
    )
    triple_13_signatures = [
        row
        for row in unique_triple_signatures
        if row["has_discriminant_13"] or row["has_order13_signature"]
    ]
    expected_signature = sha_json({"basis_order": EXPECTED_TRIPLE, "matrix": EXPECTED_MATRIX})
    matching_expected = [
        row for row in triple_13_signatures if row["signature_sha256"] == expected_signature
    ]
    certified_discriminant13 = [row for row in discriminant13_records if row["certified"]]
    certified_order13 = [row for row in order13_records if row["certified"]]
    summary = {
        "corpus_report_count": len(corpus_rows),
        "certified_report_count": sum(1 for row in corpus_rows if row["certified"]),
        "explicit_triple_record_count": len(triple_records),
        "certified_explicit_triple_record_count": len(certified_triple_records),
        "unique_certified_triple_signature_count": len(unique_triple_signatures),
        "certified_discriminant13_record_count": len(certified_discriminant13),
        "certified_order13_record_count": len(certified_order13),
        "triple_13_signature_count": len(triple_13_signatures),
        "hidden_transport_triple_unique_for_13_signatures": len(triple_13_signatures) == 1
        and len(matching_expected) == 1,
        "expected_hidden_transport_signature_sha256": expected_signature,
        "classification_scope": (
            "explicit certified theorem report fields under data/invariants/d20/theorems/*/report.json"
        ),
    }
    checks = {
        "corpus_has_reports": len(corpus_rows) > 100,
        "corpus_rows_hash_to_self": sha_json(corpus_rows)
        == sha_json(
            [
                {
                    "theorem_id": row["theorem_id"],
                    "report": row["report"],
                    "status": row["status"],
                    "all_checks_pass": row["all_checks_pass"],
                    "certified": row["certified"],
                    "sha256": row["sha256"],
                }
                for row in corpus_rows
            ]
        ),
        "all_triple_records_are_same_unique_signature": len(unique_triple_signatures) == 1,
        "unique_signature_is_hidden_transport_triple": len(unique_triple_signatures) == 1
        and unique_triple_signatures[0]["basis_order"] == EXPECTED_TRIPLE
        and unique_triple_signatures[0]["matrix"] == EXPECTED_MATRIX,
        "certified_discriminant13_records_exist": len(certified_discriminant13) >= 3,
        "certified_order13_records_exist": len(certified_order13) >= 4,
        "only_hidden_transport_triple_has_13_signature": summary[
            "hidden_transport_triple_unique_for_13_signatures"
        ],
        "expected_signature_occurs": len(matching_expected) == 1,
        "expected_signature_has_discriminant13": len(matching_expected) == 1
        and matching_expected[0]["has_discriminant_13"] is True,
        "expected_signature_has_order13_signature": len(matching_expected) == 1
        and matching_expected[0]["has_order13_signature"] is True,
    }
    report = {
        "schema": "d20.theorem.d20_triple_13_signature_uniqueness",
        "status": "D20_TRIPLE_13_SIGNATURE_UNIQUENESS_CERTIFIED",
        "object": "D20",
        "definition": {
            "explicit_triple": (
                "a certified theorem-report object with a length-3 basis_order and a 3x3 matrix"
            ),
            "13_signature": (
                "a discriminant-13 record, finite order-13 row-line record, strict-weak-order "
                "count 13, or the certified order-13 anti-diagonal line hash"
            ),
            "scope": (
                "classification over committed JSON theorem reports, excluding downstream "
                "meta-surveys that depend on this classifier; this is not an exhaustive "
                "search over every mathematically possible D20 triple"
            ),
        },
        "claim": (
            "Across the certified D20 theorem-report corpus, every explicit 3-object "
            "matrix triple with a discriminant-13 or order-13 clock signature has the "
            "same signature: basis (R33, K_mixed_S, K_pure_Sminus) and matrix "
            "[[4,0,0],[0,5,1],[0,1,2]]. Thus the hidden transport triple is unique "
            "within the certified explicit-triple corpus."
        ),
        "inputs": {
            "report_corpus": [input_record(path) for path in report_paths],
        },
        "derived": {
            "summary": summary,
            "corpus_rows": corpus_rows,
            "corpus_rows_sha256": sha_json(corpus_rows),
            "explicit_triple_records": triple_records,
            "explicit_triple_records_sha256": sha_json(triple_records),
            "unique_certified_triple_signatures": unique_triple_signatures,
            "unique_certified_triple_signatures_sha256": sha_json(unique_triple_signatures),
            "certified_discriminant13_records": certified_discriminant13,
            "certified_discriminant13_records_sha256": sha_json(certified_discriminant13),
            "certified_order13_records": certified_order13,
            "certified_order13_records_sha256": sha_json(certified_order13),
            "triple_13_signatures": triple_13_signatures,
            "triple_13_signatures_sha256": sha_json(triple_13_signatures),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "what_this_proves": [
                "there is one unique explicit certified triple signature with 13-arithmetic",
                "that signature is the hidden transport triple",
                "order-13 clock records and discriminant-13 records point back to the same triple",
            ],
            "what_this_does_not_prove": (
                "This does not rule out an undiscovered or unreported D20 triple. It certifies "
                "uniqueness in the current theorem-report corpus."
            ),
        },
        "next_highest_yield_item": (
            "Search the raw D20 object and transport tables for unreported 3x3 subforms with "
            "discriminant 13 to upgrade corpus uniqueness toward raw-object uniqueness."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_triple_13_signature_uniqueness_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "classify explicit certified D20 triples with discriminant-13 or order-13 signatures",
            "test uniqueness of the hidden transport triple in the theorem-report corpus",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


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
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
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
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
