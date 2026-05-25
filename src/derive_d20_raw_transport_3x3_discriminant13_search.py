from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_raw_transport_3x3_discriminant13_search"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
D20_OBJECT = ROOT / "d20.json"
CERTIFICATE_GROUPS = ("core", "drinfeld", "geometry", "integrity", "modular", "selectors", "tube")
CERTIFICATE_ROOTS = tuple(ROOT / "data" / group for group in CERTIFICATE_GROUPS)
THEOREM_ROOT = D20_INVARIANTS / "theorems"
COMPARISON_REPORT = THEOREM_ROOT / "d20_triple_13_signature_uniqueness" / "report.json"
REPORT_TOKENS = ("transport", "sector26", "anomaly")
MATRIX_DIMENSION_LIMIT = 100
EXPECTED_MATRIX = [[4, 0, 0], [0, 5, 1], [0, 1, 2]]
EXPECTED_HIT_LOCATIONS = {
    (
        "data/invariants/d20/theorems/sector26_invariant_suite/report.json",
        "/derived/hidden_transport_form/matrix",
        (0, 1, 2),
    ),
    (
        "data/invariants/d20/theorems/finite_anomaly_counter/report.json",
        "/derived/sector26_coupling/hidden_transport_form/matrix",
        (0, 1, 2),
    ),
}


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
    return json.loads(path.read_text(encoding="utf-8-sig"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def pointer(parts: tuple[str, ...]) -> str:
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_integer_matrix(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(
            isinstance(row, list)
            and len(row) > 0
            and all(is_int(entry) for entry in row)
            for row in value
        )
        and len({len(row) for row in value}) == 1
    )


def det3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def principal_block_discriminants(matrix: list[list[int]]) -> list[dict[str, Any]]:
    records = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        if matrix[i][j] == matrix[j][i]:
            discriminant: int | None = (
                (matrix[i][i] - matrix[j][j]) ** 2 + 4 * matrix[i][j] * matrix[i][j]
            )
        else:
            discriminant = None
        records.append({"indices": [i, j], "discriminant": discriminant})
    return records


def source_kind(path: Path) -> str:
    if path == D20_OBJECT:
        return "d20_object_json"
    if any(path.is_relative_to(root) for root in CERTIFICATE_ROOTS):
        return "certificate_json"
    if path.is_relative_to(THEOREM_ROOT):
        return "transport_sector_report_json"
    return "json"


def collect_source_paths() -> list[Path]:
    report_paths = []
    for path in sorted(THEOREM_ROOT.glob("*/report.json")):
        theorem_id = path.parent.name
        if theorem_id == THEOREM_ID:
            continue
        if any(token in theorem_id for token in REPORT_TOKENS):
            report_paths.append(path)
    certificate_paths = [
        path
        for root in CERTIFICATE_ROOTS
        if root.exists()
        for path in sorted(root.glob("*.json"))
    ]
    return [D20_OBJECT, *certificate_paths, *report_paths]


def scan_json_source(path: Path) -> dict[str, Any]:
    obj = load_json(path)
    summary = {
        "path": rel(path),
        "source_kind": source_kind(path),
        "sha256": sha_file(path),
        "square_integer_matrix_count": 0,
        "exact_3x3_integer_matrix_count": 0,
        "principal_3x3_subform_count": 0,
        "max_square_dimension": 0,
        "skipped_square_matrix_count": 0,
        "discriminant13_hit_count": 0,
        "determinant13_hit_count": 0,
    }
    discriminant_hits: list[dict[str, Any]] = []
    determinant_hits: list[dict[str, Any]] = []
    skipped_square_matrices: list[dict[str, Any]] = []

    def walk(value: Any, parts: tuple[str, ...]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, parts + (str(key),))
            return
        if not isinstance(value, list):
            return

        if is_integer_matrix(value):
            row_count = len(value)
            column_count = len(value[0])
            if row_count == column_count and row_count >= 3:
                matrix_pointer = pointer(parts)
                summary["square_integer_matrix_count"] += 1
                summary["max_square_dimension"] = max(summary["max_square_dimension"], row_count)
                if row_count == 3:
                    summary["exact_3x3_integer_matrix_count"] += 1
                if row_count > MATRIX_DIMENSION_LIMIT:
                    summary["skipped_square_matrix_count"] += 1
                    skipped_square_matrices.append(
                        {
                            "path": rel(path),
                            "pointer": matrix_pointer,
                            "dimension": row_count,
                        }
                    )
                else:
                    for indices in itertools.combinations(range(row_count), 3):
                        subform = [[int(value[i][j]) for j in indices] for i in indices]
                        summary["principal_3x3_subform_count"] += 1
                        block_records = principal_block_discriminants(subform)
                        determinant = det3(subform)
                        hit_record = {
                            "path": rel(path),
                            "source_kind": summary["source_kind"],
                            "pointer": matrix_pointer,
                            "parent_dimension": row_count,
                            "indices": [int(index) for index in indices],
                            "matrix": subform,
                            "determinant": determinant,
                            "principal_block_discriminants": block_records,
                        }
                        if any(row["discriminant"] == 13 for row in block_records):
                            summary["discriminant13_hit_count"] += 1
                            discriminant_hits.append(hit_record)
                        if abs(determinant) == 13:
                            summary["determinant13_hit_count"] += 1
                            determinant_hits.append(hit_record)

        for index, child in enumerate(value):
            walk(child, parts + (str(index),))

    walk(obj, ())
    return {
        "summary": summary,
        "discriminant13_hits": discriminant_hits,
        "determinant13_hits": determinant_hits,
        "skipped_square_matrices": skipped_square_matrices,
    }


def is_expected_hit(row: dict[str, Any]) -> bool:
    location = (row["path"], row["pointer"], tuple(row["indices"]))
    return location in EXPECTED_HIT_LOCATIONS and row["matrix"] == EXPECTED_MATRIX


def build_theorem() -> dict[str, Any]:
    source_paths = collect_source_paths()
    comparison = load_json(COMPARISON_REPORT)

    source_rows = []
    discriminant_hits = []
    determinant_hits = []
    skipped_square_matrices = []
    for path in source_paths:
        scanned = scan_json_source(path)
        source_rows.append(scanned["summary"])
        discriminant_hits.extend(scanned["discriminant13_hits"])
        determinant_hits.extend(scanned["determinant13_hits"])
        skipped_square_matrices.extend(scanned["skipped_square_matrices"])

    raw_certificate_hits = [
        row
        for row in discriminant_hits
        if row["source_kind"] in {"d20_object_json", "certificate_json"}
    ]
    transport_report_hits = [
        row for row in discriminant_hits if row["source_kind"] == "transport_sector_report_json"
    ]
    known_hidden_transport_hits = [row for row in discriminant_hits if is_expected_hit(row)]
    unreported_discriminant_hits = [
        row for row in discriminant_hits if not is_expected_hit(row)
    ]
    raw_certificate_subforms = sum(
        row["principal_3x3_subform_count"]
        for row in source_rows
        if row["source_kind"] in {"d20_object_json", "certificate_json"}
    )
    transport_report_subforms = sum(
        row["principal_3x3_subform_count"]
        for row in source_rows
        if row["source_kind"] == "transport_sector_report_json"
    )

    summary = {
        "survey_scope": (
            "d20.json, consolidated data certificate JSON files, and D20 theorem reports whose ids contain "
            "transport, sector26, or anomaly"
        ),
        "matrix_dimension_limit": MATRIX_DIMENSION_LIMIT,
        "source_count": len(source_rows),
        "raw_or_certificate_source_count": sum(
            1
            for row in source_rows
            if row["source_kind"] in {"d20_object_json", "certificate_json"}
        ),
        "transport_sector_report_source_count": sum(
            1 for row in source_rows if row["source_kind"] == "transport_sector_report_json"
        ),
        "square_integer_matrix_count": sum(
            row["square_integer_matrix_count"] for row in source_rows
        ),
        "exact_3x3_integer_matrix_count": sum(
            row["exact_3x3_integer_matrix_count"] for row in source_rows
        ),
        "principal_3x3_subform_count": sum(
            row["principal_3x3_subform_count"] for row in source_rows
        ),
        "raw_or_certificate_principal_3x3_subform_count": raw_certificate_subforms,
        "transport_sector_report_principal_3x3_subform_count": transport_report_subforms,
        "max_square_dimension": max(row["max_square_dimension"] for row in source_rows),
        "skipped_square_matrix_count": len(skipped_square_matrices),
        "principal_block_discriminant13_hit_count": len(discriminant_hits),
        "raw_or_certificate_discriminant13_hit_count": len(raw_certificate_hits),
        "transport_sector_report_discriminant13_hit_count": len(transport_report_hits),
        "known_hidden_transport_hit_count": len(known_hidden_transport_hits),
        "unreported_discriminant13_hit_count": len(unreported_discriminant_hits),
        "determinant13_hit_count": len(determinant_hits),
    }

    comparison_summary = comparison.get("derived", {}).get("summary", {})
    comparison_unique = comparison.get("derived", {}).get("unique_certified_triple_signatures", [])
    checks = {
        "source_set_nonempty": len(source_rows) > 0,
        "comparison_certificate_is_certified": comparison.get("status")
        == "D20_TRIPLE_13_SIGNATURE_UNIQUENESS_CERTIFIED"
        and comparison.get("all_checks_pass") is True,
        "comparison_unique_signature_matches_expected": len(comparison_unique) == 1
        and comparison_unique[0].get("matrix") == EXPECTED_MATRIX,
        "no_square_matrix_exceeds_dimension_limit": len(skipped_square_matrices) == 0,
        "raw_and_certificate_sources_have_no_discriminant13_principal_hits": len(raw_certificate_hits) == 0,
        "transport_hits_are_exactly_known_hidden_transport_hits": len(transport_report_hits)
        == len(EXPECTED_HIT_LOCATIONS)
        and len(known_hidden_transport_hits) == len(EXPECTED_HIT_LOCATIONS),
        "no_unreported_discriminant13_hits": len(unreported_discriminant_hits) == 0,
        "no_determinant13_principal_hits": len(determinant_hits) == 0,
        "known_hits_match_expected_matrix": all(
            row["matrix"] == EXPECTED_MATRIX for row in known_hidden_transport_hits
        ),
        "known_hits_match_prior_unique_signature": comparison_summary.get(
            "hidden_transport_triple_unique_for_13_signatures"
        )
        is True,
    }

    report = {
        "schema": "d20.theorem.d20_raw_transport_3x3_discriminant13_search",
        "status": "D20_RAW_TRANSPORT_3X3_DISCRIMINANT13_SEARCH_CERTIFIED",
        "object": "D20",
        "definition": {
            "principal_3x3_subform": (
                "the 3x3 matrix obtained by selecting the same ordered triple of row and "
                "column indices from a square integer JSON matrix"
            ),
            "principal_block_discriminant": (
                "for a symmetric 2x2 principal block [[a,b],[b,c]], the integer "
                "(a-c)^2 + 4*b^2"
            ),
            "scope": (
                "bounded JSON survey only; external NPZ payload expansion is not included "
                "except for integer matrices already materialized in JSON manifests"
            ),
        },
        "claim": (
            "In the bounded raw/transport JSON survey, d20.json and every layer JSON file "
            "contain no principal 3x3 subform with principal 2x2 discriminant 13. The only "
            "transport-sector hits are the already certified hidden transport matrix "
            "[[4,0,0],[0,5,1],[0,1,2]] in sector26_invariant_suite and finite_anomaly_counter; "
            "there are no unreported discriminant-13 hits and no determinant-13 principal "
            "3x3 subforms."
        ),
        "inputs": {
            "json_survey_sources": [input_record(path) for path in source_paths],
            "comparison_certificate": input_record(COMPARISON_REPORT),
        },
        "derived": {
            "summary": summary,
            "source_rows": source_rows,
            "source_rows_sha256": sha_json(source_rows),
            "principal_block_discriminant13_hits": discriminant_hits,
            "principal_block_discriminant13_hits_sha256": sha_json(discriminant_hits),
            "known_hidden_transport_hits": known_hidden_transport_hits,
            "known_hidden_transport_hits_sha256": sha_json(known_hidden_transport_hits),
            "unreported_discriminant13_hits": unreported_discriminant_hits,
            "unreported_discriminant13_hits_sha256": sha_json(unreported_discriminant_hits),
            "determinant13_hits": determinant_hits,
            "determinant13_hits_sha256": sha_json(determinant_hits),
            "skipped_square_matrices": skipped_square_matrices,
            "skipped_square_matrices_sha256": sha_json(skipped_square_matrices),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "what_this_proves": [
                "raw d20/layer JSON does not contain an exposed discriminant-13 principal 3x3 subform",
                "transport-sector JSON records point to the same hidden transport matrix already certified",
                "within this bounded JSON survey, no new 13-arithmetic 3x3 source has appeared",
            ],
            "what_this_does_not_prove": (
                "This does not exhaustively expand every external NPZ array or prove uniqueness over "
                "all possible derived subforms. It certifies the explicit JSON raw/layer/transport survey."
            ),
        },
        "next_highest_yield_item": (
            "Expand the same 3x3 discriminant-13 search to selected NPZ matrices with explicit "
            "shape bounds and sparse sampling safeguards."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
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


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_raw_transport_3x3_discriminant13_search_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "survey raw/layer JSON and transport-sector reports for discriminant-13 3x3 subforms",
            "separate the known hidden transport matrix from any unreported 13-arithmetic hit",
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


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
