from __future__ import annotations

import csv
import hashlib
import json
from collections import deque
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
    from .derive_long_b3mod import (
        COORIENT_NPZ,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES as B3MOD_GAP_CODES,
        INDEX_PATH,
        LONG_KR39,
        OUT_DIR as B3MOD_DIR,
        build_group_screen,
        certified,
        invert_perm,
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
    from derive_long_b3mod import (
        COORIENT_NPZ,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES as B3MOD_GAP_CODES,
        INDEX_PATH,
        LONG_KR39,
        OUT_DIR as B3MOD_DIR,
        build_group_screen,
        certified,
        invert_perm,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_b3alg"
STATUS = "LONG_B3ALG_CLASS_MULTIPLICATION_TENSOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

B3MOD_REPORT = B3MOD_DIR / "report.json"
B3MOD_CLASS_CSV = B3MOD_DIR / "class.csv"
B3MOD_PERMCHAR_CSV = B3MOD_DIR / "permutation_character.csv"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_b3alg.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_b3alg.py"

PRODUCT_COLUMNS = [
    "row_id",
    "left_class",
    "right_class",
    "out_class",
    "pair_count",
    "class_size",
    "structure_constant",
]
CLASS_COLUMNS = [
    "class_id",
    "representative_index",
    "class_size",
    "inverse_class",
    "identity_class_flag",
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
    "gamma_class_screen_input",
    "class_multiplication_tensor",
    "identity_and_inverse_class_laws",
    "commutative_class_algebra",
    "associative_class_algebra",
    "irreducible_character_diagonalization_missing",
    "E0_E7_decomposition_missing",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "group_order",
    "degree",
    "class_count",
    "class_size_sum",
    "nonzero_product_row_count",
    "dense_product_entry_count",
    "max_structure_constant",
    "identity_class",
    "identity_law_pass_flag",
    "inverse_law_pass_flag",
    "commutativity_pass_flag",
    "associativity_pass_flag",
    "balance_pass_flag",
    "irreducible_table_present_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def close_group_with_parents(generators: np.ndarray) -> dict[str, np.ndarray]:
    n = generators.shape[1]
    identity = np.arange(n, dtype=np.int16)
    gen_list: list[np.ndarray] = []
    for gen in generators.astype(np.int16, copy=False):
        gen_list.append(gen)
        gen_list.append(invert_perm(gen))
    seen: dict[bytes, int] = {identity.tobytes(): 0}
    perms: list[np.ndarray] = [identity]
    parent = [-1]
    parent_gen = [-1]
    q: deque[int] = deque([0])
    while q:
        current_idx = q.popleft()
        current = perms[current_idx]
        for gen_idx, gen in enumerate(gen_list):
            candidate = gen[current]
            raw = candidate.tobytes()
            if raw not in seen:
                seen[raw] = len(perms)
                perms.append(candidate.copy())
                parent.append(current_idx)
                parent_gen.append(gen_idx)
                q.append(len(perms) - 1)
    return {
        "group": np.vstack(perms).astype(np.int16, copy=False),
        "parent": np.asarray(parent, dtype=np.int32),
        "parent_gen": np.asarray(parent_gen, dtype=np.int16),
        "gen_list": np.vstack(gen_list).astype(np.int16, copy=False),
    }


def left_multiplication_table(
    group: np.ndarray,
    gen_list: np.ndarray,
) -> np.ndarray:
    lookup = {group[index].tobytes(): index for index in range(group.shape[0])}
    left = np.empty((gen_list.shape[0], group.shape[0]), dtype=np.int16)
    for gen_idx, gen in enumerate(gen_list):
        for element_idx, element in enumerate(group):
            product = gen[element]
            found = lookup.get(product.tobytes())
            if found is None:
                raise AssertionError("left generator product is outside group")
            left[gen_idx, element_idx] = found
    return left


def multiplication_table(
    left: np.ndarray,
    parent: np.ndarray,
    parent_gen: np.ndarray,
) -> np.ndarray:
    n = int(parent.shape[0])
    table = np.empty((n, n), dtype=np.int16)
    table[0, :] = np.arange(n, dtype=np.int16)
    for row in range(1, n):
        table[row, :] = left[int(parent_gen[row]), table[int(parent[row]), :]]
    return table


def inverse_classes(
    group: np.ndarray,
    class_of_element: np.ndarray,
) -> list[int]:
    lookup = {group[index].tobytes(): index for index in range(group.shape[0])}
    out = []
    for element in group:
        inv = invert_perm(element)
        found = lookup.get(inv.tobytes())
        if found is None:
            raise AssertionError("inverse element is outside group")
        out.append(int(class_of_element[found]))
    return out


def class_tensor(screen: dict[str, Any]) -> dict[str, Any]:
    with np.load(COORIENT_NPZ, allow_pickle=False) as payload:
        generators = np.asarray(payload["generator_permutations"], dtype=np.int16)
    closed = close_group_with_parents(generators)
    group = closed["group"]
    parent = closed["parent"]
    parent_gen = closed["parent_gen"]
    gen_list = closed["gen_list"]
    if not np.array_equal(group, screen["group"]):
        raise AssertionError("parented closure order differs from b3mod closure")
    left = left_multiplication_table(group, gen_list)
    mult = multiplication_table(left, parent, parent_gen)

    class_count = len(screen["classes"])
    class_of_element = np.empty(group.shape[0], dtype=np.int16)
    class_sizes = np.zeros(class_count, dtype=np.int64)
    for class_id, members in enumerate(screen["classes"]):
        class_of_element[np.asarray(members, dtype=np.int64)] = class_id
        class_sizes[class_id] = len(members)

    tensor = np.zeros((class_count, class_count, class_count), dtype=np.int64)
    pair_counts = np.zeros_like(tensor)
    for i, left_members in enumerate(screen["classes"]):
        left_idx = np.asarray(left_members, dtype=np.int64)
        for j, right_members in enumerate(screen["classes"]):
            right_idx = np.asarray(right_members, dtype=np.int64)
            products = mult[np.ix_(left_idx, right_idx)]
            counts = np.bincount(
                class_of_element[products.reshape(-1)].astype(np.int64),
                minlength=class_count,
            ).astype(np.int64)
            pair_counts[i, j, :] = counts
            if np.any(counts % class_sizes):
                raise AssertionError("class product count is not class-size divisible")
            tensor[i, j, :] = counts // class_sizes

    inv_by_element = inverse_classes(group, class_of_element)
    inverse_class = []
    for class_id, members in enumerate(screen["classes"]):
        values = {inv_by_element[element] for element in members}
        if len(values) != 1:
            raise AssertionError(f"class {class_id} inverse is not class-constant")
        inverse_class.append(values.pop())

    return {
        "group": group,
        "left": left,
        "multiplication": mult,
        "class_of_element": class_of_element,
        "class_sizes": class_sizes,
        "tensor": tensor,
        "pair_counts": pair_counts,
        "inverse_class": inverse_class,
    }


def associativity_holds(tensor: np.ndarray) -> bool:
    left = np.einsum("ijl,lkm->ijkm", tensor, tensor, optimize=True)
    right = np.einsum("jkl,ilm->ijkm", tensor, tensor, optimize=True)
    return bool(np.array_equal(left, right))


def build_rows() -> dict[str, Any]:
    b3mod = load_json(B3MOD_REPORT)
    long_kr39 = load_json(LONG_KR39)
    _, b3mod_class_rows = read_csv_rows(B3MOD_CLASS_CSV)
    _, b3mod_permchar_rows = read_csv_rows(B3MOD_PERMCHAR_CSV)
    screen = build_group_screen()
    tensor_data = class_tensor(screen)
    tensor = tensor_data["tensor"]
    pair_counts = tensor_data["pair_counts"]
    class_sizes = tensor_data["class_sizes"]
    class_count = int(tensor.shape[0])
    identity_class = 0

    product_rows = []
    row_id = 0
    for i in range(class_count):
        for j in range(class_count):
            for k in range(class_count):
                value = int(tensor[i, j, k])
                pairs = int(pair_counts[i, j, k])
                if value == 0 and pairs == 0:
                    continue
                product_rows.append(
                    {
                        "row_id": row_id,
                        "left_class": i,
                        "right_class": j,
                        "out_class": k,
                        "pair_count": pairs,
                        "class_size": int(class_sizes[k]),
                        "structure_constant": value,
                    }
                )
                row_id += 1

    class_rows = []
    for class_id, members in enumerate(screen["classes"]):
        class_rows.append(
            {
                "class_id": class_id,
                "representative_index": int(members[0]),
                "class_size": int(class_sizes[class_id]),
                "inverse_class": int(tensor_data["inverse_class"][class_id]),
                "identity_class_flag": int(class_id == identity_class),
            }
        )

    identity_law = True
    for class_id in range(class_count):
        if tensor[identity_class, class_id, class_id] != 1:
            identity_law = False
        if tensor[class_id, identity_class, class_id] != 1:
            identity_law = False
        if int(tensor[identity_class, class_id, :].sum()) != 1:
            identity_law = False
        if int(tensor[class_id, identity_class, :].sum()) != 1:
            identity_law = False

    inverse_law = True
    for class_id, inv_class in enumerate(tensor_data["inverse_class"]):
        if tensor[class_id, inv_class, identity_class] != int(class_sizes[class_id]):
            inverse_law = False
        if tensor[inv_class, class_id, identity_class] != int(class_sizes[class_id]):
            inverse_law = False

    balance = np.einsum("ijk,k->ij", tensor, class_sizes, optimize=True)
    expected_balance = class_sizes[:, None] * class_sizes[None, :]
    balance_law = bool(np.array_equal(balance, expected_balance))
    commutative = bool(np.array_equal(tensor, np.swapaxes(tensor, 0, 1)))
    associative = associativity_holds(tensor)

    gap_rows = [
        {
            "gap_id": GAP_CODES["gamma_class_screen_input"],
            "gap_code": GAP_CODES["gamma_class_screen_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["class_multiplication_tensor"],
            "gap_code": GAP_CODES["class_multiplication_tensor"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["identity_and_inverse_class_laws"],
            "gap_code": GAP_CODES["identity_and_inverse_class_laws"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["commutative_class_algebra"],
            "gap_code": GAP_CODES["commutative_class_algebra"],
            "certified_flag": int(commutative),
            "open_flag": int(not commutative),
            "obstruction_flag": int(not commutative),
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["associative_class_algebra"],
            "gap_code": GAP_CODES["associative_class_algebra"],
            "certified_flag": int(associative),
            "open_flag": int(not associative),
            "obstruction_flag": int(not associative),
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["irreducible_character_diagonalization_missing"],
            "gap_code": GAP_CODES["irreducible_character_diagonalization_missing"],
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
    ]
    obs = {
        "group_order": int(tensor_data["group"].shape[0]),
        "degree": int(tensor_data["group"].shape[1]),
        "class_count": class_count,
        "class_size_sum": int(class_sizes.sum()),
        "nonzero_product_row_count": len(product_rows),
        "dense_product_entry_count": int(tensor.size),
        "max_structure_constant": int(tensor.max()),
        "identity_class": identity_class,
        "identity_law_pass_flag": int(identity_law),
        "inverse_law_pass_flag": int(inverse_law),
        "commutativity_pass_flag": int(commutative),
        "associativity_pass_flag": int(associative),
        "balance_pass_flag": int(balance_law),
        "irreducible_table_present_flag": 0,
        "next_gap_code": GAP_CODES["irreducible_character_diagonalization_missing"],
    }
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "b3mod": b3mod,
        "long_kr39": long_kr39,
        "b3mod_class_rows": b3mod_class_rows,
        "b3mod_permchar_rows": b3mod_permchar_rows,
        "screen": screen,
        "tensor_data": tensor_data,
        "product_rows": product_rows,
        "class_rows": class_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    product_table = table_from_rows(PRODUCT_COLUMNS, rows["product_rows"])
    class_table = table_from_rows(CLASS_COLUMNS, rows["class_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    tensor = rows["tensor_data"]["tensor"]
    pair_counts = rows["tensor_data"]["pair_counts"]
    class_sizes = rows["tensor_data"]["class_sizes"]
    obs = rows["obs"]
    checks = {
        "input_reports_checked": rows["b3mod"].get("all_checks_pass") is True
        and rows["b3mod"]["witness"]["summary"].get("next_gap_code")
        == B3MOD_GAP_CODES["irreducible_character_table_missing"]
        and certified(rows["long_kr39"]),
        "class_shape_exact": obs["group_order"] == EXPECTED_GROUP_ORDER
        and obs["degree"] == EXPECTED_POINTS
        and obs["class_count"] == 41
        and obs["class_size_sum"] == EXPECTED_GROUP_ORDER,
        "tensor_shape_exact": tensor.shape == (41, 41, 41)
        and pair_counts.shape == (41, 41, 41),
        "product_rows_match_tensor": obs["nonzero_product_row_count"]
        == int(np.count_nonzero(tensor))
        and product_table.shape[0] == obs["nonzero_product_row_count"],
        "balance_identity_inverse_laws": obs["balance_pass_flag"] == 1
        and obs["identity_law_pass_flag"] == 1
        and obs["inverse_law_pass_flag"] == 1,
        "class_algebra_laws": obs["commutativity_pass_flag"] == 1
        and obs["associativity_pass_flag"] == 1,
        "irreducible_gap_recorded": obs["irreducible_table_present_flag"] == 0
        and obs["next_gap_code"]
        == GAP_CODES["irreducible_character_diagonalization_missing"],
        "table_shapes_match": class_table.shape == (41, len(CLASS_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS))
        and product_table.shape[1] == len(PRODUCT_COLUMNS),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "gamma_class_algebra_multiplication_tensor",
        "summary": {
            "group_order": obs["group_order"],
            "degree": obs["degree"],
            "class_count": obs["class_count"],
            "class_size_sum": obs["class_size_sum"],
            "nonzero_product_row_count": obs["nonzero_product_row_count"],
            "dense_product_entry_count": obs["dense_product_entry_count"],
            "max_structure_constant": obs["max_structure_constant"],
            "identity_class": obs["identity_class"],
            "identity_law_pass_flag": obs["identity_law_pass_flag"],
            "inverse_law_pass_flag": obs["inverse_law_pass_flag"],
            "commutativity_pass_flag": obs["commutativity_pass_flag"],
            "associativity_pass_flag": obs["associativity_pass_flag"],
            "balance_pass_flag": obs["balance_pass_flag"],
            "irreducible_table_present_flag": obs["irreducible_table_present_flag"],
            "next_gap_code": obs["next_gap_code"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "class_size_sha256": sha_array(class_sizes),
        "tensor_sha256": sha_array(tensor),
        "pair_count_tensor_sha256": sha_array(pair_counts),
        "class_table_sha256": sha_array(class_table),
        "class_text_sha256": sha_text(csv_text(CLASS_COLUMNS, rows["class_rows"])),
        "product_table_sha256": sha_array(product_table),
        "product_text_sha256": sha_text(
            csv_text(PRODUCT_COLUMNS, rows["product_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    class_algebra = {
        "schema": "long.b3alg.class_algebra@1",
        "status": STATUS if all(checks.values()) else "LONG_B3ALG_CLASS_ALGEBRA_FAIL",
        "class_count": obs["class_count"],
        "group_order": obs["group_order"],
        "identity_class": obs["identity_class"],
        "structure_constant_tensor_sha256": witness["tensor_sha256"],
        "class_sizes": [int(value) for value in class_sizes.tolist()],
        "inverse_class": [row["inverse_class"] for row in rows["class_rows"]],
        "law_flags": {
            "identity": obs["identity_law_pass_flag"],
            "inverse": obs["inverse_law_pass_flag"],
            "balance": obs["balance_pass_flag"],
            "commutative": obs["commutativity_pass_flag"],
            "associative": obs["associativity_pass_flag"],
        },
        "note": (
            "This is the multiplication algebra for class sums. The "
            "irreducible character diagonalization remains the next open step."
        ),
    }
    report = {
        "schema": "long.b3alg.report@1",
        "status": class_algebra["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_b3alg certifies the Gamma class-sum multiplication algebra "
            "behind the acceptance-basis character computation. The 41-class "
            "screen produces an integral 41 by 41 by 41 structure-constant "
            "tensor, satisfies the class-size balance law, has the expected "
            "identity and inverse class behavior, and is commutative and "
            "associative. It does not yet diagonalize this algebra into "
            "irreducible characters or decompose E0..E7."
        ),
        "stage_protocol": {
            "draft": "read long_b3mod, long_kr39, and the coorient action source",
            "witness": "emit class metadata, nonzero class-product rows, tensor tables, gaps, and observables",
            "coherence": "check tensor shape, class-size balance, identity, inverse, commutativity, associativity, and hashes",
            "closure": "certify the class algebra tensor while keeping irreducible diagonalization open",
            "emit": "write long_b3alg artifacts and verifier hook",
        },
        "inputs": {
            "long_b3mod": input_entry(
                B3MOD_REPORT,
                {
                    "status": rows["b3mod"].get("status"),
                    "certificate_sha256": rows["b3mod"].get("certificate_sha256"),
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
            "coorient_npz": input_entry(COORIENT_NPZ),
            "b3mod_class_csv": input_entry(
                B3MOD_CLASS_CSV,
                {"row_count": len(rows["b3mod_class_rows"])},
            ),
            "b3mod_permutation_character_csv": input_entry(
                B3MOD_PERMCHAR_CSV,
                {"row_count": len(rows["b3mod_permchar_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "class_algebra": relpath(OUT_DIR / "class_algebra.json"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
            "product_csv": relpath(OUT_DIR / "class_product.csv"),
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
                "the 41 Gamma classes form a class-sum multiplication algebra",
                "the dense structure tensor has shape 41 by 41 by 41",
                "all pair-counts are divisible by the output class size",
                "the identity class and inverse-class laws hold",
                "the class algebra is commutative and associative",
            ],
            "does_not_certify_because_open": [
                "irreducible character diagonalization",
                "ordinary character values over the complex numbers",
                "E0..E7 irrep decomposition",
                "R7 C2 projection",
                "acceptance-basis Krein parameter computation",
            ],
        },
        "next_highest_yield_item": (
            "Diagonalize the certified 41-class multiplication algebra to get "
            "the irreducible character table, then decompose the six orbit "
            "permutation characters and E0..E7."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.b3alg.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.b3alg.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "class_algebra": class_algebra,
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "product_csv": csv_text(PRODUCT_COLUMNS, rows["product_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": class_table,
        "product_table": product_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "structure_tensor": tensor,
        "pair_count_tensor": pair_counts,
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
    write_json(OUT_DIR / "class_algebra.json", payloads["class_algebra"])
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "class_product.csv").write_text(
        payloads["product_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        product_table=payloads["product_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        structure_tensor=payloads["structure_tensor"],
        pair_count_tensor=payloads["pair_count_tensor"],
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
