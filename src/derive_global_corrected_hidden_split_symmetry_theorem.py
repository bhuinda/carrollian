from __future__ import annotations

import csv
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "global_corrected_hidden_split_symmetry"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

GLOBAL_CORRECTED_CHARGE_MAP_REPORT = (
    D20_INVARIANTS / "theorems" / "global_corrected_charge_map" / "report.json"
)
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
RESIDUE_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
AUTOMORPHISM_SUMMARY = HCYCLE_INVARIANTS / "d20_Hcycle_automorphism_summary.json"

VERTEX_COUNT = 20
EDGE_COUNT = 30
RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
GAMMA8_MASK = 256


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def load_edges() -> tuple[list[dict[str, Any]], dict[tuple[int, int], int]]:
    edges: list[dict[str, Any]] = []
    edge_ids: dict[tuple[int, int], int] = {}
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edge = {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": row["u_label"],
                "v_label": row["v_label"],
            }
            edges.append(edge)
            edge_ids[tuple(sorted((edge["u"], edge["v"])))] = edge["edge_id"]
    edges = sorted(edges, key=lambda item: item["edge_id"])
    return edges, edge_ids


def graph_matrices(edges: list[dict[str, Any]]) -> tuple[list[list[bool]], list[set[int]], list[list[int]]]:
    adjacency = [[False] * VERTEX_COUNT for _ in range(VERTEX_COUNT)]
    for edge in edges:
        adjacency[edge["u"]][edge["v"]] = True
        adjacency[edge["v"]][edge["u"]] = True
    neighbors = [
        {candidate for candidate in range(VERTEX_COUNT) if adjacency[vertex][candidate]}
        for vertex in range(VERTEX_COUNT)
    ]
    distances: list[list[int]] = []
    for start in range(VERTEX_COUNT):
        row = [VERTEX_COUNT + 1] * VERTEX_COUNT
        row[start] = 0
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for target in neighbors[vertex]:
                if row[target] == VERTEX_COUNT + 1:
                    row[target] = row[vertex] + 1
                    queue.append(target)
        distances.append(row)
    return adjacency, neighbors, distances


def enumerate_automorphisms(
    adjacency: list[list[bool]],
    distances: list[list[int]],
) -> list[tuple[int, ...]]:
    automorphisms: list[tuple[int, ...]] = []

    def recurse(mapping: dict[int, int], used: set[int]) -> None:
        if len(mapping) == VERTEX_COUNT:
            automorphisms.append(tuple(mapping[idx] for idx in range(VERTEX_COUNT)))
            return

        best_vertex: int | None = None
        best_candidates: list[int] | None = None
        for source in range(VERTEX_COUNT):
            if source in mapping:
                continue
            candidates = []
            for target in range(VERTEX_COUNT):
                if target in used:
                    continue
                if all(
                    adjacency[source][known_source] == adjacency[target][known_target]
                    and distances[source][known_source] == distances[target][known_target]
                    for known_source, known_target in mapping.items()
                ):
                    candidates.append(target)
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_vertex = source
                best_candidates = candidates
            if best_candidates == []:
                break

        if best_vertex is None or not best_candidates:
            return

        for target in best_candidates:
            mapping[best_vertex] = target
            used.add(target)
            recurse(mapping, used)
            used.remove(target)
            del mapping[best_vertex]

    for root_image in range(VERTEX_COUNT):
        recurse({0: root_image}, {root_image})
    return sorted(set(automorphisms))


def load_residue_maps() -> tuple[dict[int, str], dict[str, int]]:
    mask_to_incidence: dict[int, str] = {}
    incidence_to_mask: dict[str, int] = {}
    with RESIDUE_SPECTRUM_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mask = int(row["mask"])
            incidence = row["incidence_vector_mod2"].strip()
            mask_to_incidence[mask] = incidence
            incidence_to_mask[incidence] = mask
    return mask_to_incidence, incidence_to_mask


def edge_permutation(
    vertex_permutation: tuple[int, ...],
    edges: list[dict[str, Any]],
    edge_ids: dict[tuple[int, int], int],
) -> list[int]:
    out: list[int] = []
    for edge in edges:
        image = tuple(sorted((vertex_permutation[edge["u"]], vertex_permutation[edge["v"]])))
        out.append(edge_ids[image])
    return out


def apply_edge_permutation_to_incidence(incidence: str, edge_perm: list[int]) -> str:
    bits = ["0"] * EDGE_COUNT
    for old_edge_id, bit in enumerate(incidence):
        if bit == "1":
            bits[edge_perm[old_edge_id]] = "1"
        elif bit != "0":
            raise ValueError(f"bad incidence bit: {bit!r}")
    return "".join(bits)


def induced_basis_images(
    edge_perm: list[int],
    mask_to_incidence: dict[int, str],
    incidence_to_mask: dict[str, int],
) -> list[int]:
    images = []
    for coord in range(RESIDUE_RANK):
        source_mask = 1 << coord
        image_incidence = apply_edge_permutation_to_incidence(
            mask_to_incidence[source_mask],
            edge_perm,
        )
        images.append(incidence_to_mask[image_incidence])
    return images


def hidden_parity(mask: int, coefficients: list[int]) -> int:
    return sum(coefficients[idx] for idx in bit_indices(mask) if coefficients[idx]) % 2


def preserves_hidden_split(basis_images: list[int], coefficients: list[int]) -> bool:
    return all(
        hidden_parity(image, coefficients) == coefficients[idx]
        for idx, image in enumerate(basis_images)
    )


def cycle_notation(permutation: list[int] | tuple[int, ...], include_fixed: bool = False) -> list[list[int]]:
    seen: set[int] = set()
    cycles: list[list[int]] = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        cycle = []
        cursor = start
        while cursor not in seen:
            seen.add(cursor)
            cycle.append(cursor)
            cursor = int(permutation[cursor])
        if include_fixed or len(cycle) > 1:
            cycles.append(cycle)
    return cycles


def orbits_from_permutations(permutations: list[list[int] | tuple[int, ...]], size: int) -> list[list[int]]:
    seen: set[int] = set()
    orbits: list[list[int]] = []
    for item in range(size):
        if item in seen:
            continue
        orbit = sorted({int(permutation[item]) for permutation in permutations})
        seen.update(orbit)
        orbits.append(orbit)
    return orbits


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[idx]] for idx in range(len(right)))


def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(permutation)
    for source, target in enumerate(permutation):
        out[target] = source
    return tuple(out)


def first_breaking_witness(
    basis_images: list[int],
    coefficients: list[int],
) -> dict[str, Any] | None:
    for idx, image in enumerate(basis_images):
        source_value = coefficients[idx]
        image_value = hidden_parity(image, coefficients)
        if source_value != image_value:
            return {
                "basis_coordinate": idx,
                "source_mask": 1 << idx,
                "source_hidden_z2": source_value,
                "image_mask": image,
                "image_basis_cycle_indices": bit_indices(image),
                "image_hidden_z2": image_value,
            }
    return None


def build_theorem() -> dict[str, Any]:
    charge_map = load_json(GLOBAL_CORRECTED_CHARGE_MAP_REPORT)
    automorphism_summary = load_json(AUTOMORPHISM_SUMMARY)
    edges, edge_ids = load_edges()
    adjacency, neighbors, distances = graph_matrices(edges)
    automorphisms = enumerate_automorphisms(adjacency, distances)
    mask_to_incidence, incidence_to_mask = load_residue_maps()

    coefficients = [
        int(value)
        for value in charge_map["derived"]["global_corrected_hidden_charge"][
            "coefficient_vector_over_f2"
        ]
    ]
    automorphism_records = []
    preserving_records = []
    breaking_records = []
    for idx, vertex_perm in enumerate(automorphisms):
        e_perm = edge_permutation(vertex_perm, edges, edge_ids)
        basis_images = induced_basis_images(e_perm, mask_to_incidence, incidence_to_mask)
        basis_image_hidden_values = [hidden_parity(mask, coefficients) for mask in basis_images]
        record = {
            "automorphism_id": idx,
            "vertex_permutation": list(vertex_perm),
            "edge_permutation": e_perm,
            "basis_image_masks": basis_images,
            "basis_image_hidden_z2": basis_image_hidden_values,
            "preserves_hidden_split": preserves_hidden_split(basis_images, coefficients),
        }
        automorphism_records.append(record)
        if record["preserves_hidden_split"]:
            preserving_records.append(
                {
                    **record,
                    "vertex_cycle_notation": cycle_notation(vertex_perm),
                    "edge_cycle_notation": cycle_notation(e_perm),
                }
            )
        else:
            witness = first_breaking_witness(basis_images, coefficients)
            if len(breaking_records) < 12:
                breaking_records.append(
                    {
                        "automorphism_id": idx,
                        "vertex_cycle_notation": cycle_notation(vertex_perm),
                        "first_breaking_witness": witness,
                    }
                )

    preserving_vertex_perms = [
        tuple(record["vertex_permutation"]) for record in preserving_records
    ]
    preserving_edge_perms = [
        record["edge_permutation"] for record in preserving_records
    ]
    preserving_set = set(preserving_vertex_perms)
    subgroup_closed = all(
        compose(left, right) in preserving_set
        for left in preserving_vertex_perms
        for right in preserving_vertex_perms
    )
    subgroup_has_inverses = all(inverse(perm) in preserving_set for perm in preserving_vertex_perms)
    nonidentity_preservers = [
        tuple(record["vertex_permutation"])
        for record in preserving_records
        if tuple(record["vertex_permutation"]) != tuple(range(VERTEX_COUNT))
    ]
    nonidentity_involutive = all(compose(perm, perm) == tuple(range(VERTEX_COUNT)) for perm in nonidentity_preservers)
    gamma8_images = []
    for record in preserving_records:
        image_incidence = apply_edge_permutation_to_incidence(
            mask_to_incidence[GAMMA8_MASK],
            record["edge_permutation"],
        )
        gamma8_images.append(incidence_to_mask[image_incidence])

    checks = {
        "edge_table_exists": EDGE_CSV.exists(),
        "residue_spectrum_exists": RESIDUE_SPECTRUM_CSV.exists(),
        "automorphism_summary_exists": AUTOMORPHISM_SUMMARY.exists(),
        "global_corrected_charge_map_is_certified": charge_map.get("status")
        == "D20_GLOBAL_CORRECTED_CHARGE_MAP_CERTIFIED"
        and charge_map.get("all_checks_pass") is True,
        "graph_has_20_vertices_and_30_edges": len(neighbors) == VERTEX_COUNT
        and len(edges) == EDGE_COUNT,
        "graph_is_cubic": sorted(len(row) for row in neighbors) == [3] * VERTEX_COUNT,
        "residue_spectrum_has_2048_masks": len(mask_to_incidence) == MASK_COUNT
        and set(mask_to_incidence) == set(range(MASK_COUNT)),
        "enumerated_automorphism_count_matches_summary": len(automorphisms)
        == int(automorphism_summary["automorphism_count"])
        == 120,
        "every_automorphism_acts_on_cycle_space": all(
            len(record["basis_image_masks"]) == RESIDUE_RANK for record in automorphism_records
        ),
        "hidden_split_stabilizer_has_order_2": len(preserving_records) == 2,
        "hidden_split_breaks_118_public_graph_symmetries": len(automorphism_records)
        - len(preserving_records)
        == 118,
        "preservers_form_subgroup": subgroup_closed and subgroup_has_inverses,
        "nonidentity_preserver_is_involution": len(nonidentity_preservers) == 1
        and nonidentity_involutive,
        "gamma8_mask_is_fixed_by_hidden_split_stabilizer": gamma8_images == [GAMMA8_MASK, GAMMA8_MASK],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
        if all_checks_pass
        else "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.global_corrected_hidden_split_symmetry",
        "status": status,
        "object": "d20",
        "claim": (
            "Among the 120 public D20 H-cycle graph automorphisms, exactly two preserve the rank-one "
            "global corrected hidden R33 split. The hidden split reduces the public state/edge symmetry "
            "group to a C2 stabilizer and breaks the other 118 graph symmetries."
        ),
        "definition": {
            "public_state_edge_symmetry": (
                "A graph automorphism of the 20-state, 30-edge D20 H-cycle boundary graph."
            ),
            "induced_cycle_space_action": (
                "Each state automorphism permutes the 30 edges, hence the mod-2 edge-incidence rows of "
                "closed returns; the residue spectrum converts each image row back to an 11-bit mask."
            ),
            "hidden_split_preservation": (
                "An automorphism preserves the split iff chi(Ae_i)=chi(e_i) for all 11 basis cycles, where "
                "chi(mask)=<[1,1,1,0,1,1,1,1,1,1,1],mask> over F2."
            ),
        },
        "inputs": {
            "global_corrected_charge_map_report": {
                "path": rel(GLOBAL_CORRECTED_CHARGE_MAP_REPORT),
                "sha256": sha_file(GLOBAL_CORRECTED_CHARGE_MAP_REPORT),
            },
            "hcycle_edge_table": {"path": rel(EDGE_CSV), "sha256": sha_file(EDGE_CSV)},
            "residue_spectrum": {
                "path": rel(RESIDUE_SPECTRUM_CSV),
                "sha256": sha_file(RESIDUE_SPECTRUM_CSV),
            },
            "automorphism_summary": {
                "path": rel(AUTOMORPHISM_SUMMARY),
                "sha256": sha_file(AUTOMORPHISM_SUMMARY),
            },
        },
        "derived": {
            "graph": {
                "vertices": VERTEX_COUNT,
                "edges": EDGE_COUNT,
                "degree_histogram": {"3": VERTEX_COUNT},
                "public_automorphism_count": len(automorphisms),
                "public_vertex_orbits": automorphism_summary.get("vertex_orbits"),
                "public_pair_orbit_count": automorphism_summary.get("pair_orbit_count"),
            },
            "hidden_split": {
                "coefficient_vector_over_f2": coefficients,
                "kernel_size": charge_map["derived"]["global_corrected_hidden_charge"]["kernel_size"],
                "odd_sector_size": charge_map["derived"]["global_corrected_hidden_charge"]["image_13_size"],
                "gamma8_mask": GAMMA8_MASK,
            },
            "symmetry_classification": {
                "preserving_automorphism_count": len(preserving_records),
                "breaking_automorphism_count": len(automorphism_records) - len(preserving_records),
                "stabilizer_is_c2": len(preserving_records) == 2 and nonidentity_involutive,
                "vertex_orbits_under_hidden_split_stabilizer": orbits_from_permutations(
                    preserving_vertex_perms,
                    VERTEX_COUNT,
                ),
                "edge_orbits_under_hidden_split_stabilizer": orbits_from_permutations(
                    preserving_edge_perms,
                    EDGE_COUNT,
                ),
                "gamma8_images_under_hidden_split_stabilizer": gamma8_images,
                "preserving_automorphisms": preserving_records,
                "first_breaking_witnesses": breaking_records,
            },
            "all_automorphism_records_sha256": sha_json(automorphism_records),
        },
        "interpretation": {
            "what_this_proves": [
                "the public H-cycle graph remains vertex-transitive with 120 automorphisms before the hidden split",
                "the corrected hidden character is not invariant under the public graph symmetry group",
                "only identity and one involution preserve the hidden kernel/odd-sector partition",
                "gamma_8 is fixed by the hidden split stabilizer",
            ],
            "what_this_does_not_prove": (
                "This classifies finite D20 H-cycle graph symmetries. It does not classify all automorphisms "
                "of A985 or any continuum symmetry recovery."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Promote the C2 hidden-split stabilizer to the augmented charge ledger and test whether it "
            "also preserves the sector-26 counterterm vector, the optical action weights, and the public "
            "charge components."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.global_corrected_hidden_split_symmetry_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "enumerate the 120 D20 H-cycle graph automorphisms",
            "verify each automorphism induces an action on the 11-dimensional mod-2 cycle space",
            "test the corrected hidden character against every induced basis image",
            "verify exactly two automorphisms preserve the hidden split",
            "verify the two preservers form C2 and fix gamma_8",
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
