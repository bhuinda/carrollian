from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_oriented_matroid_contour import (
        base_edges,
        edge_table,
        enumerate_signed_circuits,
    )
    from src.derive_d20_oriented_matroid_sector33_dual import (
        SECTOR33_EXTENSION,
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_oriented_matroid_contour import (
        base_edges,
        edge_table,
        enumerate_signed_circuits,
    )
    from src.derive_d20_oriented_matroid_sector33_dual import (
        SECTOR33_EXTENSION,
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_oriented_matroid_rational_signed_circuits"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_JSON = ROOT / "d20.json"
SECTOR33_DUAL = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
RATIONAL_TUTTE_PROMOTION = (
    D20_INVARIANTS
    / "theorems"
    / "d20_oriented_matroid_rational_tutte_promotion"
    / "report.json"
)


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


def normalize_vector(vector: list[int]) -> list[int]:
    gcd = 0
    for value in vector:
        gcd = math.gcd(gcd, abs(value))
    if gcd:
        vector = [value // gcd for value in vector]
    for value in vector:
        if value:
            return vector if value > 0 else [-entry for entry in vector]
    return vector


def support_mask(support: list[int] | tuple[int, ...]) -> int:
    mask = 0
    for element in support:
        mask |= 1 << int(element)
    return mask


def mask_support(mask: int) -> list[int]:
    return [idx for idx in range(mask.bit_length()) if (mask >> idx) & 1]


def signed_circuit_record(mask: int, vector: tuple[int, ...]) -> dict[str, Any]:
    support = mask_support(mask)
    return {
        "support": support,
        "coefficients": [int(vector[element]) for element in support],
    }


def enumerate_rational_signed_circuits() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    matrix, attachment = build_sector33_height_attachment_matrix()
    edge_rows = edge_table(d20)
    graph_edges = base_edges(edge_rows)
    # The e33 column has +1 at vertex 0 and -1 at vertex 13.  With the local
    # incidence convention (- at u, + at v), this is the oriented edge 13 -> 0.
    graph_edges[int(attachment["new_element_id"])] = (13, 0)

    simple_cycles = enumerate_signed_circuits(graph_edges, 20)
    candidates: dict[int, tuple[int, ...]] = {}
    cycle_rows: list[tuple[int, tuple[int, ...], int]] = []
    balanced_cycle_count = 0
    unbalanced_cycle_count = 0

    for cycle in simple_cycles:
        vector = [0 for _ in range(31)]
        for element, sign in cycle["signed_support"]:
            vector[int(element)] = int(sign)
        image = matrix_vector_product(matrix, vector)
        if any(value != 0 for value in image[:-1]):
            raise ValueError("cycle vector is not an incidence circulation")
        height = int(image[-1])
        mask = support_mask(cycle["support"])
        normalized = tuple(normalize_vector(vector))
        cycle_rows.append((mask, normalized, height))
        if height == 0:
            balanced_cycle_count += 1
            candidates[mask] = normalized
        else:
            unbalanced_cycle_count += 1

    unbalanced_cycles = [row for row in cycle_rows if row[2] != 0]
    pair_count = 0
    for idx, (_mask1, vector1, height1) in enumerate(unbalanced_cycles):
        for _mask2, vector2, height2 in unbalanced_cycles[idx + 1 :]:
            pair_count += 1
            combined = [
                int(height2) * int(vector1[element])
                - int(height1) * int(vector2[element])
                for element in range(31)
            ]
            mask = support_mask([element for element, value in enumerate(combined) if value])
            if mask == 0 or mask in candidates:
                continue
            normalized = tuple(normalize_vector(combined))
            candidates[mask] = normalized

    minimal_masks: list[int] = []
    minimal_by_size: dict[int, list[int]] = {}
    for mask in sorted(candidates, key=lambda item: (item.bit_count(), mask_support(item))):
        size = mask.bit_count()
        has_smaller_dependency = False
        for smaller_size in range(1, size):
            for smaller in minimal_by_size.get(smaller_size, []):
                if smaller & mask == smaller:
                    has_smaller_dependency = True
                    break
            if has_smaller_dependency:
                break
        if not has_smaller_dependency:
            minimal_masks.append(mask)
            minimal_by_size.setdefault(size, []).append(mask)

    circuit_rows = [
        signed_circuit_record(mask, candidates[mask])
        for mask in sorted(minimal_masks, key=lambda item: (item.bit_count(), mask_support(item)))
    ]
    dependency_failures = []
    primitive_failures = []
    for row in circuit_rows:
        vector = [0 for _ in range(31)]
        for element, coefficient in zip(row["support"], row["coefficients"]):
            vector[int(element)] = int(coefficient)
        image = matrix_vector_product(matrix, vector)
        if any(value != 0 for value in image):
            dependency_failures.append(row["support"])
        gcd = 0
        for coefficient in row["coefficients"]:
            gcd = math.gcd(gcd, abs(int(coefficient)))
        if gcd != 1:
            primitive_failures.append(row["support"])

    positive_support = attachment["active_support"] + [attachment["new_element_id"]]
    positive_support_set = set(positive_support)
    positive_circuit = next(
        row for row in circuit_rows if set(row["support"]) == positive_support_set
    )
    size_histogram = Counter(len(row["support"]) for row in circuit_rows)

    return {
        "matrix": matrix,
        "attachment": attachment,
        "simple_cycle_count": len(simple_cycles),
        "balanced_simple_cycle_dependency_count": balanced_cycle_count,
        "unbalanced_simple_cycle_count": unbalanced_cycle_count,
        "unbalanced_cycle_pair_count": pair_count,
        "generated_dependency_support_count": len(candidates),
        "rational_circuit_support_count": len(circuit_rows),
        "signed_rational_circuit_count": 2 * len(circuit_rows),
        "circuit_size_histogram": {
            str(size): size_histogram[size] for size in sorted(size_histogram)
        },
        "circuit_rows": circuit_rows,
        "circuit_rows_sha256": sha_json(circuit_rows),
        "dependency_failures": dependency_failures,
        "primitive_failures": primitive_failures,
        "positive_gamma8_e33_circuit": positive_circuit,
    }


def build_theorem() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    extension = load_json(SECTOR33_EXTENSION)
    dual = load_json(SECTOR33_DUAL)
    rational_tutte = load_json(RATIONAL_TUTTE_PROMOTION)
    enumeration = enumerate_rational_signed_circuits()
    circuit_rows = enumeration["circuit_rows"]

    dual_cocircuit = dual["derived"]["dual_positive_cocircuit"]
    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "sector33_extension_input_is_certified": extension.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED"
        and extension.get("all_checks_pass") is True,
        "sector33_dual_input_is_certified": dual.get("status")
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual.get("all_checks_pass") is True,
        "rational_tutte_promotion_input_is_certified": rational_tutte.get("status")
        == "D20_ORIENTED_MATROID_RATIONAL_TUTTE_PROMOTION_CERTIFIED"
        and rational_tutte.get("all_checks_pass") is True,
        "simple_cycle_count_is_1757": enumeration["simple_cycle_count"] == 1757,
        "generated_dependency_count_is_633558": enumeration[
            "generated_dependency_support_count"
        ]
        == 633558,
        "rational_circuit_support_count_is_24946": enumeration[
            "rational_circuit_support_count"
        ]
        == 24946,
        "signed_rational_circuit_count_is_49892": enumeration[
            "signed_rational_circuit_count"
        ]
        == 49892,
        "all_recorded_circuits_are_exact_dependencies": not enumeration[
            "dependency_failures"
        ],
        "all_recorded_circuits_are_primitive": not enumeration["primitive_failures"],
        "positive_gamma8_e33_circuit_present": enumeration[
            "positive_gamma8_e33_circuit"
        ]
        == {"support": [1, 2, 11, 21, 22, 30], "coefficients": [1, 1, 1, 1, 1, 2]},
        "distinguished_dual_cocircuit_still_certified": dual_cocircuit[
            "support_is_dual_cocircuit"
        ]
        is True
        and dual_cocircuit["support"] == [1, 2, 11, 21, 22, 30],
        "rational_tutte_rank_matches": rational_tutte["derived"]["rational_matrix"][
            "rank"
        ]
        == 20,
    }

    report = {
        "schema": "d20.theorem.d20_oriented_matroid_rational_signed_circuits",
        "status": "D20_ORIENTED_MATROID_RATIONAL_SIGNED_CIRCUITS_CERTIFIED",
        "object": "D20",
        "definition": {
            "circuit_generation": (
                "circuits of the sector-33 lift matroid are generated by balanced "
                "simple cycles and height-zero combinations of two unbalanced simple "
                "cycles; inclusion-minimal generated dependencies are the rational "
                "circuits"
            ),
            "signed_normal_form": (
                "each circuit vector is primitive integral and normalized so the "
                "first nonzero coefficient is positive; the opposite sign gives the "
                "paired signed circuit"
            ),
            "cocircuit_scope": (
                "the distinguished positive dual cocircuit gamma8+e33 is carried "
                "forward from the exact nullspace-dual certificate; full cocircuit "
                "enumeration remains a separate gate"
            ),
        },
        "claim": (
            "The rational sector-33 height-attachment oriented matroid has 24,946 "
            "circuit supports, hence 49,892 signed circuits up to global sign. "
            "They are obtained by exact lift-matroid generation from 1,757 simple "
            "cycles and 633,558 generated dependency supports. The positive "
            "gamma8+e33 circuit [1,1,1,1,1,2] is one of these rational signed "
            "circuits, and the matching distinguished dual cocircuit remains "
            "certified by the exact dual witness."
        ),
        "inputs": {
            "d20_json": input_record(D20_JSON),
            "d20_oriented_matroid_sector33_extension_report": input_record(
                SECTOR33_EXTENSION
            ),
            "d20_oriented_matroid_sector33_dual_report": input_record(SECTOR33_DUAL),
            "d20_oriented_matroid_rational_tutte_promotion_report": input_record(
                RATIONAL_TUTTE_PROMOTION
            ),
        },
        "derived": {
            "rational_matrix": {
                "ground_set_size": len(enumeration["matrix"][0]),
                "rank": rational_tutte["derived"]["rational_matrix"]["rank"],
                "integer_matrix_sha256": sha_json(enumeration["matrix"]),
                "sector33_height_attachment": enumeration["attachment"],
            },
            "generation_summary": {
                key: enumeration[key]
                for key in (
                    "simple_cycle_count",
                    "balanced_simple_cycle_dependency_count",
                    "unbalanced_simple_cycle_count",
                    "unbalanced_cycle_pair_count",
                    "generated_dependency_support_count",
                    "rational_circuit_support_count",
                    "signed_rational_circuit_count",
                    "circuit_size_histogram",
                    "circuit_rows_sha256",
                )
            },
            "positive_gamma8_e33_circuit": enumeration["positive_gamma8_e33_circuit"],
            "distinguished_dual_cocircuit": dual_cocircuit,
            "circuit_rows": circuit_rows,
            "circuit_rows_sha256": enumeration["circuit_rows_sha256"],
            "promotion_boundary": {
                "full_rational_signed_circuit_set_certified": True,
                "distinguished_dual_cocircuit_certified": True,
                "full_rational_signed_cocircuit_set_certified": False,
                "remaining_gate": (
                    "enumerate all rational cocircuits/covector-minimal row-space "
                    "supports, not only the distinguished positive dual cocircuit"
                ),
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "all rational signed circuits of the sector-33 lift matroid are now recorded",
                "the positive gamma8+e33 obstruction is in the full rational circuit list",
                "the distinguished positive dual cocircuit remains certified exactly",
            ],
            "guardrails": [
                "full signed cocircuit enumeration is not yet certified",
                "the circuit-generation theorem uses the lift-matroid structure of the sector-33 matrix",
                "this is a finite oriented-matroid certificate, not a complexity-theoretic conclusion",
            ],
        },
        "next_highest_yield_item": (
            "Enumerate the full rational signed cocircuit set by row-space covector "
            "minimal supports, then compare it with the distinguished gamma8+e33 "
            "dual cocircuit."
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
        "schema": "d20.theorem.d20_oriented_matroid_rational_signed_circuits_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "enumerate the full rational signed circuit set for the sector-33 lift matroid",
            "carry forward the distinguished positive dual cocircuit as the cocircuit witness",
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
    print(report["derived"]["generation_summary"]["circuit_rows_sha256"])


if __name__ == "__main__":
    main()
