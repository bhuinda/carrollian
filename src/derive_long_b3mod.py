from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, deque
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


EXPECTED_OBJECT_SIZES_BY_LABEL = [384, 192, 144, 576, 512, 768]
EXPECTED_SORTED_OBJECT_SIZES = sorted(EXPECTED_OBJECT_SIZES_BY_LABEL)
EXPECTED_GROUP_ORDER = 9216
EXPECTED_POINTS = 2576

THEOREM_ID = "long_b3mod"
STATUS = "LONG_B3MOD_ACTION_CHARACTER_SOURCE_BOUNDARY_PROVISIONAL"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

DOCS_REAL = ROOT / "docs" / "real.txt"
COORIENT_NPZ = ROOT / "data" / "coorient" / "be3_coorient_generators.npz"
COORIENT_FORMULA = ROOT / "data" / "coorient" / "lifted_coorient_signature_formula.json"
SOURCE_CACHE_REPORT = (
    D20_INVARIANTS / "theorems" / "zero_axiom_coorient_cache" / "report.json"
)
STRICT_REPLAY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "zero_axiom_coorient_strict_replay"
    / "report.json"
)
LONG_KR39 = PROOF_ROOT / "long_kr39" / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_b3mod.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_b3mod.py"

OBJECT_LABELS = ["B_minus", "B_plus", "V_minus", "V_plus", "S_minus", "S_plus"]
E_LABELS = [f"E{i}" for i in range(8)]

CLASS_COLUMNS = [
    "class_id",
    "representative_index",
    "class_size",
    "element_order",
    "cycle_count",
    "fixed_B_minus",
    "fixed_B_plus",
    "fixed_V_minus",
    "fixed_V_plus",
    "fixed_S_minus",
    "fixed_S_plus",
]
PERMCHAR_COLUMNS = [
    "class_id",
    "character_B_minus",
    "character_B_plus",
    "character_V_minus",
    "character_V_plus",
    "character_S_minus",
    "character_S_plus",
]
E_COLUMNS = [
    "e_id",
    "e_label_code",
    "irrep_decomposition_present_flag",
    "c2_projection_present_flag",
    "open_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "coorient_action_source",
    "conjugacy_class_screen",
    "six_orbit_permutation_characters",
    "irreducible_character_table_missing",
    "E0_E7_decomposition_missing",
    "R7_C2_projection_missing",
    "krein_acceptance_basis_missing",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "generator_count",
    "degree",
    "group_order",
    "point_orbit_count",
    "object_size_sum",
    "class_count",
    "class_size_sum",
    "max_class_size",
    "permutation_character_count",
    "permutation_character_constant_flag",
    "e_module_row_count",
    "e_module_decomposition_present_count",
    "c2_projection_present_count",
    "acceptance_completion_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def invert_perm(p: np.ndarray) -> np.ndarray:
    inv = np.empty_like(p)
    inv[p.astype(np.int64)] = np.arange(p.size, dtype=p.dtype)
    return inv


def validate_permutation_rows(gens: np.ndarray, n: int) -> None:
    target = np.arange(n, dtype=np.int64)
    for index, gen in enumerate(gens):
        if gen.shape != (n,):
            raise ValueError(f"generator {index} has shape {gen.shape}")
        if not np.array_equal(np.sort(gen.astype(np.int64)), target):
            raise ValueError(f"generator {index} is not a permutation")


def close_group(generators: np.ndarray) -> tuple[np.ndarray, list[int]]:
    n = generators.shape[1]
    identity = np.arange(n, dtype=np.int16)
    gen_list: list[np.ndarray] = []
    for gen in generators.astype(np.int16, copy=False):
        gen_list.append(gen)
        gen_list.append(invert_perm(gen))
    seen: dict[bytes, int] = {identity.tobytes(): 0}
    perms: list[np.ndarray] = [identity]
    q: deque[np.ndarray] = deque([identity])
    closure_sizes: list[int] = []
    while q:
        current = q.popleft()
        for gen in gen_list:
            candidate = gen[current]
            raw = candidate.tobytes()
            if raw not in seen:
                seen[raw] = len(perms)
                saved = candidate.copy()
                perms.append(saved)
                q.append(saved)
        if len(closure_sizes) == 0 or len(perms) >= closure_sizes[-1] * 2:
            closure_sizes.append(len(perms))
    return np.vstack(perms).astype(np.int16, copy=False), closure_sizes


def point_orbits(group: np.ndarray) -> tuple[np.ndarray, list[list[int]], list[int]]:
    n = group.shape[1]
    used = np.zeros(n, dtype=np.bool_)
    raw_orbits: list[np.ndarray] = []
    for point in range(n):
        if used[point]:
            continue
        orbit = np.unique(group[:, point]).astype(np.int32)
        used[orbit.astype(np.int64)] = True
        raw_orbits.append(orbit)
    sizes = sorted(int(orbit.size) for orbit in raw_orbits)
    size_to_label = {
        size: label for label, size in enumerate(EXPECTED_OBJECT_SIZES_BY_LABEL)
    }
    object_of_point = np.empty(n, dtype=np.int16)
    for orbit in raw_orbits:
        label = size_to_label[int(orbit.size)]
        object_of_point[orbit.astype(np.int64)] = int(label)
    return object_of_point, [orbit.astype(int).tolist() for orbit in raw_orbits], sizes


def cycle_profile(perm: np.ndarray) -> tuple[int, int, list[list[int]]]:
    used = np.zeros(perm.size, dtype=np.bool_)
    counts: Counter[int] = Counter()
    order = 1
    for start in range(perm.size):
        if used[start]:
            continue
        length = 0
        pos = start
        while not used[pos]:
            used[pos] = True
            length += 1
            pos = int(perm[pos])
        counts[length] += 1
        order = math.lcm(order, length)
    compact = [[int(length), int(count)] for length, count in sorted(counts.items())]
    return int(order), int(sum(counts.values())), compact


def conjugacy_classes(
    group: np.ndarray,
    generators: np.ndarray,
) -> tuple[list[list[int]], list[np.ndarray]]:
    gen_list: list[np.ndarray] = []
    for gen in generators.astype(np.int16, copy=False):
        gen_list.append(gen)
        gen_list.append(invert_perm(gen))
    inv_list = [invert_perm(gen) for gen in gen_list]
    lookup = {group[index].tobytes(): index for index in range(group.shape[0])}
    assigned = np.zeros(group.shape[0], dtype=np.bool_)
    classes: list[list[int]] = []
    for seed in range(group.shape[0]):
        if assigned[seed]:
            continue
        members: set[int] = {seed}
        q: deque[int] = deque([seed])
        assigned[seed] = True
        while q:
            current = q.popleft()
            element = group[current]
            for gen, inv in zip(gen_list, inv_list):
                conjugate = gen[element[inv]]
                idx = lookup.get(conjugate.tobytes())
                if idx is None:
                    raise AssertionError("conjugate not found in closed action")
                if idx not in members:
                    members.add(idx)
                    assigned[idx] = True
                    q.append(idx)
        classes.append(sorted(members))
    classes.sort(key=lambda values: values[0])
    return classes, gen_list


def fixed_matrix(group: np.ndarray, object_of_point: np.ndarray) -> np.ndarray:
    points = np.arange(group.shape[1], dtype=group.dtype)
    fixed = group == points
    out = np.zeros((group.shape[0], len(OBJECT_LABELS)), dtype=np.int64)
    for label in range(len(OBJECT_LABELS)):
        mask = object_of_point == label
        out[:, label] = fixed[:, mask].sum(axis=1)
    return out


def build_group_screen() -> dict[str, Any]:
    with np.load(COORIENT_NPZ, allow_pickle=False) as payload:
        generators = np.asarray(payload["generator_permutations"], dtype=np.int16)
    validate_permutation_rows(generators, EXPECTED_POINTS)
    group, closure_trace = close_group(generators)
    object_of_point, orbit_list, orbit_sizes = point_orbits(group)
    classes, gen_list = conjugacy_classes(group, generators)
    fixed = fixed_matrix(group, object_of_point)

    class_rows: list[dict[str, int]] = []
    permchar_rows: list[dict[str, int]] = []
    class_json: list[dict[str, Any]] = []
    permutation_character_constant = True
    for class_id, members in enumerate(classes):
        rep = members[0]
        order, cycle_count, cycles = cycle_profile(group[rep])
        char_values = [int(value) for value in fixed[rep].tolist()]
        member_fixed = fixed[np.asarray(members, dtype=np.int64), :]
        if not np.all(member_fixed == np.asarray(char_values, dtype=np.int64)):
            permutation_character_constant = False
        class_rows.append(
            {
                "class_id": class_id,
                "representative_index": rep,
                "class_size": len(members),
                "element_order": order,
                "cycle_count": cycle_count,
                "fixed_B_minus": char_values[0],
                "fixed_B_plus": char_values[1],
                "fixed_V_minus": char_values[2],
                "fixed_V_plus": char_values[3],
                "fixed_S_minus": char_values[4],
                "fixed_S_plus": char_values[5],
            }
        )
        permchar_rows.append(
            {
                "class_id": class_id,
                "character_B_minus": char_values[0],
                "character_B_plus": char_values[1],
                "character_V_minus": char_values[2],
                "character_V_plus": char_values[3],
                "character_S_minus": char_values[4],
                "character_S_plus": char_values[5],
            }
        )
        class_json.append(
            {
                "class_id": class_id,
                "representative_index": rep,
                "class_size": len(members),
                "element_order": order,
                "cycle_count": cycle_count,
                "cycle_profile": cycles,
                "six_orbit_permutation_character": {
                    OBJECT_LABELS[index]: char_values[index]
                    for index in range(len(OBJECT_LABELS))
                },
            }
        )

    return {
        "generators": generators,
        "group": group,
        "closure_trace": closure_trace,
        "object_of_point": object_of_point,
        "orbit_list": orbit_list,
        "orbit_sizes": orbit_sizes,
        "gen_list": gen_list,
        "classes": classes,
        "class_json": class_json,
        "class_rows": class_rows,
        "permchar_rows": permchar_rows,
        "permutation_character_constant": permutation_character_constant,
    }


def build_rows() -> dict[str, Any]:
    docs_real_hash = hashlib.sha256(DOCS_REAL.read_bytes()).hexdigest()
    formula = load_json(COORIENT_FORMULA)
    source_cache = load_json(SOURCE_CACHE_REPORT)
    strict_replay = load_json(STRICT_REPLAY_REPORT)
    long_kr39 = load_json(LONG_KR39)
    screen = build_group_screen()

    e_rows = [
        {
            "e_id": index,
            "e_label_code": index,
            "irrep_decomposition_present_flag": 0,
            "c2_projection_present_flag": 0,
            "open_flag": 1,
        }
        for index in range(len(E_LABELS))
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["coorient_action_source"],
            "gap_code": GAP_CODES["coorient_action_source"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["conjugacy_class_screen"],
            "gap_code": GAP_CODES["conjugacy_class_screen"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["six_orbit_permutation_characters"],
            "gap_code": GAP_CODES["six_orbit_permutation_characters"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["irreducible_character_table_missing"],
            "gap_code": GAP_CODES["irreducible_character_table_missing"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["E0_E7_decomposition_missing"],
            "gap_code": GAP_CODES["E0_E7_decomposition_missing"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["R7_C2_projection_missing"],
            "gap_code": GAP_CODES["R7_C2_projection_missing"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["krein_acceptance_basis_missing"],
            "gap_code": GAP_CODES["krein_acceptance_basis_missing"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs = {
        "generator_count": int(screen["generators"].shape[0]),
        "degree": int(screen["generators"].shape[1]),
        "group_order": int(screen["group"].shape[0]),
        "point_orbit_count": len(screen["orbit_sizes"]),
        "object_size_sum": int(sum(screen["orbit_sizes"])),
        "class_count": len(screen["classes"]),
        "class_size_sum": int(sum(len(values) for values in screen["classes"])),
        "max_class_size": int(max(len(values) for values in screen["classes"])),
        "permutation_character_count": len(OBJECT_LABELS),
        "permutation_character_constant_flag": int(
            screen["permutation_character_constant"]
        ),
        "e_module_row_count": len(e_rows),
        "e_module_decomposition_present_count": int(
            sum(row["irrep_decomposition_present_flag"] for row in e_rows)
        ),
        "c2_projection_present_count": int(
            sum(row["c2_projection_present_flag"] for row in e_rows)
        ),
        "acceptance_completion_flag": 0,
        "next_gap_code": GAP_CODES["irreducible_character_table_missing"],
    }
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "docs_real_hash": docs_real_hash,
        "formula": formula,
        "source_cache": source_cache,
        "strict_replay": strict_replay,
        "long_kr39": long_kr39,
        "screen": screen,
        "e_rows": e_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    class_table = table_from_rows(CLASS_COLUMNS, rows["screen"]["class_rows"])
    permchar_table = table_from_rows(PERMCHAR_COLUMNS, rows["screen"]["permchar_rows"])
    e_table = table_from_rows(E_COLUMNS, rows["e_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    orbit_sizes_by_label = [
        int(np.count_nonzero(rows["screen"]["object_of_point"] == index))
        for index in range(len(OBJECT_LABELS))
    ]
    checks = {
        "input_reports_checked": certified(rows["source_cache"])
        and certified(rows["strict_replay"])
        and certified(rows["long_kr39"]),
        "generator_shape_exact": obs["generator_count"] == 3
        and obs["degree"] == EXPECTED_POINTS,
        "group_action_order_exact": obs["group_order"] == EXPECTED_GROUP_ORDER
        and rows["screen"]["group"].shape == (EXPECTED_GROUP_ORDER, EXPECTED_POINTS),
        "point_orbit_sizes_exact": rows["screen"]["orbit_sizes"]
        == EXPECTED_SORTED_OBJECT_SIZES
        and orbit_sizes_by_label == [384, 192, 144, 576, 512, 768],
        "conjugacy_classes_partition_group": obs["class_count"] > 0
        and obs["class_size_sum"] == EXPECTED_GROUP_ORDER,
        "permutation_characters_constant": obs[
            "permutation_character_constant_flag"
        ]
        == 1,
        "e_module_gap_recorded": obs["e_module_row_count"] == 8
        and obs["e_module_decomposition_present_count"] == 0
        and obs["c2_projection_present_count"] == 0
        and obs["acceptance_completion_flag"] == 0,
        "table_shapes_match": class_table.shape
        == (obs["class_count"], len(CLASS_COLUMNS))
        and permchar_table.shape == (obs["class_count"], len(PERMCHAR_COLUMNS))
        and e_table.shape == (8, len(E_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "gamma_action_character_source_boundary",
        "summary": {
            "generator_count": obs["generator_count"],
            "degree": obs["degree"],
            "group_order": obs["group_order"],
            "point_orbit_count": obs["point_orbit_count"],
            "orbit_sizes_by_integral_label": orbit_sizes_by_label,
            "class_count": obs["class_count"],
            "class_size_sum": obs["class_size_sum"],
            "max_class_size": obs["max_class_size"],
            "permutation_character_count": obs["permutation_character_count"],
            "e_module_row_count": obs["e_module_row_count"],
            "e_module_decomposition_present_count": obs[
                "e_module_decomposition_present_count"
            ],
            "c2_projection_present_count": obs["c2_projection_present_count"],
            "acceptance_completion_flag": obs["acceptance_completion_flag"],
            "next_gap_code": obs["next_gap_code"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "object_labels": OBJECT_LABELS,
        "E_labels": E_LABELS,
        "generator_permutations_sha256": sha_array(rows["screen"]["generators"]),
        "action_sha256": sha_array(rows["screen"]["group"]),
        "object_of_point_sha256": sha_array(rows["screen"]["object_of_point"]),
        "class_table_sha256": sha_array(class_table),
        "class_text_sha256": sha_text(
            csv_text(CLASS_COLUMNS, rows["screen"]["class_rows"])
        ),
        "permchar_table_sha256": sha_array(permchar_table),
        "permchar_text_sha256": sha_text(
            csv_text(PERMCHAR_COLUMNS, rows["screen"]["permchar_rows"])
        ),
        "e_table_sha256": sha_array(e_table),
        "e_text_sha256": sha_text(csv_text(E_COLUMNS, rows["e_rows"])),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    source_json = {
        "schema": "long.b3mod.character_source@1",
        "status": STATUS,
        "irreducible_character_table_present_flag": 0,
        "classes": rows["screen"]["class_json"],
        "six_orbit_permutation_characters": rows["screen"]["permchar_rows"],
        "note": (
            "This file certifies the Gamma action class screen and permutation "
            "characters only; the irreducible character table remains open."
        ),
    }
    b3mod = {
        "schema": "long.b3mod@1",
        "object": "gamma_module_source_boundary",
        "status": STATUS if all(checks.values()) else "LONG_B3MOD_SOURCE_BOUNDARY_FAIL",
        "witness": witness,
    }
    report = {
        "schema": "long.b3mod.report@1",
        "status": b3mod["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_b3mod certifies the Gamma coorient action source needed before "
            "the acceptance-basis Krein computation. The action closes to order "
            "9216 on 2576 points, has six point orbits of sizes 384, 192, "
            "144, 576, 512, and 768, and now has a materialized conjugacy-class "
            "screen with six orbit permutation characters. It does not yet "
            "materialize the irreducible character table, the E0..E7 module "
            "decomposition, or the R7 C2 projection."
        ),
        "stage_protocol": {
            "draft": "read docs/real.txt, long_kr39, and the coorient action source reports",
            "witness": "emit Gamma class rows, six orbit permutation characters, E0..E7 open rows, gaps, and observables",
            "coherence": "check action order, point-orbit sizes, class partition, character constancy, and table hashes",
            "closure": "certify the source boundary and keep the irreducible module basis provisional",
            "emit": "write long_b3mod artifacts and verifier hook",
        },
        "inputs": {
            "docs_real": input_entry(DOCS_REAL, {"sha256": rows["docs_real_hash"]}),
            "coorient_npz": input_entry(
                COORIENT_NPZ,
                {
                    "generator_count": obs["generator_count"],
                    "degree": obs["degree"],
                },
            ),
            "coorient_formula": input_entry(
                COORIENT_FORMULA,
                {
                    "schema": rows["formula"].get("schema"),
                    "expected_closure_order": rows["formula"].get(
                        "expected_closure_order"
                    ),
                },
            ),
            "source_cache_report": input_entry(
                SOURCE_CACHE_REPORT,
                {
                    "status": rows["source_cache"].get("status"),
                    "certificate_sha256": rows["source_cache"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "strict_replay_report": input_entry(
                STRICT_REPLAY_REPORT,
                {
                    "status": rows["strict_replay"].get("status"),
                    "certificate_sha256": rows["strict_replay"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_kr39": input_entry(
                LONG_KR39,
                {
                    "status": rows["long_kr39"].get("status"),
                    "certificate_sha256": rows["long_kr39"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "b3mod": relpath(OUT_DIR / "b3mod.json"),
            "character_source": relpath(OUT_DIR / "widetildeB3_character_table.json"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
            "permutation_character_csv": relpath(OUT_DIR / "permutation_character.csv"),
            "e_decomposition_csv": relpath(
                OUT_DIR / "balanced_Ei_irrep_decomposition.csv"
            ),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "the Gamma coorient action source is present and closes to group order 9216",
                "the action degree is 2576 and the six point-orbit sizes are 384, 192, 144, 576, 512, and 768",
                "the conjugacy-class screen partitions all 9216 action elements",
                "the six point-orbit permutation characters are constant on the materialized classes",
                "the E0..E7 rows are emitted as explicit open module-decomposition obligations",
            ],
            "does_not_certify_because_provisional": [
                "the irreducible character table",
                "the E0..E7 irrep decomposition",
                "the R7 C2 projection",
                "the acceptance-basis Krein parameters",
                "denominator clearance or acceptance-ladder closure",
            ],
        },
        "next_highest_yield_item": (
            "Compute the irreducible character table for the Gamma action source, "
            "then decompose E0..E7 and feed the resulting basis into the Krein "
            "parameter computation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.b3mod.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.b3mod.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "b3mod": b3mod,
        "source_json": source_json,
        "class_csv": csv_text(CLASS_COLUMNS, rows["screen"]["class_rows"]),
        "permutation_character_csv": csv_text(
            PERMCHAR_COLUMNS, rows["screen"]["permchar_rows"]
        ),
        "e_csv": csv_text(E_COLUMNS, rows["e_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": class_table,
        "permchar_table": permchar_table,
        "e_table": e_table,
        "gap_table": gap_table,
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
    write_json(OUT_DIR / "b3mod.json", payloads["b3mod"])
    write_json(OUT_DIR / "widetildeB3_character_table.json", payloads["source_json"])
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "permutation_character.csv").write_text(
        payloads["permutation_character_csv"], encoding="utf-8"
    )
    (OUT_DIR / "balanced_Ei_irrep_decomposition.csv").write_text(
        payloads["e_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        permchar_table=payloads["permchar_table"],
        e_table=payloads["e_table"],
        gap_table=payloads["gap_table"],
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
