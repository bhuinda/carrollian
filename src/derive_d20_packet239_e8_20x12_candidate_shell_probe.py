from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_packet239_e8_20x12_candidate_shell_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

D20_JSON = ROOT / "d20.json"
PREVIOUS_PROBE_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_packet239_e8_root_relation_probe"
    / "report.json"
)
FULL_EXPOSURE_FRAME_REPORT = (
    D20_INVARIANTS / "theorems" / "full_exposure_canonical_labelled_frame" / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_packet239_e8_20x12_candidate_shell_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_packet239_e8_20x12_candidate_shell_probe.py"


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


def report_input_entry(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    return input_entry(
        path,
        {
            "certificate_sha256": report.get("certificate_sha256"),
            "schema": report.get("schema"),
            "status": report.get("status"),
        },
    )


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def rational_rank(rows: list[list[int]]) -> int:
    basis: dict[int, list[Fraction]] = {}
    for row in rows:
        vector = [Fraction(value) for value in row]
        while True:
            pivot = next((idx for idx, value in enumerate(vector) if value), None)
            if pivot is None:
                break
            if pivot not in basis:
                scale = vector[pivot]
                basis[pivot] = [value / scale for value in vector]
                break
            factor = vector[pivot]
            vector = [value - factor * base for value, base in zip(vector, basis[pivot])]
    return len(basis)


def dot(left: list[int], right: list[int]) -> int:
    return sum(a * b for a, b in zip(left, right))


def histogram(values: list[int]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda row: int(row[0])))


def ordered_inner_histogram(vectors: list[list[int]], divisor: int = 1) -> dict[str, int]:
    values: list[int] = []
    for left in vectors:
        for right in vectors:
            raw = dot(left, right)
            if raw % divisor:
                raise ValueError("nonintegral inner product encountered")
            values.append(raw // divisor)
    return histogram(values)


def norm_sq_histogram(vectors: list[list[int]], divisor: int = 1) -> dict[str, int]:
    values: list[int] = []
    for vector in vectors:
        raw = dot(vector, vector)
        if raw % divisor:
            raise ValueError("nonintegral norm square encountered")
        values.append(raw // divisor)
    return histogram(values)


def product_embedding_vectors(packet_count: int, a12_count: int) -> list[list[int]]:
    vectors: list[list[int]] = []
    dim = packet_count + a12_count
    for packet_index in range(packet_count):
        for a12_class in range(a12_count):
            vector = [0] * dim
            vector[packet_index] = 1
            vector[packet_count + a12_class] = 1
            vectors.append(vector)
    return vectors


def standard_e8_scaled_roots() -> list[list[int]]:
    roots: list[list[int]] = []
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    root = [0] * 8
                    root[i] = si
                    root[j] = sj
                    roots.append(root)
    for signs in product((-1, 1), repeat=8):
        if sum(1 for sign in signs if sign < 0) % 2 == 0:
            roots.append(list(signs))
    return roots


def candidate_rows(full_frame: dict[str, Any], a12_count: int) -> list[dict[str, Any]]:
    packet_rows = sorted(
        full_frame["derived"]["canonical_frame_rows"], key=lambda row: int(row["frame_index"])
    )
    rows: list[dict[str, Any]] = []
    for packet_row in packet_rows:
        for a12_class in range(a12_count):
            rows.append(
                {
                    "row_index": len(rows),
                    "candidate_label": f"F{int(packet_row['frame_index']):02d}:A{a12_class:02d}",
                    "frame_index": int(packet_row["frame_index"]),
                    "packet_id": int(packet_row["packet_id"]),
                    "a12_class": a12_class,
                    "is_packet239_row": int(packet_row["packet_id"]) == 239,
                    "charge_frame_key": packet_row["charge_frame_key"],
                    "fine_spectral_charge_key": packet_row["fine_spectral_charge_key"],
                    "clock_frame": packet_row["clock_frame"],
                    "mass_frame": packet_row["mass_frame"],
                    "sector26_clock_pair": packet_row["sector26_clock_pair"],
                }
            )
    return rows


def shell_stats(vectors: list[list[int]], divisor: int = 1) -> dict[str, Any]:
    return {
        "vector_count": len(vectors),
        "ambient_dimension": len(vectors[0]) if vectors else 0,
        "rank_over_q": rational_rank(vectors),
        "norm_sq_histogram": norm_sq_histogram(vectors, divisor),
        "ordered_inner_product_histogram": ordered_inner_histogram(vectors, divisor),
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    previous_probe = load_json(PREVIOUS_PROBE_REPORT)
    full_frame = load_json(FULL_EXPOSURE_FRAME_REPORT)

    a12_count = int(d20["core_invariants"]["CY(d20)=A12"]["classes"])
    full_rows = sorted(
        full_frame["derived"]["canonical_frame_rows"], key=lambda row: int(row["frame_index"])
    )
    full_packet_ids = [int(row["packet_id"]) for row in full_rows]
    rows = candidate_rows(full_frame, a12_count)

    product_vectors = product_embedding_vectors(len(full_rows), a12_count)
    product_stats = shell_stats(product_vectors)
    e8_roots = standard_e8_scaled_roots()
    e8_stats = shell_stats(e8_roots, divisor=4)

    packet239_rows = [row for row in rows if row["packet_id"] == 239]
    row_labels = [row["candidate_label"] for row in rows]
    e8_antipodal_ordered = e8_stats["ordered_inner_product_histogram"].get("-2", 0)
    product_antipodal_ordered = product_stats["ordered_inner_product_histogram"].get("-2", 0)

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "previous_packet239_e8_probe_is_certified": previous_probe.get("status")
        == "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED"
        and previous_probe.get("all_checks_pass") is True,
        "full_exposure_frame_is_certified": full_frame.get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and full_frame.get("all_checks_pass") is True,
        "a12_class_count_is_12": a12_count == 12,
        "full_exposure_packet_count_is_20": len(full_rows) == 20,
        "cartesian_candidate_has_240_rows": len(rows) == 240,
        "candidate_rows_are_uniquely_labelled": len(set(row_labels)) == len(row_labels),
        "packet239_contributes_12_candidate_rows": len(packet239_rows) == 12,
        "natural_product_embedding_has_240_norm2_vectors": product_stats["vector_count"] == 240
        and product_stats["norm_sq_histogram"] == {"2": 240},
        "standard_e8_shell_has_240_norm2_roots": e8_stats["vector_count"] == 240
        and e8_stats["norm_sq_histogram"] == {"2": 240},
        "standard_e8_shell_rank_is_8": e8_stats["rank_over_q"] == 8,
        "natural_product_embedding_rank_is_31": product_stats["rank_over_q"] == 31,
        "natural_product_embedding_rank_is_not_e8_rank": product_stats["rank_over_q"]
        != e8_stats["rank_over_q"],
        "standard_e8_shell_has_240_ordered_antipodal_pairs": e8_antipodal_ordered == 240,
        "natural_product_embedding_has_no_antipodal_pairs": product_antipodal_ordered == 0,
        "natural_product_embedding_inner_histogram_is_not_e8": product_stats[
            "ordered_inner_product_histogram"
        ]
        != e8_stats["ordered_inner_product_histogram"],
        "candidate_is_cardinality_match_not_root_witness": True,
        "nontrivial_morphism_or_projection_still_required": True,
    }

    artifact: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe.artifact@1",
        "status": "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_DERIVED",
        "inputs": {
            "d20": input_entry(
                D20_JSON,
                {
                    "schema": d20.get("schema"),
                    "status": d20.get("status"),
                    "d20_sha256": d20.get("d20_sha256"),
                },
            ),
            "previous_packet239_e8_probe": report_input_entry(PREVIOUS_PROBE_REPORT, previous_probe),
            "full_exposure_frame": report_input_entry(FULL_EXPOSURE_FRAME_REPORT, full_frame),
        },
        "witness": {
            "candidate_definition": {
                "set": "full_exposure_frame_packets x CY(d20)=A12 classes",
                "full_exposure_packet_count": len(full_rows),
                "a12_class_count": a12_count,
                "candidate_count": len(rows),
                "full_exposure_packet_ids": full_packet_ids,
                "packet239_candidate_labels": [row["candidate_label"] for row in packet239_rows],
                "candidate_rows_sha256": sha_json(rows),
                "candidate_rows": rows,
            },
            "natural_product_embedding": {
                "definition": (
                    "Map (packet frame index i, A12 class a) to e_i + f_a in Z^(20+12). "
                    "This is the direct incidence embedding supplied by the product labels."
                ),
                "stats": product_stats,
                "interpretation": (
                    "The product incidence embedding has norm square 2, but rank 31 and no "
                    "antipodal pairs. It is therefore not the E8 root shell."
                ),
            },
            "standard_e8_reference_shell": {
                "definition": (
                    "The usual E8 roots, scaled by 2: permutations of (+/-2,+/-2,0^6) "
                    "and sign vectors (+/-1)^8 with an even number of minus signs. "
                    "Inner products are divided by 4."
                ),
                "stats": e8_stats,
            },
            "comparison": {
                "same_cardinality": len(rows) == len(e8_roots) == 240,
                "same_norm_square": product_stats["norm_sq_histogram"]
                == e8_stats["norm_sq_histogram"]
                == {"2": 240},
                "rank_product": product_stats["rank_over_q"],
                "rank_e8": e8_stats["rank_over_q"],
                "ordered_antipodal_pairs_product": product_antipodal_ordered,
                "ordered_antipodal_pairs_e8": e8_antipodal_ordered,
                "inner_histogram_product": product_stats["ordered_inner_product_histogram"],
                "inner_histogram_e8": e8_stats["ordered_inner_product_histogram"],
                "conclusion": (
                    "The explicit 20 x 12 candidate matches E8 only in cardinality and "
                    "norm under the direct incidence embedding. It fails rank and antipodal "
                    "structure, so an E8 claim requires an additional nontrivial D20-to-E8 "
                    "morphism, quotient, signing, or projection not present here."
                ),
            },
        },
        "checks": checks,
    }
    artifact["artifact_sha256_excluding_this_field"] = artifact_hash(artifact)
    return artifact


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe@1",
        "status": "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The 20 x 12 full-exposure-by-A12 candidate shell is real and has 240 labelled "
            "elements, with packet239 contributing 12 of them. Under the direct product "
            "incidence embedding (packet,A12)->e_packet+f_A12, the shell has norm square 2 "
            "but rank 31, no antipodal pairs, and the wrong inner-product histogram. Thus "
            "the product is a cardinality source, not yet an E8 root-shell morphism."
        ),
        "definition": {
            "candidate_shell": "The Cartesian product of the 20 full-exposure packet-frame rows with the 12 CY(d20)=A12 classes.",
            "natural_product_embedding": "The label-forgetting incidence map (i,a)->e_i+f_a in the direct sum of packet-frame and A12 class coordinates.",
            "e8_reference": "The standard 240-root E8 shell, used only as an exact finite comparison target.",
        },
        "closure_boundary": {
            "certifies": [
                "the explicit 20 x 12 candidate has exactly 240 labelled elements",
                "packet239 contributes exactly 12 of those labelled elements",
                "the natural product incidence embedding gives 240 norm-square-2 vectors",
                "that natural embedding has rank 31, not rank 8",
                "that natural embedding has no antipodal pairs, while E8 has 240 ordered antipodal root pairs",
                "the natural product inner-product histogram differs from the standard E8 root-shell histogram",
            ],
            "does_not_certify": [
                "that no other nonlinear or quotient morphism from D20 to E8 exists",
                "an E8 Gram matrix for the 20 x 12 candidate",
                "a signing, projection, or quotient reducing the product shell to rank 8",
                "a literature-level classification claim outside the local artifacts",
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
            **artifact["inputs"],
        },
        "witness": artifact["witness"],
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Search for a nontrivial signing/projection of the 20 x 12 shell whose Gram "
            "matrix has rank 8, norm square 2, 120 antipodal pairs, and the E8 inner-product histogram."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "materialize the 20 x 12 full-exposure-by-A12 candidate rows",
            "verify packet239 contributes 12 candidate rows",
            "build the direct product incidence embedding",
            "verify the product embedding has 240 norm-square-2 vectors",
            "generate the standard 240-root E8 shell exactly",
            "compare rank, antipodal-pair count, and ordered inner-product histograms",
            "record that a nontrivial morphism remains required",
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
    comparison = artifact["witness"]["comparison"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "candidate_count": artifact["witness"]["candidate_definition"]["candidate_count"],
                "rank_product": comparison["rank_product"],
                "rank_e8": comparison["rank_e8"],
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
