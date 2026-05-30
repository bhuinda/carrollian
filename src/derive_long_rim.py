from __future__ import annotations

import csv
import hashlib
import json
from itertools import combinations, permutations
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


THEOREM_ID = "long_rim"
STATUS = "LONG_RIM_DEFECT_PHASES_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

ATLAS_REPORT = PROOF_ROOT / "c985_d20_boundary_invariant_atlas" / "report.json"
ATLAS_CSV = (
    PROOF_ROOT
    / "c985_d20_boundary_invariant_atlas"
    / "d20_boundary_invariant_atlas.csv"
)
HYPERBOLIC_REPORT = PROOF_ROOT / "c985_d20_hyperbolic_boundary_graph" / "report.json"
HYPERBOLIC_EDGES = (
    PROOF_ROOT
    / "c985_d20_hyperbolic_boundary_graph"
    / "boundary_hyperbolic_edges.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rim.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rim.py"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
H6_INDEX = {label: index for index, label in enumerate(H6_LABELS)}

COEFF_COLUMNS = [f"coeff_x{power}" for power in range(20, -1, -1)]
CLASS_COLUMNS = [
    "class_id",
    "orbit_count",
    "rim_count",
    "rank",
    "nullity",
    "golden_flag",
    *COEFF_COLUMNS,
]
ORBIT_COLUMNS = [
    "orbit_id",
    "class_id",
    "orbit_rim_count",
    "rank",
    "nullity",
    "golden_flag",
    "representative_rim",
    "charpoly_sha256",
]
RANK_COLUMNS = [
    "rank",
    "nullity",
    "class_count",
    "orbit_count",
    "rim_count",
    "golden_class_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

OBS_NAMES = [
    "atom_count",
    "johnson_edge_count",
    "johnson_diameter",
    "complement_pair_count",
    "normalized_oriented_rim_count",
    "normalized_unoriented_rim_count",
    "s6_automorphism_count",
    "s6_rim_orbit_count",
    "defect_polynomial_class_count",
    "golden_defect_class_count",
    "golden_defect_orbit_count",
    "golden_defect_unoriented_rim_count",
    "golden_defect_oriented_rim_count",
    "golden_defect_canonical_flag",
    "defect_phase_flag",
    "golden_special_phase_flag",
    "minimum_defect_rank",
    "maximum_defect_rank",
    "rank10_defect_class_count",
    "rank10_defect_orbit_count",
    "rank10_defect_unoriented_rim_count",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def triple_from_label(label: str) -> tuple[int, int, int]:
    return tuple(H6_INDEX[item] for item in label.split("|"))


def poly_mul(left: list[int], right: list[int]) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] += x * y
    return out


def golden_charpoly_coefficients() -> tuple[int, ...]:
    x10 = [1] + [0] * 10
    x2_minus_36 = [1, 0, -36]
    quartic = [1, 0, -52, 0, 656]
    return tuple(poly_mul(x10, poly_mul(x2_minus_36, poly_mul(quartic, quartic))))


GOLDEN_COEFFS = golden_charpoly_coefficients()


def matrix_multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    n = len(left)
    m = len(right[0])
    k = len(right)
    return [
        [sum(left[i][t] * right[t][j] for t in range(k)) for j in range(m)]
        for i in range(n)
    ]


def charpoly_coefficients(matrix: list[list[int]]) -> tuple[int, ...]:
    """Return det(xI - matrix) coefficients from x^n down to x^0."""

    n = len(matrix)
    power = [row[:] for row in matrix]
    traces: list[int] = []
    for _ in range(1, n + 1):
        traces.append(sum(power[index][index] for index in range(n)))
        power = matrix_multiply(power, matrix)

    coefficients = [1]
    for k in range(1, n + 1):
        numerator = sum(coefficients[k - i] * traces[i - 1] for i in range(1, k + 1))
        if numerator % k != 0:
            raise AssertionError(f"nonintegral charpoly coefficient at {k}")
        coefficients.append(-numerator // k)
    return tuple(coefficients)


def zero_multiplicity(coefficients: tuple[int, ...]) -> int:
    count = 0
    for value in reversed(coefficients):
        if value != 0:
            break
        count += 1
    return count


def load_boundary() -> dict[str, Any]:
    atlas_rows = read_csv_dicts(ATLAS_CSV)
    if len(atlas_rows) != 20:
        raise AssertionError("atlas atom count mismatch")
    atlas_rows.sort(key=lambda row: int(row["atom_id"]))
    triples = [triple_from_label(row["h6_triple"]) for row in atlas_rows]
    expected_triples = list(combinations(range(6), 3))
    if triples != expected_triples:
        raise AssertionError("atlas H6 triple order mismatch")
    complement = [int(row["complement_atom_id"]) for row in atlas_rows]
    expected_complement = [
        expected_triples.index(tuple(x for x in range(6) if x not in triple))
        for triple in expected_triples
    ]
    if complement != expected_complement:
        raise AssertionError("atlas complement map mismatch")

    adjacency = [[0] * 20 for _ in range(20)]
    sets = [set(triple) for triple in triples]
    for i, left in enumerate(sets):
        for j, right in enumerate(sets):
            adjacency[i][j] = 1 if i != j and len(left & right) == 2 else 0
    edge_count = sum(adjacency[i][j] for i in range(20) for j in range(i + 1, 20))
    if edge_count != 90:
        raise AssertionError("Johnson edge count mismatch")

    edge_rows = read_csv_dicts(HYPERBOLIC_EDGES)
    for row in edge_rows:
        i = int(row["atom_i"])
        j = int(row["atom_j"])
        if int(row["is_johnson_edge"]) != adjacency[i][j]:
            raise AssertionError(f"hyperbolic edge row mismatch at {i},{j}")

    return {
        "triples": triples,
        "complement": complement,
        "adjacency": adjacency,
        "edge_count": edge_count,
    }


def normalize_started_rim(rim: tuple[int, ...]) -> tuple[int, ...]:
    reversed_rim = (0,) + tuple(reversed(rim[1:]))
    return min(tuple(rim), reversed_rim)


def normalize_any_rim(rim: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    sequence = tuple(rim)
    start = sequence.index(0)
    rotated = sequence[start:] + sequence[:start]
    return normalize_started_rim(rotated)


def enumerate_rims(adjacency: list[list[int]], complement: list[int]) -> set[tuple[int, ...]]:
    pairs: list[tuple[int, int]] = []
    seen: set[int] = set()
    for atom in range(20):
        if atom in seen:
            continue
        pair = tuple(sorted((atom, complement[atom])))
        pairs.append(pair)
        seen.update(pair)
    remaining_pairs = [pair for pair in pairs if pair != (0, complement[0])]

    rims: set[tuple[int, ...]] = set()

    def backtrack(path: list[int], used_pairs: set[tuple[int, int]]) -> None:
        if len(path) == 10:
            if adjacency[path[-1]][complement[0]]:
                rim = tuple(path + [complement[atom] for atom in path])
                rims.add(normalize_started_rim(rim))
            return

        previous = path[-1]
        for pair in remaining_pairs:
            if pair in used_pairs:
                continue
            for atom in pair:
                if adjacency[previous][atom]:
                    used_pairs.add(pair)
                    path.append(atom)
                    backtrack(path, used_pairs)
                    path.pop()
                    used_pairs.remove(pair)

    backtrack([0], set())
    return rims


def s6_atom_maps(triples: list[tuple[int, int, int]]) -> list[tuple[int, ...]]:
    triple_index = {triple: index for index, triple in enumerate(triples)}
    return [
        tuple(
            triple_index[tuple(sorted(perm[item] for item in triple))]
            for triple in triples
        )
        for perm in permutations(range(6))
    ]


def orbit_from_seed(
    seed: tuple[int, ...],
    maps: list[tuple[int, ...]],
) -> set[tuple[int, ...]]:
    return {normalize_any_rim([mapping[atom] for atom in seed]) for mapping in maps}


def defect_matrix(
    rim: tuple[int, ...],
    adjacency: list[list[int]],
) -> list[list[int]]:
    successor = {rim[index]: rim[(index + 1) % 20] for index in range(20)}
    return [
        [
            adjacency[successor[left]][successor[right]] - adjacency[left][right]
            for right in range(20)
        ]
        for left in range(20)
    ]


def pipe(values: tuple[int, ...] | list[int]) -> str:
    return "|".join(str(value) for value in values)


def classify_rims() -> dict[str, Any]:
    boundary = load_boundary()
    adjacency = boundary["adjacency"]
    complement = boundary["complement"]
    rims = enumerate_rims(adjacency, complement)
    maps = s6_atom_maps(boundary["triples"])
    unseen = set(rims)
    orbit_records: list[dict[str, Any]] = []
    class_accumulator: dict[tuple[int, ...], dict[str, Any]] = {}

    while unseen:
        seed = min(unseen)
        orbit = orbit_from_seed(seed, maps)
        if not orbit <= rims:
            raise AssertionError("S6 image left the admissible rim set")
        unseen -= orbit

        coefficients = charpoly_coefficients(defect_matrix(seed, adjacency))
        nullity = zero_multiplicity(coefficients)
        rank = 20 - nullity
        golden_flag = int(coefficients == GOLDEN_COEFFS)
        digest = sha_text(pipe(coefficients))
        orbit_records.append(
            {
                "seed": seed,
                "orbit_rim_count": len(orbit),
                "coefficients": coefficients,
                "rank": rank,
                "nullity": nullity,
                "golden_flag": golden_flag,
                "charpoly_sha256": digest,
            }
        )
        entry = class_accumulator.setdefault(
            coefficients,
            {
                "orbit_count": 0,
                "rim_count": 0,
                "rank": rank,
                "nullity": nullity,
                "golden_flag": golden_flag,
                "representative": seed,
            },
        )
        entry["orbit_count"] += 1
        entry["rim_count"] += len(orbit)

    class_items = sorted(
        class_accumulator.items(),
        key=lambda item: (
            -int(item[1]["golden_flag"]),
            -int(item[1]["rim_count"]),
            item[0],
        ),
    )
    class_id_by_coefficients = {
        coefficients: class_id for class_id, (coefficients, _) in enumerate(class_items)
    }

    class_rows: list[dict[str, Any]] = []
    for class_id, (coefficients, entry) in enumerate(class_items):
        row = {
            "class_id": class_id,
            "orbit_count": int(entry["orbit_count"]),
            "rim_count": int(entry["rim_count"]),
            "rank": int(entry["rank"]),
            "nullity": int(entry["nullity"]),
            "golden_flag": int(entry["golden_flag"]),
        }
        for column, coefficient in zip(COEFF_COLUMNS, coefficients):
            row[column] = coefficient
        class_rows.append(row)

    orbit_rows: list[dict[str, Any]] = []
    for orbit_id, record in enumerate(sorted(orbit_records, key=lambda row: row["seed"])):
        coefficients = record["coefficients"]
        orbit_rows.append(
            {
                "orbit_id": orbit_id,
                "class_id": class_id_by_coefficients[coefficients],
                "orbit_rim_count": int(record["orbit_rim_count"]),
                "rank": int(record["rank"]),
                "nullity": int(record["nullity"]),
                "golden_flag": int(record["golden_flag"]),
                "representative_rim": pipe(record["seed"]),
                "charpoly_sha256": str(record["charpoly_sha256"]),
            }
        )

    rank_rows: list[dict[str, Any]] = []
    for rank in sorted({int(row["rank"]) for row in class_rows}):
        nullity = 20 - rank
        matching_classes = [row for row in class_rows if int(row["rank"]) == rank]
        matching_orbits = [row for row in orbit_rows if int(row["rank"]) == rank]
        rank_rows.append(
            {
                "rank": rank,
                "nullity": nullity,
                "class_count": len(matching_classes),
                "orbit_count": len(matching_orbits),
                "rim_count": sum(int(row["orbit_rim_count"]) for row in matching_orbits),
                "golden_class_count": sum(
                    int(row["golden_flag"]) for row in matching_classes
                ),
            }
        )

    golden_orbits = [row for row in orbit_rows if int(row["golden_flag"]) == 1]
    rank10_classes = [row for row in class_rows if int(row["rank"]) == 10]
    rank10_orbits = [row for row in orbit_rows if int(row["rank"]) == 10]
    obs = {
        "atom_count": 20,
        "johnson_edge_count": int(boundary["edge_count"]),
        "johnson_diameter": 3,
        "complement_pair_count": 10,
        "normalized_oriented_rim_count": 2 * len(rims),
        "normalized_unoriented_rim_count": len(rims),
        "s6_automorphism_count": len(maps),
        "s6_rim_orbit_count": len(orbit_rows),
        "defect_polynomial_class_count": len(class_rows),
        "golden_defect_class_count": sum(int(row["golden_flag"]) for row in class_rows),
        "golden_defect_orbit_count": len(golden_orbits),
        "golden_defect_unoriented_rim_count": sum(
            int(row["orbit_rim_count"]) for row in golden_orbits
        ),
        "golden_defect_oriented_rim_count": 2
        * sum(int(row["orbit_rim_count"]) for row in golden_orbits),
        "golden_defect_canonical_flag": int(len(class_rows) == 1),
        "defect_phase_flag": int(len(class_rows) > 1),
        "golden_special_phase_flag": int(
            len(class_rows) > 1 and len(golden_orbits) == 1
        ),
        "minimum_defect_rank": min(int(row["rank"]) for row in class_rows),
        "maximum_defect_rank": max(int(row["rank"]) for row in class_rows),
        "rank10_defect_class_count": len(rank10_classes),
        "rank10_defect_orbit_count": len(rank10_orbits),
        "rank10_defect_unoriented_rim_count": sum(
            int(row["orbit_rim_count"]) for row in rank10_orbits
        ),
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
        "class_rows": class_rows,
        "orbit_rows": orbit_rows,
        "rank_rows": rank_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = classify_rims()
    obs = rows["obs"]
    atlas_report = load_json(ATLAS_REPORT)
    hyperbolic_report = load_json(HYPERBOLIC_REPORT)
    class_table = table_from_rows(CLASS_COLUMNS, rows["class_rows"])
    rank_table = table_from_rows(RANK_COLUMNS, rows["rank_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    orbit_numeric_rows = [
        {
            "orbit_id": row["orbit_id"],
            "class_id": row["class_id"],
            "orbit_rim_count": row["orbit_rim_count"],
            "rank": row["rank"],
            "nullity": row["nullity"],
            "golden_flag": row["golden_flag"],
        }
        for row in rows["orbit_rows"]
    ]
    orbit_table = table_from_rows(
        [
            "orbit_id",
            "class_id",
            "orbit_rim_count",
            "rank",
            "nullity",
            "golden_flag",
        ],
        orbit_numeric_rows,
    )
    checks = {
        "input_boundary_reports_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED"
        and atlas_report.get("all_checks_pass") is True
        and hyperbolic_report.get("status")
        == "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED"
        and hyperbolic_report.get("all_checks_pass") is True,
        "johnson_boundary_counts_match": obs["atom_count"] == 20
        and obs["johnson_edge_count"] == 90
        and obs["johnson_diameter"] == 3
        and obs["complement_pair_count"] == 10,
        "admissible_rim_universe_enumerated": obs["normalized_oriented_rim_count"]
        == 177408
        and obs["normalized_unoriented_rim_count"] == 88704,
        "s6_orbit_partition_exact": obs["s6_automorphism_count"] == 720
        and obs["s6_rim_orbit_count"] == 124
        and sum(int(row["orbit_rim_count"]) for row in rows["orbit_rows"])
        == obs["normalized_unoriented_rim_count"],
        "defect_classes_are_finite_phases": obs["defect_polynomial_class_count"] == 63
        and obs["defect_phase_flag"] == 1
        and obs["golden_defect_canonical_flag"] == 0,
        "golden_defect_is_special_phase": obs["golden_defect_class_count"] == 1
        and obs["golden_defect_orbit_count"] == 1
        and obs["golden_defect_unoriented_rim_count"] == 144
        and obs["golden_special_phase_flag"] == 1,
        "table_shapes_match": class_table.shape
        == (obs["defect_polynomial_class_count"], len(CLASS_COLUMNS))
        and orbit_table.shape == (obs["s6_rim_orbit_count"], 6)
        and rank_table.shape[1] == len(RANK_COLUMNS)
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "complement_antipodal_c20_rim_defect_phase_classification",
        "operator_convention": "Delta_half = P^{-1} A_J P - A_J, where P advances one step along the visible C20 rim",
        "summary": {
            "atom_count": obs["atom_count"],
            "johnson_edge_count": obs["johnson_edge_count"],
            "complement_pair_count": obs["complement_pair_count"],
            "normalized_unoriented_rims": obs["normalized_unoriented_rim_count"],
            "normalized_oriented_rims": obs["normalized_oriented_rim_count"],
            "s6_rim_orbits": obs["s6_rim_orbit_count"],
            "defect_polynomial_classes": obs["defect_polynomial_class_count"],
            "classification_outcome": "finite_defect_phases",
            "golden_defect_canonical_flag": obs["golden_defect_canonical_flag"],
            "golden_defect_class_count": obs["golden_defect_class_count"],
            "golden_defect_orbit_count": obs["golden_defect_orbit_count"],
            "golden_defect_unoriented_rims": obs[
                "golden_defect_unoriented_rim_count"
            ],
            "golden_defect_oriented_rims": obs["golden_defect_oriented_rim_count"],
            "golden_defect_rank": 10,
            "golden_defect_nullity": 10,
            "golden_charpoly_factorization": "x^10*(x^2-36)*(x^4-52*x^2+656)^2",
            "golden_spectrum_squares": ["36", "26+2*sqrt(5)", "26-2*sqrt(5)"],
            "minimum_defect_rank": obs["minimum_defect_rank"],
            "maximum_defect_rank": obs["maximum_defect_rank"],
        },
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "class_table_sha256": sha_array(class_table),
        "orbit_table_sha256": sha_array(orbit_table),
        "rank_table_sha256": sha_array(rank_table),
        "observable_table_sha256": sha_array(observable_table),
        "class_text_sha256": sha_text(csv_text(CLASS_COLUMNS, rows["class_rows"])),
        "orbit_text_sha256": sha_text(csv_text(ORBIT_COLUMNS, rows["orbit_rows"])),
        "rank_text_sha256": sha_text(csv_text(RANK_COLUMNS, rows["rank_rows"])),
    }
    rim_classification = {
        "schema": "long.rim@1",
        "object": "complement_antipodal_c20_rim_defect_phase_classification",
        "status": STATUS if all(checks.values()) else "LONG_RIM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rim.report@1",
        "status": rim_classification["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rim classifies complement-antipodal Hamiltonian C20 rims in "
            "the certified J(6,3) boundary. The half-tick defect polynomial is "
            "not canonical across all admissible rims: the 88,704 unoriented "
            "rims split into 63 finite defect polynomial phases. The golden "
            "rank-10 polynomial is realized by one S6 rim orbit containing 144 "
            "unoriented rims, so it is a special rim phase rather than a "
            "J(6,3)-canonical invariant."
        ),
        "stage_protocol": {
            "draft": "read the certified d20 atom atlas and Johnson J(6,3) hyperbolic boundary graph",
            "witness": "enumerate complement-antipodal C20 rims, S6 rim orbits, defect polynomials, and rank rows",
            "coherence": "check atlas order, complement involution, Johnson edge rows, orbit partition, polynomial classes, and table hashes",
            "closure": "certify finite defect phases and demote canonical golden-defect status",
            "emit": "write long_rim artifacts and verifier hook",
        },
        "inputs": {
            "atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "atlas_csv": input_entry(ATLAS_CSV),
            "hyperbolic_report": input_entry(
                HYPERBOLIC_REPORT,
                {
                    "status": hyperbolic_report.get("status"),
                    "certificate_sha256": hyperbolic_report.get("certificate_sha256"),
                },
            ),
            "hyperbolic_edges": input_entry(HYPERBOLIC_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rim_classification": relpath(OUT_DIR / "rim_classification.json"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
            "orbit_csv": relpath(OUT_DIR / "orbit.csv"),
            "rank_csv": relpath(OUT_DIR / "rank.csv"),
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
                "D20 is realized as the 20 atom C(H6,3) boundary for this test",
                "the certified Johnson graph has 20 vertices and 90 edges",
                "all complement-antipodal Hamiltonian C20 rims are enumerated up to rotation and reversal",
                "the admissible rim universe has 88,704 unoriented normalized rims",
                "the S6 action partitions those rims into 124 rim orbits",
                "the half-tick defect polynomials form 63 finite classes",
                "the golden polynomial x^10*(x^2-36)*(x^4-52*x^2+656)^2 occurs in one S6 orbit with 144 unoriented rims",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the golden half-tick defect is canonical for J(6,3)",
                "that the stress graph or transition semantics selects the golden rim orbit",
                "a nondegenerate Lorentzian metric, curvature tensor, or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build a rim-selection gate: compare the golden rim orbit against the "
            "certified stress/contact/transition surfaces and decide whether any "
            "existing certificate selects that phase rather than leaving it as a "
            "rim gauge choice."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rim.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rim.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rim_classification": rim_classification,
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "orbit_csv": csv_text(ORBIT_COLUMNS, rows["orbit_rows"]),
        "rank_csv": csv_text(RANK_COLUMNS, rows["rank_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": class_table,
        "orbit_table": orbit_table,
        "rank_table": rank_table,
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
    write_json(OUT_DIR / "rim_classification.json", payloads["rim_classification"])
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "orbit.csv").write_text(payloads["orbit_csv"], encoding="utf-8")
    (OUT_DIR / "rank.csv").write_text(payloads["rank_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        orbit_table=payloads["orbit_table"],
        rank_table=payloads["rank_table"],
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
