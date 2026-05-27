from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_boundary_neighborhood_stress_graph"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
ARTIFACT_PATH = OUT_DIR / "artifact.json"
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
ATLAS_NPZ = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
ATLAS_REPORT = ATLAS_DIR / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_boundary_neighborhood_stress_graph.py"
VALIDATOR = ROOT / "src" / "certify_c985_d20_boundary_neighborhood_stress_graph.py"

COL_ATOM = 0
COL_COMPLEMENT = 1
COL_SUPPORT = 3
COL_MASS = 4
COL_RELATION_COUNT = 5
COL_SIGNATURE_COUNT = 6
COL_SELF_TRANSPOSE = 7
COL_RELATION_SIZE = 8
COL_OUTPUT_SUPPORT = 11
COL_OUTPUT_MASS = 14


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
    out = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        out.update(extra)
    return out


def self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def atom_feature_matrix(atom_table: np.ndarray) -> np.ndarray:
    cols = [
        COL_SUPPORT,
        COL_MASS,
        COL_RELATION_COUNT,
        COL_SIGNATURE_COUNT,
        COL_SELF_TRANSPOSE,
        COL_RELATION_SIZE,
        COL_OUTPUT_SUPPORT,
        COL_OUTPUT_MASS,
    ]
    features = np.log1p(atom_table[:, cols].astype(float))
    mean = features.mean(axis=0)
    std = features.std(axis=0)
    std = np.where(std > 0.0, std, 1.0)
    return (features - mean) / std


def complement_tension(atom_table: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    complements = atom_table[:, COL_COMPLEMENT].astype(int)
    support = atom_table[:, COL_SUPPORT].astype(float)
    mass = atom_table[:, COL_MASS].astype(float)
    support_delta = np.abs(support - support[complements])
    mass_delta = np.abs(mass - mass[complements])
    support_norm = support_delta / max(1.0, float(support_delta.max()))
    mass_norm = mass_delta / max(1.0, float(mass_delta.max()))
    magnitude = 0.68 * mass_norm + 0.32 * support_norm
    polarity = np.where(np.arange(atom_table.shape[0]) <= complements, 1.0, -1.0)
    return magnitude, magnitude * polarity


def neighborhood_graph(atom_table: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    features = atom_feature_matrix(atom_table)
    diff = features[:, None, :] - features[None, :, :]
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    upper = dist[np.triu_indices_from(dist, k=1)]
    sigma = float(np.median(upper)) or 1.0
    similarity = np.exp(-(dist * dist) / (2.0 * sigma * sigma))
    np.fill_diagonal(similarity, 0.0)
    tension, signed_tension = complement_tension(atom_table)
    complements = atom_table[:, COL_COMPLEMENT].astype(int)
    weight = similarity * (0.68 + 0.32 * (1.0 - np.abs(tension[:, None] - tension[None, :])))
    for atom_id, complement_id in enumerate(complements):
        weight[atom_id, complement_id] += 0.55
    row_sums = weight.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums > 0.0, row_sums, 1.0)
    normalized = weight / row_sums
    rows: list[dict[str, Any]] = []
    for atom_id in range(atom_table.shape[0]):
        order = np.argsort(normalized[atom_id])[::-1]
        neighbors = [
            {
                "atom_id": int(idx),
                "weight": round(float(normalized[atom_id, idx]), 10),
                "signed_tension": round(float(signed_tension[idx]), 10),
            }
            for idx in order[:5]
            if idx != atom_id and float(normalized[atom_id, idx]) > 0.0
        ]
        rows.append(
            {
                "atom_id": atom_id,
                "complement_atom_id": int(complements[atom_id]),
                "tension": round(float(tension[atom_id]), 10),
                "signed_tension": round(float(signed_tension[atom_id]), 10),
                "neighbors": neighbors,
            }
        )
    return normalized, signed_tension, rows


def build_artifact() -> dict[str, Any]:
    atlas_report = load_json(ATLAS_REPORT)
    with np.load(ATLAS_NPZ, allow_pickle=False) as npz:
        atom_table = np.asarray(npz["atom_table"], dtype=np.int64)
    weights, signed_tension, graph_rows = neighborhood_graph(atom_table)
    row_sums = weights.sum(axis=1)
    complements = atom_table[:, COL_COMPLEMENT].astype(int)
    checks = {
        "atlas_report_passed": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED"
        and atlas_report.get("all_checks_pass") is True,
        "atom_table_shape_is_20_by_15": tuple(atom_table.shape) == (20, 15),
        "complement_map_is_involutive": all(int(complements[int(c)]) == i for i, c in enumerate(complements)),
        "graph_rows_are_stochastic": bool(np.allclose(row_sums, 1.0, atol=1e-10)),
        "all_nodes_have_five_neighbors": all(len(row["neighbors"]) == 5 for row in graph_rows),
        "signed_tension_has_two_polarities": bool(np.any(signed_tension > 0.0) and np.any(signed_tension < 0.0)),
    }
    status = (
        "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        if all(checks.values())
        else "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_PROVISIONAL"
    )
    payload: dict[str, Any] = {
        "schema": "c985.d20_boundary_neighborhood_stress_graph.artifact@1",
        "status": status,
        "source": {
            "atlas_npz": input_entry(ATLAS_NPZ),
            "atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "D20 boundary-neighborhood stress graph",
            "node": "one C985 atlas-projected D20 boundary atom",
            "edge_weight": (
                "row-normalized feature-neighborhood similarity from NPZ atom_table columns, "
                "with complement-pair boost and complement-tension compatibility"
            ),
            "stress": (
                "signed complement-pair tension from tensor mass/support imbalance; positive and "
                "negative signs distinguish the two atoms in each complement pair"
            ),
            "renderer_use": "smooth physical mask over the RGBA atom without changing canonical RGBA bytes",
        },
        "witness": {
            "summary": {
                "node_count": int(atom_table.shape[0]),
                "neighbor_count_per_node": 5,
                "row_sum_min": float(row_sums.min()),
                "row_sum_max": float(row_sums.max()),
                "signed_tension_min": float(signed_tension.min()),
                "signed_tension_max": float(signed_tension.max()),
                "mean_abs_signed_tension": float(np.mean(np.abs(signed_tension))),
                "weight_matrix_sha256": sha_json(np.round(weights, 12).tolist()),
            },
            "graph_rows": graph_rows,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(
        payload, "artifact_sha256_excluding_this_field"
    )
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report = {
        "schema": "c985.d20_boundary_neighborhood_stress_graph@1",
        "status": artifact["status"],
        "claim": (
            "The certified C985 D20 boundary atlas induces a deterministic 20-node stress-neighborhood "
            "graph usable as a smooth physical mask over the live RGBA atom."
        ),
        "stages": {
            "draft": "build a graph from NPZ atom_table features",
            "witness": "record row-normalized graph rows and signed complement tension",
            "coherence": "check complement involution, stochastic rows, and two-polarity tension",
            "closure": "certify graph as renderer mask input only",
            "emit": "publish graph rows and hashes",
        },
        "definition": artifact["definition"],
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                },
            ),
            "validator": input_entry(VALIDATOR),
            **artifact["source"],
        },
        "witness": artifact["witness"],
        "checks": artifact["checks"],
        "all_checks_pass": all(artifact["checks"].values()),
        "closure_boundary": {
            "certifies": [
                "deterministic stress-neighborhood graph from the C985 D20 atlas NPZ",
                "signed complement-pair stress suitable for visualization",
            ],
            "does_not_certify": [
                "physical stress-energy tensor",
                "unitary/modular normalization",
                "browser compositor pixel output",
            ],
        },
        "next_highest_yield_item": (
            "Use browser getImageData once available to compare the stress-mask overlay against "
            "the graph-row constants embedded in the renderer."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "c985.d20_boundary_neighborhood_stress_graph_manifest@1",
        "name": THEOREM_ID,
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
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                **report["witness"]["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
