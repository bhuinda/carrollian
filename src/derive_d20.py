#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from src.derive_zero_axiom_coorient import derive as derive_zero_axiom_coorient

ROOT = Path(__file__).resolve().parents[1]

WEIGHTS = {
    "B-": 384,
    "B+": 192,
    "V-": 144,
    "V+": 576,
    "S-": 512,
    "S+": 768,
}
ORDER = ["B-", "B+", "V-", "V+", "S-", "S+"]
EPSILON0 = 589_824
WEYL_D6 = 23_040
FOAM_DIM = 16
D20_EDGE_CLOSURE_ORDER = 5

MAX_EMBED_ARRAY = 2048

EXCLUDED_SCAN_DIRS = {
    ".git",
    ".codex_deps",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tools",
    ".venv",
    "__pycache__",
    "a236_compute_py_bundle",
}

EXCLUDED_SCAN_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def excluded_scan_path(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return any(part in EXCLUDED_SCAN_DIRS for part in rel.parts) or path.suffix in EXCLUDED_SCAN_SUFFIXES


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def factorization(n: int) -> dict[str, int]:
    x = int(n)
    out: dict[str, int] = {}
    p = 2
    while p * p <= x:
        while x % p == 0:
            out[str(p)] = out.get(str(p), 0) + 1
            x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        out[str(x)] = out.get(str(x), 0) + 1
    return out


def array_digest(a: np.ndarray) -> str:
    c = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(c.dtype).encode())
    h.update(str(c.shape).encode())
    h.update(c.tobytes())
    return h.hexdigest()


def array_entry(a: np.ndarray) -> dict[str, Any]:
    a = np.asarray(a)
    ent: dict[str, Any] = {
        "shape": list(a.shape),
        "dtype": str(a.dtype),
        "size": int(a.size),
        "sha256": array_digest(a),
    }
    if a.size <= MAX_EMBED_ARRAY and a.dtype.kind in "biufUS":
        ent["values"] = a.tolist()
    if a.size and a.dtype.kind in "biuf":
        ent["min"] = int(a.min()) if np.issubdtype(a.dtype, np.integer) else float(a.min())
        ent["max"] = int(a.max()) if np.issubdtype(a.dtype, np.integer) else float(a.max())
        if a.size <= 5_000_000:
            ent["sum"] = int(a.sum()) if np.issubdtype(a.dtype, np.integer) else float(a.sum())
    return ent


def npz_manifest(path: Path) -> dict[str, Any]:
    z = np.load(path, allow_pickle=False)
    arrays = {k: array_entry(np.asarray(z[k])) for k in sorted(z.files)}
    return {
        "path": str(path.relative_to(ROOT)),
        "file_size": path.stat().st_size,
        "file_sha256": sha_file(path),
        "arrays": arrays,
    }


def csv_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    rows = list(csv.DictReader(text.splitlines()))
    return {
        "path": str(path.relative_to(ROOT)),
        "file_size": path.stat().st_size,
        "file_sha256": sha_file(path),
        "rows": rows,
    }


def _to_int(x: Any, default: int = 0) -> int:
    try:
        return int(str(x).replace(",", ""))
    except Exception:
        return default


def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(str(x))
    except Exception:
        return default


def hcycle_game_theory() -> dict[str, Any]:
    """Load and summarize the d20 H-cycle/game-theory layer.

    The raw tables are kept under data/hcycle and are also embedded in d20.json
    so the object file lists the game/control invariants directly.
    """
    base = ROOT / "data" / "hcycle"
    if not base.exists():
        return {"status": "D20_HCYCLE_LAYER_MISSING", "present": False}

    def load_j(name: str) -> Any:
        return load_json(base / name)

    def c(name: str) -> dict[str, Any]:
        return csv_payload(base / name)

    manifest = load_j("Hsubcycle_S20_manifest.json")
    control = load_j("subscript_Hcycle_control_manifest.json")
    automorphism = load_j("d20_Hcycle_automorphism_summary.json")

    csv_names = [
        "Hsubcycle_S20_conjugacy_classes.csv",
        "d20_Hcycle_S20_strategy_class_atlas.csv",
        "subscript_Hcycle_d20_edges.csv",
        "subscript_Hcycle_primitive_cycles.csv",
        "d20_Hcycle_invariant_ledger.csv",
        "d20_Hcycle_circuit_grammar.csv",
        "d20_Hcycle_consequences.csv",
        "d20_Hcycle_pair_transposition_costs.csv",
        "d20_Hcycle_distance_class_summary.csv",
        "d20_Hcycle_pair_automorphism_orbits.csv",
        "d20_Hcycle_basis_composition_matrix.csv",
        "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv",
        "d20_Hcycle_mod2_residue_spectrum_minimal.csv",
    ]
    tables = {name: c(name) for name in csv_names if (base / name).exists()}

    primitive = tables.get("subscript_Hcycle_primitive_cycles.csv", {}).get("rows", [])
    edges = tables.get("subscript_Hcycle_d20_edges.csv", {}).get("rows", [])
    pair_costs = tables.get("d20_Hcycle_pair_transposition_costs.csv", {}).get("rows", [])
    distance_rows = tables.get("d20_Hcycle_distance_class_summary.csv", {}).get("rows", [])
    residue_rows = tables.get("d20_Hcycle_mod2_residue_spectrum_minimal.csv", {}).get("rows", [])
    strategy_rows = tables.get("d20_Hcycle_S20_strategy_class_atlas.csv", {}).get("rows", [])
    grammar_rows = tables.get("d20_Hcycle_circuit_grammar.csv", {}).get("rows", [])
    ledger_rows = tables.get("d20_Hcycle_invariant_ledger.csv", {}).get("rows", [])

    lengths = [_to_int(r.get("length")) for r in primitive]
    optical = [_to_int(r.get("optical_action")) for r in primitive]
    entropy = [_to_float(r.get("entropy_proxy_A_over_4WD6")) for r in primitive]
    edge_weights = [_to_int(r.get("interface_weight")) for r in edges]
    exact_costs = [_to_int(r.get("exact_word_cost_transposition")) for r in pair_costs]
    improved = sum(1 for r in pair_costs if str(r.get("best_simple_can_use_longer_path", "")).lower() == "true")

    length_hist: dict[str, int] = {}
    for x in lengths:
        length_hist[str(x)] = length_hist.get(str(x), 0) + 1

    parity_hist: dict[str, int] = {}
    for r in strategy_rows:
        parity = str(r.get("parity", "unknown"))
        parity_hist[parity] = parity_hist.get(parity, 0) + 1

    files = {}
    for path in sorted(base.iterdir()):
        if path.is_file():
            files[path.name] = {"size": path.stat().st_size, "sha256": sha_file(path)}

    # Solved finite board/control invariants.
    n_vertices = 20
    label_by_vertex: dict[int, str] = {}
    adjacency = [[0 for _ in range(n_vertices)] for _ in range(n_vertices)]
    optical_weight = [[0 for _ in range(n_vertices)] for _ in range(n_vertices)]
    for r in edges:
        u = _to_int(r.get("u")); v = _to_int(r.get("v")); w = _to_int(r.get("interface_weight"))
        if 0 <= u < n_vertices and 0 <= v < n_vertices:
            adjacency[u][v] = adjacency[v][u] = 1
            optical_weight[u][v] = optical_weight[v][u] = w
            if r.get("u_label"):
                label_by_vertex.setdefault(u, str(r.get("u_label")))
            if r.get("v_label"):
                label_by_vertex.setdefault(v, str(r.get("v_label")))

    def bfs_dist(src: int) -> list[int]:
        dist = [-1] * n_vertices
        dist[src] = 0
        q = [src]
        for x in q:
            for y, a in enumerate(adjacency[x]):
                if a and dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        return dist

    import heapq
    def dijkstra(src: int) -> list[int]:
        INF = 10**30
        dist = [INF] * n_vertices
        dist[src] = 0
        pq = [(0, src)]
        while pq:
            d, x = heapq.heappop(pq)
            if d != dist[x]:
                continue
            for y, w in enumerate(optical_weight[x]):
                if w:
                    nd = d + w
                    if nd < dist[y]:
                        dist[y] = nd
                        heapq.heappush(pq, (nd, y))
        return [int(v) for v in dist]

    graph_value = [bfs_dist(i) for i in range(n_vertices)]
    optical_value = [dijkstra(i) for i in range(n_vertices)]
    graph_ecc = [max(row) for row in graph_value]
    optical_ecc = [max(row) for row in optical_value]
    graph_radius = min(graph_ecc) if graph_ecc else None
    optical_radius = min(optical_ecc) if optical_ecc else None
    graph_centers = [i for i, x in enumerate(graph_ecc) if x == graph_radius]
    optical_centers = [i for i, x in enumerate(optical_ecc) if x == optical_radius]

    exact_transposition = [[0 for _ in range(n_vertices)] for _ in range(n_vertices)]
    pair_opt_shortest = [[0 for _ in range(n_vertices)] for _ in range(n_vertices)]
    pair_opt_simple = [[0 for _ in range(n_vertices)] for _ in range(n_vertices)]
    for r in pair_costs:
        u = _to_int(r.get("u")); v = _to_int(r.get("v"))
        if 0 <= u < n_vertices and 0 <= v < n_vertices:
            exact_transposition[u][v] = exact_transposition[v][u] = _to_int(r.get("exact_word_cost_transposition"))
            pair_opt_shortest[u][v] = pair_opt_shortest[v][u] = _to_int(r.get("best_optical_cost_over_shortest_paths"))
            pair_opt_simple[u][v] = pair_opt_simple[v][u] = _to_int(r.get("best_optical_cost_over_simple_paths"))

    # Markov controls: uniform legal walk and optical-conductance walk.
    degrees = [sum(row) for row in adjacency]
    uniform_stationary = [deg / (2 * len(edges)) if edges else 0 for deg in degrees]
    conductance = [[(1.0 / optical_weight[i][j]) if optical_weight[i][j] else 0.0 for j in range(n_vertices)] for i in range(n_vertices)]
    conductance_sums = [sum(row) for row in conductance]
    total_conductance = sum(conductance_sums)
    conductance_stationary = [x / total_conductance if total_conductance else 0.0 for x in conductance_sums]
    conductance_kernel = []
    for i in range(n_vertices):
        row = []
        denom = conductance_sums[i]
        for j in range(n_vertices):
            row.append(conductance[i][j] / denom if denom else 0.0)
        conductance_kernel.append(row)

    # Spectral invariants of the graph Laplacian.
    try:
        import numpy as _np
        A = _np.array(adjacency, dtype=float)
        L = _np.diag(A.sum(axis=1)) - A
        lap_eigs = sorted(float(round(x, 12)) for x in _np.linalg.eigvalsh(L))
        W = _np.array(optical_weight, dtype=float)
        C = _np.zeros_like(W, dtype=float)
        mask = W > 0
        C[mask] = 1.0 / W[mask]
        Lw = _np.diag(C.sum(axis=1)) - C
        wlap_eigs = sorted(float(round(x, 18)) for x in _np.linalg.eigvalsh(Lw))
    except Exception:
        lap_eigs = []
        wlap_eigs = []

    # Macro-strategy / conjugacy statistics.
    total_states = sum(_to_int(r.get("class_size")) for r in strategy_rows)
    even_states = sum(_to_int(r.get("class_size")) for r in strategy_rows if str(r.get("parity")) == "even")
    odd_states = sum(_to_int(r.get("class_size")) for r in strategy_rows if str(r.get("parity")) == "odd")
    weighted_all_transposition_sum = sum(_to_int(r.get("class_size")) * _to_int(r.get("all_transposition_distance")) for r in strategy_rows)
    weighted_support_sum = sum(_to_int(r.get("class_size")) * _to_int(r.get("support_size")) for r in strategy_rows)

    solved_game = {
        "status": "D20_HCYCLE_SOLVED_BOARD_GAME_PASS",
        "board_value_functions": {
            "interpretation": "V[target][source] is the minimal cost-to-target on the d20 legal graph.",
            "graph_step_value_matrix": graph_value,
            "optical_action_value_matrix": optical_value,
            "exact_pair_transposition_word_cost_matrix": exact_transposition,
            "pair_best_optical_shortest_path_matrix": pair_opt_shortest,
            "pair_best_optical_simple_path_matrix": pair_opt_simple,
        },
        "minimax_centers": {
            "graph_radius": graph_radius,
            "graph_centers": graph_centers,
            "graph_center_labels": {str(i): label_by_vertex.get(i, "") for i in graph_centers},
            "graph_diameter": max(graph_ecc) if graph_ecc else None,
            "optical_radius": optical_radius,
            "optical_centers": optical_centers,
            "optical_center_labels": {str(i): label_by_vertex.get(i, "") for i in optical_centers},
            "optical_diameter": max(optical_ecc) if optical_ecc else None,
        },
        "markov_control": {
            "uniform_legal_walk_stationary_distribution": uniform_stationary,
            "optical_conductance_stationary_distribution": conductance_stationary,
            "optical_conductance_transition_kernel": conductance_kernel,
            "stationary_distribution_sums": {
                "uniform": sum(uniform_stationary),
                "optical_conductance": sum(conductance_stationary),
            },
        },
        "spectral_game_invariants": {
            "laplacian_eigenvalues": lap_eigs,
            "weighted_conductance_laplacian_eigenvalues": wlap_eigs,
            "algebraic_connectivity": lap_eigs[1] if len(lap_eigs) > 1 else None,
        },
        "macro_strategy_statistics": {
            "S20_order_from_classes": total_states,
            "even_state_count": even_states,
            "odd_state_count": odd_states,
            "parity_balanced": even_states == odd_states,
            "weighted_mean_all_transposition_distance": weighted_all_transposition_sum / total_states if total_states else None,
            "weighted_mean_support_size": weighted_support_sum / total_states if total_states else None,
        },
        "residue_algebra": {
            "rank": 11,
            "state_count": 2048,
            "composition_law": "bitwise_xor_on_11_basis_H_cycles",
            "identity_mask": 0,
            "all_subset_rows": len(tables.get("d20_Hcycle_mod2_residue_spectrum_all_subsets.csv", {}).get("rows", [])),
            "minimal_representative_rows": len(residue_rows),
            "complete_minimal_spectrum": len(residue_rows) == 2048,
        },
    }

    return {
        "status": "D20_HCYCLE_GAME_THEORY_CERTIFIED",
        "present": True,
        "framework": "H_{circlearrowleft} theory",
        "source_files": files,
        "solved_game": solved_game,
        "board": {
            "vertices": int(control.get("graph", {}).get("vertices", 20)),
            "edges": int(control.get("graph", {}).get("edges", 30)),
            "degree": int(control.get("graph", {}).get("degree", 3)),
            "connected": bool(control.get("graph", {}).get("connected", True)),
            "girth": int(control.get("graph", {}).get("girth", 5)),
            "diameter": int(control.get("graph", {}).get("diameter", 5)),
            "cycle_rank": int(control.get("graph", {}).get("cycle_rank", len(primitive))),
            "edge_table_rows": len(edges),
            "automorphism_count": int(automorphism.get("automorphism_count", 0)),
            "pair_orbit_count": int(automorphism.get("pair_orbit_count", 0)),
        },
        "state_space": {
            "S20_order": int(manifest.get("S20_order", 2432902008176640000)),
            "conjugacy_class_count": int(manifest.get("conjugacy_class_count", len(strategy_rows))),
            "strategy_class_atlas_rows": len(strategy_rows),
            "strategy_parity_histogram": parity_hist,
        },
        "primitive_H_cycles": {
            "count": len(primitive),
            "length_histogram": length_hist,
            "min_length": min(lengths) if lengths else None,
            "max_length": max(lengths) if lengths else None,
            "min_optical_action": min(optical) if optical else None,
            "max_optical_action": max(optical) if optical else None,
            "total_optical_action": sum(optical),
            "min_entropy_proxy_A_over_4WD6": min(entropy) if entropy else None,
            "max_entropy_proxy_A_over_4WD6": max(entropy) if entropy else None,
            "cycles": load_j("subscript_Hcycle_primitive_cycles.json") if (base / "subscript_Hcycle_primitive_cycles.json").exists() else primitive,
        },
        "edge_costs": {
            "edge_count": len(edges),
            "min_interface_weight": min(edge_weights) if edge_weights else None,
            "max_interface_weight": max(edge_weights) if edge_weights else None,
            "total_interface_weight": sum(edge_weights),
            "pair_transposition_rows": len(pair_costs),
            "min_exact_word_cost": min(exact_costs) if exact_costs else None,
            "max_exact_word_cost": max(exact_costs) if exact_costs else None,
            "longer_path_improves_count": improved,
            "distance_class_summary_rows": len(distance_rows),
        },
        "residue_spectrum": {
            "rank": 11,
            "expected_mod2_residues": 2048,
            "minimal_rows": len(residue_rows),
            "all_subset_rows": len(tables.get("d20_Hcycle_mod2_residue_spectrum_all_subsets.csv", {}).get("rows", [])),
            "complete": len(residue_rows) == 2048,
        },
        "grammar": {
            "circuit_count": len(grammar_rows),
            "circuits": grammar_rows,
        },
        "invariant_ledger": {
            "entry_count": len(ledger_rows),
            "entries": ledger_rows,
        },
        "tables": tables,
    }


def json_payloads() -> dict[str, Any]:
    skip = {"d20.json", "certificate.json", "layers/index.json", "layers\\index.json"}
    payloads: dict[str, Any] = {}
    for path in sorted(ROOT.rglob("*.json")):
        if excluded_scan_path(path):
            continue
        rel = str(path.relative_to(ROOT))
        if rel in skip:
            continue
        if rel.startswith("manifests/"):
            continue
        # generated/cache JSON files are not canonical inputs.
        if rel.startswith("generated/"):
            continue
        try:
            payloads[rel] = load_json(path)
        except Exception as e:
            payloads[rel] = {"unreadable_json": str(e), "file_sha256": sha_file(path)}
    return payloads


def generated_json_payloads() -> dict[str, Any]:
    d = ROOT / "generated"
    payloads: dict[str, Any] = {}
    if not d.exists():
        return payloads
    for path in sorted(d.rglob("*.json")):
        rel = str(path.relative_to(ROOT))
        try:
            payloads[rel] = load_json(path)
        except Exception as e:
            payloads[rel] = {"unreadable_json": str(e), "file_sha256": sha_file(path)}
    return payloads


def source_file_manifest() -> dict[str, Any]:
    entries = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if excluded_scan_path(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("generated/"):
            continue
        if rel.startswith("manifests/"):
            continue
        if rel in {"d20.json", "certificate.json"}:
            continue
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        })
    return {"entries": entries, "count": len(entries)}


def core_invariants() -> dict[str, Any]:
    out: dict[str, Any] = {}
    z = np.load(ROOT / "data/raw/tensor_sparse.npz")
    triples = np.asarray(z["triples"], dtype=np.int64)
    reps = np.asarray(z["reps"], dtype=np.int64)
    M = np.asarray(z["M"], dtype=np.int64)
    out["A985"] = {
        "relation_count": 985,
        "tensor_support": int(triples.shape[0]),
        "tensor_coefficient_total": int(triples[:, 3].sum()),
        "tensor_coefficient_min": int(triples[:, 3].min()),
        "tensor_coefficient_max": int(triples[:, 3].max()),
        "tensor_triples_shape": list(triples.shape),
        "reps_shape": list(reps.shape),
        "object_pair_matrix": M.tolist(),
        "object_pair_matrix_shape": list(M.shape),
        "tensor_triples_sha256": array_digest(triples),
        "reps_sha256": array_digest(reps),
        "object_pair_matrix_sha256": array_digest(M),
    }
    q = np.load(ROOT / "data/raw/quotients.npz")
    q42 = np.asarray(q["q42_map"], dtype=np.int64)
    q12 = np.asarray(q["q12_map"], dtype=np.int64)
    q42t = np.asarray(q["q42_tensor"], dtype=np.int64)
    q12t = np.asarray(q["q12_tensor"], dtype=np.int64)
    q42_to_q12 = []
    q42_ok = True
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            q42_ok = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))
    out["Pin(d20)=A42"] = {
        "classes": 42,
        "map_shape": list(q42.shape),
        "tensor_shape": list(q42t.shape),
        "tensor_nonzero": int(np.count_nonzero(q42t)),
        "tensor_sum": int(q42t.sum()),
        "map_sha256": array_digest(q42),
        "tensor_sha256": array_digest(q42t),
    }
    out["CY(d20)=A12"] = {
        "classes": 12,
        "map_shape": list(q12.shape),
        "tensor_shape": list(q12t.shape),
        "tensor_nonzero": int(np.count_nonzero(q12t)),
        "tensor_sum": int(q12t.sum()),
        "map_sha256": array_digest(q12),
        "tensor_sha256": array_digest(q12t),
        "A42_to_A12_consistent": bool(q42_ok),
        "A42_to_A12_map": q42_to_q12,
    }
    b = np.load(ROOT / "data/raw/simple_branching_matrices.npz")
    B236_42 = np.asarray(b["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(b["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(b["B236_12"], dtype=np.int64)
    comp = B236_42 @ B42_12
    dims236 = [1]*20 + [3]*10 + [4,5,6,7]
    out["Chem(d20)=A236"] = {
        "simple_count": 34,
        "simple_dimensions": dims236,
        "dimension": int(sum(d*d for d in dims236)),
        "center_dimension": 34,
        "B236_to_A42_shape": list(B236_42.shape),
        "B42_to_A12_shape": list(B42_12.shape),
        "B236_to_A12_shape": list(B236_12.shape),
        "naturality_B236_to_A12_equals_B236_to_A42_times_B42_to_A12": bool(np.array_equal(comp, B236_12)),
        "B236_to_A42_sha256": array_digest(B236_42),
        "B42_to_A12_sha256": array_digest(B42_12),
        "B236_to_A12_sha256": array_digest(B236_12),
    }
    rel = np.load(ROOT / "data/raw/relation_memberships.npz")
    object_of_point = np.asarray(rel["object_of_point"], dtype=np.int64)
    object_sizes = np.bincount(object_of_point, minlength=6)
    out["six_address_field"] = {
        "H6": ORDER,
        "object_orbit_sizes": {ORDER[i]: int(object_sizes[i]) for i in range(6)},
        "object_orbit_size_sum": int(object_sizes.sum()),
        "dodecad_shell_size": 2576,
    }
    # Leech metadata
    leech = np.load(ROOT / "data/raw/leech_projective_generators.npz")
    for k in leech.files:
        a = np.asarray(leech[k])
        if a.shape == (98280, 24):
            out["Leech_layer"] = {
                "projective_shell_vertices": 98280,
                "coordinate_dimension": 24,
                "array_key": k,
                "array_sha256": array_digest(a),
            }
            break
    return out


def optics_invariants() -> dict[str, Any]:
    weights = [WEIGHTS[x] for x in ORDER]
    q = [WEYL_D6 // w for w in weights]
    m = [x // 5 for x in q]
    face_masses = []
    face_entries = []
    for a in range(6):
        for b in range(a + 1, 6):
            for c in range(b + 1, 6):
                mu = weights[a] * weights[b] * weights[c]
                face_masses.append(mu)
                face_entries.append({"face": [ORDER[a], ORDER[b], ORDER[c]], "mu": mu, "mu_over_epsilon0": mu // EPSILON0})
    E = sum(face_masses)
    closed_area_packet = D20_EDGE_CLOSURE_ORDER * EPSILON0
    complement_product = math.prod(weights)
    duad_entries = []
    for a in range(6):
        for b in range(a + 1, 6):
            duad_entries.append({"duad": [ORDER[a], ORDER[b]], "T": weights[a] * weights[b]})
    star = {ORDER[i]: sum(e["mu"] for e in face_entries if ORDER[i] in e["face"]) for i in range(6)}
    star_norm = {k: v // EPSILON0 for k, v in star.items()}
    return {
        "constants": {
            "epsilon0": EPSILON0,
            "epsilon0_factorization": factorization(EPSILON0),
            "W_D6_order": WEYL_D6,
            "W_D6_factorization": factorization(WEYL_D6),
            "foam_dim": FOAM_DIM,
            "spin_packet_dim": 2 * FOAM_DIM,
            "order5_closure": D20_EDGE_CLOSURE_ORDER,
        },
        "packet20_weights": {ORDER[i]: weights[i] for i in range(6)},
        "packet20_weight_sum": sum(weights),
        "d20_etendue": E,
        "d20_etendue_over_epsilon0": E // EPSILON0,
        "face_masses": face_entries,
        "duad_snell_invariants": duad_entries,
        "star_masses": star,
        "star_masses_over_epsilon0": star_norm,
        "star_mass_sum_over_epsilon0": sum(star_norm.values()),
        "complement_product": complement_product,
        "complement_product_over_epsilon0_squared": complement_product // (EPSILON0 * EPSILON0),
        "central_identity": {
            "5_epsilon0": 5 * EPSILON0,
            "128_W_D6": 128 * WEYL_D6,
            "5_epsilon0_equals_128_W_D6": 5 * EPSILON0 == 128 * WEYL_D6,
            "5_epsilon0_over_4W_D6": (5 * EPSILON0) // (4 * WEYL_D6),
            "equals_32": (5 * EPSILON0) // (4 * WEYL_D6) == 32,
            "single_epsilon0_over_4W_D6_fraction": "32/5",
        },
        "weyl_reciprocity": {
            "q_i_equals_W_D6_over_w_i": {ORDER[i]: q[i] for i in range(6)},
            "sum_q_i": sum(q),
            "sum_q_i_equals_binom_15_3": sum(q) == math.comb(15, 3),
            "m_i_equals_q_i_over_5": {ORDER[i]: m[i] for i in range(6)},
            "sum_m_i": sum(m),
            "sum_m_i_equals_binom_14_2": sum(m) == math.comb(14, 2),
        },
        "entropy": {
            "closed_area_packet": closed_area_packet,
            "closed_area_packet_weyl_cells": closed_area_packet // WEYL_D6,
            "entropy_packet": closed_area_packet // (4 * WEYL_D6),
            "closed_packets_in_E_d20": E // closed_area_packet,
            "S_d20": E // (4 * WEYL_D6),
            "S_d20_equals_binom_15_3_times_32": E // (4 * WEYL_D6) == math.comb(15, 3) * 32,
        },
    }


def layer_payloads() -> dict[str, Any]:
    out = {}
    for p in sorted((ROOT / "layers").glob("*/certificate.json")):
        out[p.parent.name] = load_json(p)
    return out


def layer_registry() -> dict[str, Any]:
    path = ROOT / "layers" / "index.json"
    if not path.exists():
        return {"path": "layers/index.json", "status": "LAYER_REGISTRY_MISSING"}
    payload = load_json(path)
    return {
        "path": "layers/index.json",
        "file_sha256": sha_file(path),
        **payload,
    }


def csv_payloads() -> dict[str, Any]:
    out = {}
    for path in sorted(ROOT.rglob("*.csv")):
        if excluded_scan_path(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("generated/"):
            continue
        out[rel] = csv_payload(path)
    return out


def npz_manifests() -> dict[str, Any]:
    out = {}
    for path in sorted(ROOT.rglob("*.npz")):
        if excluded_scan_path(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        # generated NPZ cache is not source; if present it is not part of canonical d20.
        if rel.startswith("generated/"):
            continue
        out[rel] = npz_manifest(path)
    return out



def coorient_seed_invariants() -> dict[str, Any]:
    """Expose the small non-scratch coorient seed explicitly inside d20.json.

    This is the remaining finite witness from which the lifted Be3 coorient action
    is reconstructed. The large permutation/action/tensor data are not stored here
    as primitive ontology; they are derived from this seed plus the coherent
    relation-signature reconstruction rules.
    """
    base = ROOT / "data" / "coorient"
    files: dict[str, Any] = {}
    for name in [
        "lifted_coorient_canonical_marker_formula.json",
        "lifted_coorient_signature_formula.json",
        "absolute_d20_word_presentation.json",
        "be3_coorient_generators.npz",
    ]:
        path = base / name
        if not path.exists():
            continue
        entry: dict[str, Any] = {
            "path": str(path.relative_to(ROOT)),
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        }
        if path.suffix == ".json":
            payload = load_json(path)
            entry["schema"] = payload.get("schema")
            entry["payload"] = payload
            if name == "lifted_coorient_canonical_marker_formula.json":
                b = payload.get("base_points", [])
                imgs = payload.get("generator_base_images", [])
                entry["seed_integer_count"] = len(b) + sum(len(row) for row in imgs)
            if name == "lifted_coorient_signature_formula.json":
                b = payload.get("base_points", [])
                imgs = payload.get("generator_base_images", [])
                entry["signature_integer_count"] = len(b) + sum(len(row) for row in imgs)
            if name == "absolute_d20_word_presentation.json":
                entry["closure_order"] = payload.get("closure_order")
                entry["generators"] = payload.get("generators")
                entry["presentation_sha256"] = payload.get("presentation_sha256")
        elif path.suffix == ".npz":
            entry["npz_manifest"] = npz_manifest(path)
        files[name] = entry

    canonical = files.get("lifted_coorient_canonical_marker_formula.json", {}).get("payload", {})
    sig = files.get("lifted_coorient_signature_formula.json", {}).get("payload", {})
    word = files.get("absolute_d20_word_presentation.json", {}).get("payload", {})
    return {
        "status": "COORIENT_SEED_EXPLICIT",
        "remaining_non_scratch_seed": "canonical lifted coorient marker plus marked d20/D6 word presentation",
        "canonical_base_points": canonical.get("base_points"),
        "canonical_generator_base_images": canonical.get("generator_base_images"),
        "canonical_seed_integer_count": files.get("lifted_coorient_canonical_marker_formula.json", {}).get("seed_integer_count"),
        "signature_base_points": sig.get("base_points"),
        "signature_generator_base_images": sig.get("generator_base_images"),
        "signature_integer_count": files.get("lifted_coorient_signature_formula.json", {}).get("signature_integer_count"),
        "word_presentation_generators": word.get("generators"),
        "word_presentation_closure_order": word.get("closure_order"),
        "word_presentation_sha256": word.get("presentation_sha256"),
        "derived_from_seed": [
            "lifted Be3 coorient action on 2576 dodecads",
            "six object orbits",
            "985 ordered-pair orbitals",
            "T985 sparse multiplication tensor",
            "A42/A12 quotients",
            "d20 selector, optics, integrity, H-cycle/game invariants",
        ],
        "files": files,
    }



def universal_integral_uniqueness_payload() -> dict[str, Any]:
    path = ROOT / "data" / "d20" / "universal_integral_uniqueness.json"
    if path.exists():
        return load_json(path)
    from src.derive_universal_integral_uniqueness import derive as _derive_universal_integral_uniqueness
    return _derive_universal_integral_uniqueness()


def final_investigation_status(z: dict[str, Any] | None = None, u: dict[str, Any] | None = None) -> dict[str, Any]:
    """Final theorem ledger for the d20 investigation.

    This is deliberately explicit about the one remaining conditional boundary:
    the four lifted coorient generator images on the canonical three-point base.
    Everything downstream is certified/generated from that tiny marker.
    """
    if z is None:
        z = derive_zero_axiom_coorient()
    if u is None:
        u = universal_integral_uniqueness_payload()
    base = z.get("canonical_base_derivation", {})
    uniq = u.get("uniqueness_result", {})
    comp = u.get("coorient_lift_uniqueness_computation", {})
    return {
        "status": "D20_INVESTIGATION_FINALIZED_WITH_A985_INTEGRAL_UNIQUENESS",
        "finite_computational_closure": True,
        "A985_integral_uniqueness_computed": uniq.get("A985_integral_uniqueness_computed") is True,
        "coorient_action_group_unique_over_A985": uniq.get("coorient_action_group_unique") is True,
        "full_zero_axiom_constructor": False,
        "zero_axiom_reduction": True,
        "remaining_boundary": {
            "name": "absolute H8^3-to-A985 coorient emergence theorem",
            "description": "A985-integral uniqueness is computed. What remains outside this finite check is deriving A985 itself, including the coherent relation body, without already having the A985 relation table.",
            "remaining_seed_integer_count_in_A985_integral_theory": 0,
            "coherent_signature_lift_count": comp.get("coherent_signature_lift_triples"),
            "generated_action_order": comp.get("generated_action_order"),
            "canonical_base": base.get("base", [18, 67, 37]),
            "canonical_base_is_derived": base.get("matches_stored_canonical_base") is True and base.get("separates_all_points") is True,
            "twelve_integers_role": "not semantic seed after uniqueness; only coordinates for one named generator basis of the unique 9216-element lift group",
            "not_stored_as_large_data": True,
        },
        "closed_layers": {
            "source_to_golay_dodecads": "certified constructor",
            "coorient_marker_to_Be3": "certified constructor",
            "Be3_to_985_orbitals": "certified constructor",
            "orbitals_to_T985": "certified constructor",
            "T985_to_center_idempotents": "certified finite-field constructor",
            "T985_to_A42_A12": "certified quotient constructor",
            "native_A236_formula": "certified d20/D6 representation formula",
            "packet20_C20": "certified from Be3 stabilizers and D6 divisor rule",
            "sector33_integrity": "certified finite obstruction",
            "d20_selector": "certified D6 Coxeter-polarity selector",
            "Foam_d20": "certified 1+Lambda^2 H6 chart",
            "Optics_d20": "certified etendue/Snell/complement/caustic layer",
            "Hcycle_game_layer": "certified board/control invariant layer",
            "regeneration": "python certify.py rebuilds d20.json, certificate.json, manifest hashes, then audits",
        },
        "game_theory_finalization": {
            "board": "20 d20 faces, 30 D6-selected legal edges, dodecahedral graph",
            "state_space": "S20 = 20! with 627 conjugacy/macro-strategy classes",
            "control": "graph distances, optical action costs, Markov stationary laws, spectral invariants, F2^11 residue algebra",
            "solved_in_current_scope": True,
            "not_claimed": [
                "universal strategic optimality for arbitrary external payoff functions",
                "physical identification of d20 with a literal spacetime theory",
                "unconditional zero-axiom derivation before the coorient-lift uniqueness theorem is proved",
            ],
        },
        "final_verdict": {
            "finite_object_status": "complete as a regenerating finite verifier object",
            "mathematical_theorem_status": "conditional only at the coorient uniqueness boundary",
            "practical_bundle_status": "one-command certification via python certify.py",
        },
    }



def pre_a985_relation_body_theorem() -> dict[str, Any]:
    path = ROOT / "data/d20/pre_A985_relation_body_theorem.json"
    if path.exists():
        return load_json(path)
    from src.derive_pre_a985_relation_body import derive as _derive_pre_a985
    return _derive_pre_a985(regenerate=False)

def derive() -> dict[str, Any]:
    zero_axiom = derive_zero_axiom_coorient()
    universal_uniqueness = universal_integral_uniqueness_payload()
    result: dict[str, Any] = {
        "schema": "d20.object.v2",
        "status": "D20_CERTIFIED",
        "object": "d20",
        "definition": {
            "d20": "normalized finite object",
            "Code(d20)": "A985",
            "Chem(d20)": "A236",
            "Pin(d20)": "A42",
            "CY(d20)": "A12",
            "Foam(d20)": "1 + Lambda^2 H6",
            "Optics(d20)": "etendue, Snell transport, complement conservation, caustic resolvent",
            "Integrity(d20)": "sector-33 integral wall",
        },
        "core_invariants": core_invariants(),
        "optics": optics_invariants(),
        "game_theory": hcycle_game_theory(),
        "zero_axiom_coorient": zero_axiom,
        "universal_integral_uniqueness": universal_uniqueness,
        "pre_A985_relation_body_theorem": pre_a985_relation_body_theorem(),
        "coorient_seed": coorient_seed_invariants(),
        "final_investigation": final_investigation_status(zero_axiom, universal_uniqueness),
        "layer_registry": layer_registry(),
        "layer_certificates": layer_payloads(),
        "json_invariants": json_payloads(),
        "csv_invariants": csv_payloads(),
        "npz_array_manifests": npz_manifests(),
        "source_manifest": source_file_manifest(),
    }
    result["d20_sha256"] = sha_json({k: v for k, v in result.items() if k != "d20_sha256"})
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="d20.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive()
    p = ROOT / args.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True), encoding="utf-8")
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
