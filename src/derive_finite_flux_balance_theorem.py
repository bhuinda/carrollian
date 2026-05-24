from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "finite_flux_balance"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
RESIDUE_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
CHANNEL_WEIGHTS = {
    "B-": 384,
    "B+": 192,
    "V-": 144,
    "V+": 576,
    "S-": 512,
    "S+": 768,
}
FAMILY_AXIS = {
    "B": -1,
    "V": 0,
    "S": 1,
}


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_label(label: str) -> tuple[str, ...]:
    body = label.strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise ValueError(f"bad D20 label: {label!r}")
    order = {name: i for i, name in enumerate(H6_LABELS)}
    parts = tuple(part.strip() for part in body[1:-1].split(",") if part.strip())
    return tuple(sorted(parts, key=order.__getitem__))


def label_text(parts: tuple[str, ...]) -> str:
    return "{" + ",".join(parts) + "}"


def channel_charge(label: str) -> dict[str, int]:
    family = label[0]
    sign = 1 if label.endswith("+") else -1
    weight = CHANNEL_WEIGHTS[label]
    axis = FAMILY_AXIS[family]
    return {
        "M": weight,
        "J": sign * weight,
        "P": axis * weight,
        "Phi": sign * axis * weight,
    }


def add_charge(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {key: a.get(key, 0) + b.get(key, 0) for key in ("M", "J", "P", "Phi")}


def sub_charge(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {key: a[key] - b[key] for key in ("M", "J", "P", "Phi")}


def zero_charge() -> dict[str, int]:
    return {"M": 0, "J": 0, "P": 0, "Phi": 0}


def d20_charge(parts: tuple[str, ...]) -> dict[str, int]:
    out = zero_charge()
    for part in parts:
        out = add_charge(out, channel_charge(part))
    return out


def load_graph() -> tuple[dict[int, tuple[str, ...]], list[dict[str, Any]], dict[tuple[int, int], int]]:
    vertices: dict[int, tuple[str, ...]] = {}
    edges: list[dict[str, Any]] = []
    edge_ids: dict[tuple[int, int], int] = {}
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            u = int(row["u"])
            v = int(row["v"])
            u_label = parse_label(row["u_label"])
            v_label = parse_label(row["v_label"])
            vertices.setdefault(u, u_label)
            vertices.setdefault(v, v_label)
            edge = {
                "edge_id": int(row["edge_id"]),
                "u": u,
                "v": v,
                "u_label": label_text(u_label),
                "v_label": label_text(v_label),
                "interface_weight": int(row["interface_weight"]),
            }
            edges.append(edge)
            edge_ids[tuple(sorted((u, v)))] = edge["edge_id"]
    return vertices, edges, edge_ids


def load_primitive_cycles() -> list[dict[str, Any]]:
    cycles: list[dict[str, Any]] = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            vertices = [int(value) for value in row["vertices"].split()]
            edge_ids = [int(value) for value in row["edge_ids"].split()]
            cycles.append(
                {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "vertices": vertices,
                    "edge_ids": edge_ids,
                    "optical_action": int(row["optical_action"]),
                    "entropy_proxy_A_over_4WD6": row["entropy_proxy_A_over_4WD6"],
                }
            )
    return cycles


def load_residue_spectrum() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with RESIDUE_SPECTRUM_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "mask": int(row["mask"]),
                    "basis_cycle_ids": [int(value) for value in row["basis_cycle_ids"].split()] if row["basis_cycle_ids"] else [],
                    "incidence_vector_mod2": row["incidence_vector_mod2"].strip(),
                }
            )
    return rows


def cycle_flux(vertices: dict[int, tuple[str, ...]], cycle_vertices: list[int]) -> dict[str, Any]:
    flux = zero_charge()
    steps: list[dict[str, Any]] = []
    for u, v in zip(cycle_vertices, cycle_vertices[1:]):
        delta = sub_charge(d20_charge(vertices[v]), d20_charge(vertices[u]))
        flux = add_charge(flux, delta)
        steps.append({"u": u, "v": v, "flux": delta})
    q_in = d20_charge(vertices[cycle_vertices[0]])
    q_out = d20_charge(vertices[cycle_vertices[-1]])
    residual = sub_charge(sub_charge(q_out, q_in), flux)
    return {
        "q_in": q_in,
        "q_out": q_out,
        "flux": flux,
        "residual": residual,
        "steps": steps,
    }


def even_boundary_for_incidence(incidence: str, edges: list[dict[str, Any]]) -> bool:
    parity: dict[int, int] = defaultdict(int)
    for bit, edge in zip(incidence, edges):
        if bit == "1":
            parity[edge["u"]] ^= 1
            parity[edge["v"]] ^= 1
        elif bit != "0":
            raise ValueError(f"bad incidence bit: {bit!r}")
    return all(value == 0 for value in parity.values())


def build_theorem() -> dict[str, Any]:
    vertices, edges, edge_ids = load_graph()
    charges = {vertex: d20_charge(parts) for vertex, parts in vertices.items()}
    expected_triples = {tuple(H6_LABELS[i] for i in combo) for combo in combinations(range(6), 3)}
    primitive_cycles = load_primitive_cycles()
    residue_rows = load_residue_spectrum()
    edge_count = len(edges)
    vertex_count = len(vertices)
    cycle_rank = edge_count - vertex_count + 1

    primitive_balance = []
    for cycle in primitive_cycles:
        balance = cycle_flux(vertices, cycle["vertices"])
        primitive_balance.append(
            {
                "cycle_id": cycle["cycle_id"],
                "length": cycle["length"],
                "vertices": cycle["vertices"],
                "edge_ids": cycle["edge_ids"],
                "optical_action": cycle["optical_action"],
                "entropy_proxy_A_over_4WD6": cycle["entropy_proxy_A_over_4WD6"],
                "q_in": balance["q_in"],
                "q_out": balance["q_out"],
                "flux_D20": balance["flux"],
                "res_A985": balance["residual"],
                "residual_zero": balance["residual"] == zero_charge(),
            }
        )

    residue_incidence_lengths = {len(row["incidence_vector_mod2"]) for row in residue_rows}
    residue_masks = sorted(row["mask"] for row in residue_rows)
    all_residue_vectors_are_cycles = all(
        even_boundary_for_incidence(row["incidence_vector_mod2"], edges)
        for row in residue_rows
    )

    checks = {
        "edge_table_exists": EDGE_CSV.exists(),
        "primitive_cycle_table_exists": PRIMITIVE_CYCLES_CSV.exists(),
        "residue_spectrum_exists": RESIDUE_SPECTRUM_CSV.exists(),
        "d20_state_count_is_20": vertex_count == 20,
        "d20_states_are_all_lambda3_h6": set(vertices.values()) == expected_triples,
        "edge_count_is_30": edge_count == 30,
        "cycle_rank_is_11": cycle_rank == 11,
        "primitive_cycle_count_is_11": len(primitive_cycles) == 11,
        "primitive_cycles_are_closed": all(cycle["vertices"][0] == cycle["vertices"][-1] for cycle in primitive_cycles),
        "primitive_flux_residuals_zero": all(row["residual_zero"] for row in primitive_balance),
        "residue_class_count_is_2_power_11": len(residue_rows) == 2**cycle_rank,
        "residue_masks_are_complete": residue_masks == list(range(2**cycle_rank)),
        "residue_incidence_vectors_have_30_edges": residue_incidence_lengths == {30},
        "all_residue_vectors_are_cycles": all_residue_vectors_are_cycles,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_EXACT_FLUX_BALANCE_NEEDS_REVIEW"
    )
    charge_basis = {
        "definition": "Q_boundary(state) is the sum of four finite channel probes over the three labels in the D20 state.",
        "components": {
            "M": "sum of channel weights",
            "J": "signed channel-weight sum, plus labels positive and minus labels negative",
            "P": "family-axis channel-weight sum, B=-1, V=0, S=1",
            "Phi": "signed family-axis channel-weight sum",
        },
        "channel_contributions": {
            label: channel_charge(label)
            for label in H6_LABELS
        },
        "state_charges": {
            str(vertex): {
                "state": label_text(vertices[vertex]),
                "Q_boundary": charges[vertex],
            }
            for vertex in sorted(vertices)
        },
    }
    exact_flux_condition = {
        "name": "exact_boundary_flux_coherence",
        "condition": (
            "there exists a globally assigned finite charge Q_boundary on D20 "
            "such that every oriented boundary edge u->v has Flux_D20(u,v)=Q_boundary(v)-Q_boundary(u)"
        ),
        "consequence": (
            "Flux_D20 is a coboundary, so its pairing with every closed H-cycle "
            "and every mod-2 residue cycle is zero; the A985 residual term is therefore zero in this exact sector"
        ),
    }
    report = {
        "schema": "d20.theorem.finite_flux_balance.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "For the D20 H-cycle boundary graph, exact boundary flux satisfies "
            "Q_boundary_out-Q_boundary_in=Flux_D20(gamma)+Res_A985(gamma) with Res_A985(gamma)=0 "
            "on every closed return generated by the certified cycle space."
        ),
        "inputs": {
            "hcycle_edge_table": {"path": rel(EDGE_CSV), "sha256": sha_file(EDGE_CSV)},
            "primitive_cycle_table": {"path": rel(PRIMITIVE_CYCLES_CSV), "sha256": sha_file(PRIMITIVE_CYCLES_CSV)},
            "residue_spectrum": {"path": rel(RESIDUE_SPECTRUM_CSV), "sha256": sha_file(RESIDUE_SPECTRUM_CSV)},
        },
        "definitions": {
            "boundary_charge": charge_basis,
            "exact_flux_coherence": exact_flux_condition,
            "balance_law": "Q_boundary_out - Q_boundary_in = Flux_D20(gamma) + Res_A985(gamma)",
        },
        "derived": {
            "graph_counts": {
                "vertices": vertex_count,
                "edges": edge_count,
                "cycle_rank": cycle_rank,
                "residue_class_count": len(residue_rows),
            },
            "primitive_cycle_balances": primitive_balance,
            "cycle_space": {
                "mod2_residue_vectors_checked": len(residue_rows),
                "all_residue_vectors_are_cycles": all_residue_vectors_are_cycles,
                "proof": "For exact Flux=B^T Q and every closed residue z with Bz=0, <Flux,z>=<Q,Bz>=0.",
            },
        },
        "checks": checks,
        "theorem": {
            "statement": (
                "Under exact_boundary_flux_coherence, the D20 boundary charge update "
                "around each certified closed H-cycle is zero, and the hidden A985 residual term vanishes."
            ),
            "scope": (
                "This certifies the exact/coboundary flux sector. It does not assert "
                "that the positive optical action weights are exact fluxes, nor that general BMS flux balance is complete."
            ),
            "not_claimed": [
                "arbitrary optical action cycles have zero action",
                "all A985 hidden-sector residues vanish outside the exact boundary-flux sector",
                "continuum BMS balance has been recovered",
            ],
        },
        "next_highest_yield_item": (
            "Attach non-exact optical/action flux to the same cycle-space ledger and isolate "
            "the first cycle classes where Res_A985(gamma) must be nonzero."
        ),
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
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
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_flux_balance_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "derive a finite four-component boundary charge on every Lambda^3 H6 state",
            "type every primitive H-cycle by exact D20 flux plus A985 residual",
            "verify all primitive closed returns have zero exact residual",
            "verify the 2048 mod-2 residue vectors are closed cycle-space elements",
            "prove exact flux pairs trivially with the whole closed cycle space",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
