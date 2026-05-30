from __future__ import annotations

import csv
import hashlib
import json
import random
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
    from .derive_long_b3alg import OUT_DIR as GAMMA_ALG_DIR
    from .derive_long_b3mod import OUT_DIR as GAMMA_SOURCE_DIR
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
    from derive_long_b3alg import OUT_DIR as GAMMA_ALG_DIR
    from derive_long_b3mod import OUT_DIR as GAMMA_SOURCE_DIR
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_gchar"
STATUS = "LONG_GCHAR_MODULAR_CLASS_DIAGONALIZATION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

FIELD_PRIME = 10_007
SPLIT_SEED = 1
GROUP_ORDER = 9_216
CLASS_COUNT = 41

GAMMA_ALG_REPORT = GAMMA_ALG_DIR / "report.json"
GAMMA_ALG_TABLES = GAMMA_ALG_DIR / "tables.npz"
GAMMA_SOURCE_REPORT = GAMMA_SOURCE_DIR / "report.json"
GAMMA_PERMCHAR_CSV = GAMMA_SOURCE_DIR / "permutation_character.csv"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_gchar.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_gchar.py"

CHAR_COLUMNS = ["irrep_id", "root_mod", "degree"] + [
    f"char_c{index}_mod" for index in range(CLASS_COUNT)
]
IDEMP_COLUMNS = ["irrep_id"] + [
    f"idempotent_c{index}_mod" for index in range(CLASS_COUNT)
]
DECOMP_COLUMNS = [
    "orbit_id",
    "irrep_id",
    "multiplicity_mod",
    "multiplicity_int",
    "degree",
    "dimension_contribution",
]
E_COLUMNS = [
    "e_id",
    "e_label_code",
    "decomposition_input_present_flag",
    "modular_decomposition_present_flag",
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
    "gamma_class_algebra_input",
    "finite_field_split_element",
    "primitive_idempotents_mod_p",
    "modular_character_table",
    "row_orthogonality_mod_p",
    "six_orbit_decomposition_mod_p",
    "E0_E7_decomposition_input_missing",
    "acceptance_basis_krein_pending",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "field_prime",
    "split_seed",
    "class_count",
    "root_count",
    "distinct_root_count",
    "primitive_idempotent_count",
    "degree_square_sum",
    "orthogonality_pass_flag",
    "homomorphism_pass_flag",
    "idempotent_pass_flag",
    "permutation_character_count",
    "permutation_decomposition_row_count",
    "permutation_dimension_pass_count",
    "e_module_row_count",
    "e_decomposition_present_count",
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


def charpoly_mod(matrix: np.ndarray, prime: int) -> list[int]:
    n = int(matrix.shape[0])
    ident = np.eye(n, dtype=np.int64)
    work = ident.copy()
    coeffs: list[int] = [1]
    for step in range(1, n + 1):
        product = (matrix @ work) % prime
        coeff = (-int(np.trace(product) % prime) * pow(step, -1, prime)) % prime
        coeffs.append(coeff)
        work = (product + coeff * ident) % prime
    return coeffs


def eval_poly_mod(coeffs: list[int], value: int, prime: int) -> int:
    out = 0
    for coeff in coeffs:
        out = (out * value + coeff) % prime
    return int(out)


def roots_mod(coeffs: list[int], prime: int) -> list[int]:
    return [value for value in range(prime) if eval_poly_mod(coeffs, value, prime) == 0]


def nullvec_mod(matrix: np.ndarray, prime: int) -> np.ndarray:
    mat = matrix.copy() % prime
    rows, cols = mat.shape
    pivots: list[int] = []
    pivot_row = 0
    for col in range(cols):
        found = None
        for row in range(pivot_row, rows):
            if int(mat[row, col]) % prime:
                found = row
                break
        if found is None:
            continue
        if found != pivot_row:
            mat[[pivot_row, found]] = mat[[found, pivot_row]]
        inv = pow(int(mat[pivot_row, col]), -1, prime)
        mat[pivot_row] = (mat[pivot_row] * inv) % prime
        for row in range(rows):
            if row != pivot_row and int(mat[row, col]) % prime:
                mat[row] = (mat[row] - int(mat[row, col]) * mat[pivot_row]) % prime
        pivots.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break
    free = [col for col in range(cols) if col not in pivots]
    if len(free) != 1:
        raise AssertionError(f"expected one-dimensional eigenspace, found {len(free)}")
    vec = np.zeros(cols, dtype=np.int64)
    vec[free[0]] = 1
    for row in range(len(pivots) - 1, -1, -1):
        col = pivots[row]
        vec[col] = (-int(np.dot(mat[row], vec) % prime)) % prime
    return vec


def class_product(
    left: np.ndarray,
    right: np.ndarray,
    tensor: np.ndarray,
    prime: int,
) -> np.ndarray:
    return np.einsum("i,j,ijk->k", left, right, tensor, optimize=True) % prime


def left_action(class_id: int, vector: np.ndarray, tensor: np.ndarray, prime: int) -> np.ndarray:
    return np.einsum("j,jk->k", vector, tensor[class_id], optimize=True) % prime


def split_weights(prime: int, seed: int) -> np.ndarray:
    rng = random.Random(seed)
    return np.asarray([rng.randrange(1, prime) for _ in range(CLASS_COUNT)], dtype=np.int64)


def build_modular_data() -> dict[str, Any]:
    with np.load(GAMMA_ALG_TABLES, allow_pickle=False) as payload:
        tensor_int = np.asarray(payload["structure_tensor"], dtype=np.int64)
        class_table = np.asarray(payload["class_table"], dtype=np.int64)
    tensor = tensor_int % FIELD_PRIME
    class_sizes = class_table[:, 2].astype(np.int64)
    inverse_class = class_table[:, 3].astype(np.int64)
    weights = split_weights(FIELD_PRIME, SPLIT_SEED)
    split_matrix = np.tensordot(weights % FIELD_PRIME, tensor, axes=(0, 0)).T
    split_matrix %= FIELD_PRIME
    charpoly = charpoly_mod(split_matrix, FIELD_PRIME)
    roots = roots_mod(charpoly, FIELD_PRIME)
    if len(roots) != CLASS_COUNT or len(set(roots)) != CLASS_COUNT:
        raise AssertionError("chosen split element does not have 41 distinct roots")

    rows: list[dict[str, Any]] = []
    for root in roots:
        raw_vec = nullvec_mod(
            (split_matrix - root * np.eye(CLASS_COUNT, dtype=np.int64)) % FIELD_PRIME,
            FIELD_PRIME,
        )
        square = class_product(raw_vec, raw_vec, tensor, FIELD_PRIME)
        support = np.flatnonzero(raw_vec)
        scale = int(square[int(support[0])] * pow(int(raw_vec[int(support[0])]), -1, FIELD_PRIME) % FIELD_PRIME)
        if not np.array_equal(square, (scale * raw_vec) % FIELD_PRIME):
            raise AssertionError("eigenvector square is not scalar-proportional")
        idem = (raw_vec * pow(scale, -1, FIELD_PRIME)) % FIELD_PRIME
        idem_square = class_product(idem, idem, tensor, FIELD_PRIME)
        if not np.array_equal(idem_square, idem):
            raise AssertionError("primitive idempotent scaling failed")

        degree_square = int(idem[0] * GROUP_ORDER % FIELD_PRIME)
        degree_candidates = [
            degree for degree in range(1, 256) if degree * degree % FIELD_PRIME == degree_square
        ]
        if len(degree_candidates) != 1:
            raise AssertionError(f"degree not unique for root {root}: {degree_candidates}")
        degree = degree_candidates[0]

        central = []
        nonzero = np.flatnonzero(idem)
        pivot = int(nonzero[0])
        pivot_inv = pow(int(idem[pivot]), -1, FIELD_PRIME)
        for class_id in range(CLASS_COUNT):
            acted = left_action(class_id, idem, tensor, FIELD_PRIME)
            scalar = int(acted[pivot] * pivot_inv % FIELD_PRIME)
            if not np.array_equal(acted, (scalar * idem) % FIELD_PRIME):
                raise AssertionError("central character is not scalar on idempotent")
            central.append(scalar)
        char_values = [
            int(central[class_id] * degree * pow(int(class_sizes[class_id]), -1, FIELD_PRIME) % FIELD_PRIME)
            for class_id in range(CLASS_COUNT)
        ]
        rows.append(
            {
                "root": int(root),
                "degree": int(degree),
                "idempotent": idem.astype(np.int64),
                "central": np.asarray(central, dtype=np.int64),
                "character": np.asarray(char_values, dtype=np.int64),
            }
        )

    rows.sort(key=lambda row: (row["degree"], row["character"].astype(int).tolist()))
    for index, row in enumerate(rows):
        row["irrep_id"] = index

    chars = np.vstack([row["character"] for row in rows]).astype(np.int64)
    idempotents = np.vstack([row["idempotent"] for row in rows]).astype(np.int64)
    central = np.vstack([row["central"] for row in rows]).astype(np.int64)
    degrees = np.asarray([row["degree"] for row in rows], dtype=np.int64)
    roots_sorted = np.asarray([row["root"] for row in rows], dtype=np.int64)

    return {
        "tensor": tensor,
        "class_sizes": class_sizes,
        "inverse_class": inverse_class,
        "weights": weights,
        "split_matrix": split_matrix,
        "charpoly": np.asarray(charpoly, dtype=np.int64),
        "roots": roots_sorted,
        "characters": chars,
        "idempotents": idempotents,
        "central_characters": central,
        "degrees": degrees,
    }


def verify_idempotents(data: dict[str, Any]) -> bool:
    tensor = data["tensor"]
    idempotents = data["idempotents"]
    ident = np.zeros(CLASS_COUNT, dtype=np.int64)
    ident[0] = 1
    if not np.array_equal(idempotents.sum(axis=0) % FIELD_PRIME, ident):
        return False
    for left in range(CLASS_COUNT):
        for right in range(CLASS_COUNT):
            product = class_product(
                idempotents[left], idempotents[right], tensor, FIELD_PRIME
            )
            target = idempotents[left] if left == right else np.zeros(CLASS_COUNT, dtype=np.int64)
            if not np.array_equal(product, target % FIELD_PRIME):
                return False
    return True


def verify_homomorphisms(data: dict[str, Any]) -> bool:
    tensor = data["tensor"]
    central = data["central_characters"]
    for row in central:
        lhs = (row[:, None] * row[None, :]) % FIELD_PRIME
        rhs = np.einsum("ijk,k->ij", tensor, row, optimize=True) % FIELD_PRIME
        if not np.array_equal(lhs, rhs):
            return False
    return True


def verify_orthogonality(data: dict[str, Any]) -> bool:
    chars = data["characters"]
    sizes = data["class_sizes"] % FIELD_PRIME
    inverse_class = data["inverse_class"]
    for left in range(CLASS_COUNT):
        for right in range(CLASS_COUNT):
            total = 0
            for class_id in range(CLASS_COUNT):
                total += (
                    int(sizes[class_id])
                    * int(chars[left, class_id])
                    * int(chars[right, int(inverse_class[class_id])])
                )
            expected = GROUP_ORDER % FIELD_PRIME if left == right else 0
            if total % FIELD_PRIME != expected:
                return False
    return True


def permutation_decomposition(data: dict[str, Any]) -> dict[str, Any]:
    _, perm_rows = read_csv_rows(GAMMA_PERMCHAR_CSV)
    perm = np.asarray(
        [[int(row[f"character_{label}"]) for label in [
            "B_minus",
            "B_plus",
            "V_minus",
            "V_plus",
            "S_minus",
            "S_plus",
        ]] for row in perm_rows],
        dtype=np.int64,
    )
    chars = data["characters"]
    degrees = data["degrees"]
    sizes = data["class_sizes"]
    inverse_class = data["inverse_class"]
    rows = []
    dimension_pass = 0
    reconstructed = np.zeros((6, CLASS_COUNT), dtype=np.int64)
    for orbit_id in range(6):
        dimension = int(perm[0, orbit_id])
        dimension_sum = 0
        for irrep_id in range(CLASS_COUNT):
            total = 0
            for class_id in range(CLASS_COUNT):
                total += (
                    int(sizes[class_id])
                    * int(perm[class_id, orbit_id])
                    * int(chars[irrep_id, int(inverse_class[class_id])])
                )
            multiplicity = int(total * pow(GROUP_ORDER, -1, FIELD_PRIME) % FIELD_PRIME)
            if multiplicity > FIELD_PRIME // 2:
                raise AssertionError("negative modular multiplicity lift")
            dimension_sum += multiplicity * int(degrees[irrep_id])
            reconstructed[orbit_id] += multiplicity * chars[irrep_id]
            rows.append(
                {
                    "orbit_id": orbit_id,
                    "irrep_id": irrep_id,
                    "multiplicity_mod": multiplicity,
                    "multiplicity_int": multiplicity,
                    "degree": int(degrees[irrep_id]),
                    "dimension_contribution": int(multiplicity * degrees[irrep_id]),
                }
            )
        if dimension_sum == dimension:
            dimension_pass += 1
    reconstructed %= FIELD_PRIME
    reconstruct_pass = bool(np.array_equal(reconstructed.T, perm % FIELD_PRIME))
    return {
        "rows": rows,
        "source_rows": perm_rows,
        "dimension_pass_count": dimension_pass,
        "reconstruct_pass": reconstruct_pass,
        "permutation_character_count": 6,
    }


def build_rows() -> dict[str, Any]:
    gamma_alg = load_json(GAMMA_ALG_REPORT)
    gamma_source = load_json(GAMMA_SOURCE_REPORT)
    data = build_modular_data()
    decomp = permutation_decomposition(data)
    char_rows = []
    for irrep_id in range(CLASS_COUNT):
        row = {
            "irrep_id": irrep_id,
            "root_mod": int(data["roots"][irrep_id]),
            "degree": int(data["degrees"][irrep_id]),
        }
        row.update(
            {
                f"char_c{class_id}_mod": int(data["characters"][irrep_id, class_id])
                for class_id in range(CLASS_COUNT)
            }
        )
        char_rows.append(row)
    idem_rows = []
    for irrep_id in range(CLASS_COUNT):
        row = {"irrep_id": irrep_id}
        row.update(
            {
                f"idempotent_c{class_id}_mod": int(data["idempotents"][irrep_id, class_id])
                for class_id in range(CLASS_COUNT)
            }
        )
        idem_rows.append(row)
    e_rows = [
        {
            "e_id": index,
            "e_label_code": index,
            "decomposition_input_present_flag": 0,
            "modular_decomposition_present_flag": 0,
            "open_flag": 1,
        }
        for index in range(8)
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES[name],
            "gap_code": GAP_CODES[name],
            "certified_flag": int(index <= GAP_CODES["six_orbit_decomposition_mod_p"]),
            "open_flag": int(index > GAP_CODES["six_orbit_decomposition_mod_p"]),
            "obstruction_flag": int(index > GAP_CODES["six_orbit_decomposition_mod_p"]),
            "next_flag": int(name == "E0_E7_decomposition_input_missing"),
        }
        for index, name in enumerate(GAP_NAMES)
    ]
    obs = {
        "field_prime": FIELD_PRIME,
        "split_seed": SPLIT_SEED,
        "class_count": CLASS_COUNT,
        "root_count": int(len(data["roots"])),
        "distinct_root_count": int(len(set(int(x) for x in data["roots"].tolist()))),
        "primitive_idempotent_count": int(data["idempotents"].shape[0]),
        "degree_square_sum": int(np.sum(data["degrees"] * data["degrees"])),
        "orthogonality_pass_flag": int(verify_orthogonality(data)),
        "homomorphism_pass_flag": int(verify_homomorphisms(data)),
        "idempotent_pass_flag": int(verify_idempotents(data)),
        "permutation_character_count": decomp["permutation_character_count"],
        "permutation_decomposition_row_count": len(decomp["rows"]),
        "permutation_dimension_pass_count": decomp["dimension_pass_count"],
        "e_module_row_count": len(e_rows),
        "e_decomposition_present_count": int(
            sum(row["modular_decomposition_present_flag"] for row in e_rows)
        ),
        "next_gap_code": GAP_CODES["E0_E7_decomposition_input_missing"],
    }
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "gamma_alg": gamma_alg,
        "gamma_source": gamma_source,
        "data": data,
        "decomp": decomp,
        "char_rows": char_rows,
        "idem_rows": idem_rows,
        "decomp_rows": decomp["rows"],
        "e_rows": e_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    char_table = table_from_rows(CHAR_COLUMNS, rows["char_rows"])
    idem_table = table_from_rows(IDEMP_COLUMNS, rows["idem_rows"])
    decomp_table = table_from_rows(DECOMP_COLUMNS, rows["decomp_rows"])
    e_table = table_from_rows(E_COLUMNS, rows["e_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    data = rows["data"]
    checks = {
        "input_reports_checked": certified(rows["gamma_alg"])
        and rows["gamma_source"].get("all_checks_pass") is True,
        "finite_field_split_exact": obs["field_prime"] == FIELD_PRIME
        and obs["root_count"] == CLASS_COUNT
        and obs["distinct_root_count"] == CLASS_COUNT,
        "primitive_idempotents_verified": obs["primitive_idempotent_count"] == CLASS_COUNT
        and obs["idempotent_pass_flag"] == 1,
        "degree_and_orthogonality_verified": obs["degree_square_sum"] == GROUP_ORDER
        and obs["orthogonality_pass_flag"] == 1
        and obs["homomorphism_pass_flag"] == 1,
        "permutation_decompositions_verified": obs["permutation_character_count"] == 6
        and obs["permutation_decomposition_row_count"] == 6 * CLASS_COUNT
        and obs["permutation_dimension_pass_count"] == 6
        and rows["decomp"]["reconstruct_pass"],
        "e_gap_recorded": obs["e_module_row_count"] == 8
        and obs["e_decomposition_present_count"] == 0
        and obs["next_gap_code"] == GAP_CODES["E0_E7_decomposition_input_missing"],
        "table_shapes_match": char_table.shape == (CLASS_COUNT, len(CHAR_COLUMNS))
        and idem_table.shape == (CLASS_COUNT, len(IDEMP_COLUMNS))
        and decomp_table.shape == (6 * CLASS_COUNT, len(DECOMP_COLUMNS))
        and e_table.shape == (8, len(E_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "gamma_modular_character_diagonalization",
        "summary": {
            "field_prime": obs["field_prime"],
            "split_seed": obs["split_seed"],
            "class_count": obs["class_count"],
            "root_count": obs["root_count"],
            "distinct_root_count": obs["distinct_root_count"],
            "primitive_idempotent_count": obs["primitive_idempotent_count"],
            "degree_square_sum": obs["degree_square_sum"],
            "orthogonality_pass_flag": obs["orthogonality_pass_flag"],
            "homomorphism_pass_flag": obs["homomorphism_pass_flag"],
            "idempotent_pass_flag": obs["idempotent_pass_flag"],
            "permutation_character_count": obs["permutation_character_count"],
            "permutation_decomposition_row_count": obs[
                "permutation_decomposition_row_count"
            ],
            "permutation_dimension_pass_count": obs[
                "permutation_dimension_pass_count"
            ],
            "e_decomposition_present_count": obs["e_decomposition_present_count"],
            "next_gap_code": obs["next_gap_code"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "split_weights_sha256": sha_array(data["weights"]),
        "split_matrix_sha256": sha_array(data["split_matrix"]),
        "charpoly_sha256": sha_array(data["charpoly"]),
        "roots_sha256": sha_array(data["roots"]),
        "degree_vector_sha256": sha_array(data["degrees"]),
        "character_table_sha256": sha_array(char_table),
        "character_text_sha256": sha_text(csv_text(CHAR_COLUMNS, rows["char_rows"])),
        "idempotent_table_sha256": sha_array(idem_table),
        "decomposition_table_sha256": sha_array(decomp_table),
        "decomposition_text_sha256": sha_text(
            csv_text(DECOMP_COLUMNS, rows["decomp_rows"])
        ),
        "e_table_sha256": sha_array(e_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    gamma_character = {
        "schema": "long.gchar.modular_character_table@1",
        "status": STATUS if all(checks.values()) else "LONG_GCHAR_MODULAR_TABLE_FAIL",
        "field_prime": FIELD_PRIME,
        "split_seed": SPLIT_SEED,
        "class_count": CLASS_COUNT,
        "irrep_count": CLASS_COUNT,
        "degrees": [int(value) for value in data["degrees"].tolist()],
        "degree_square_sum": obs["degree_square_sum"],
        "character_table_sha256": witness["character_table_sha256"],
        "ordinary_character_claim_flag": 0,
        "note": (
            "This is an exact split modular diagonalization of the Gamma class "
            "algebra over F_10007. Complex character-field reconstruction is "
            "not claimed here."
        ),
    }
    report = {
        "schema": "long.gchar.report@1",
        "status": gamma_character["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_gchar certifies an exact split modular diagonalization of "
            "the Gamma 41-class algebra over F_10007. It emits 41 primitive "
            "idempotents, 41 modular character rows, a degree vector with "
            "square-sum 9216, row orthogonality, central-character homomorphism "
            "checks, and decompositions of the six point-orbit permutation "
            "characters. It does not yet certify complex character-field "
            "reconstruction or E0..E7 decomposition."
        ),
        "stage_protocol": {
            "draft": "read long_b3alg and the Gamma source permutation characters",
            "witness": "emit modular character rows, primitive idempotents, six orbit decompositions, E0..E7 open rows, gaps, and observables",
            "coherence": "check finite-field split roots, idempotents, degrees, orthogonality, homomorphism laws, and permutation-character reconstruction",
            "closure": "certify exact modular diagonalization while keeping ordinary character-field and E0..E7 inputs open",
            "emit": "write long_gchar artifacts and verifier hook",
        },
        "inputs": {
            "long_b3alg": input_entry(
                GAMMA_ALG_REPORT,
                {
                    "status": rows["gamma_alg"].get("status"),
                    "certificate_sha256": rows["gamma_alg"].get("certificate_sha256"),
                },
            ),
            "long_b3mod": input_entry(
                GAMMA_SOURCE_REPORT,
                {
                    "status": rows["gamma_source"].get("status"),
                    "certificate_sha256": rows["gamma_source"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "gamma_alg_tables": input_entry(GAMMA_ALG_TABLES),
            "gamma_permutation_character_csv": input_entry(
                GAMMA_PERMCHAR_CSV,
                {"row_count": len(rows["decomp"]["source_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "gamma_character": relpath(OUT_DIR / "gamma_character.json"),
            "character_csv": relpath(OUT_DIR / "gamma_modular_character_table.csv"),
            "idempotent_csv": relpath(OUT_DIR / "primitive_idempotent.csv"),
            "decomposition_csv": relpath(
                OUT_DIR / "six_orbit_permutation_decomposition.csv"
            ),
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
                "the Gamma class algebra has a 41-root split element over F_10007",
                "41 primitive idempotents are emitted and verified modulo 10007",
                "the modular degree vector has square-sum 9216",
                "the modular character rows satisfy row orthogonality and central-character homomorphism laws",
                "the six point-orbit permutation characters decompose and reconstruct modulo 10007",
            ],
            "does_not_certify_because_open": [
                "complex character-field reconstruction",
                "ordinary character table over algebraic numbers",
                "E0..E7 decomposition",
                "R7 C2 projection",
                "acceptance-basis Krein parameter computation",
            ],
        },
        "next_highest_yield_item": (
            "Supply or derive the E0..E7 Gamma character inputs, then decompose "
            "them against the certified modular character table and feed the "
            "basis into the Krein computation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.gchar.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.gchar.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "gamma_character": gamma_character,
        "character_csv": csv_text(CHAR_COLUMNS, rows["char_rows"]),
        "idempotent_csv": csv_text(IDEMP_COLUMNS, rows["idem_rows"]),
        "decomposition_csv": csv_text(DECOMP_COLUMNS, rows["decomp_rows"]),
        "e_csv": csv_text(E_COLUMNS, rows["e_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "char_table": char_table,
        "idempotent_table": idem_table,
        "decomp_table": decomp_table,
        "e_table": e_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "characters": data["characters"],
        "idempotents": data["idempotents"],
        "central_characters": data["central_characters"],
        "degrees": data["degrees"],
        "roots": data["roots"],
        "weights": data["weights"],
        "charpoly": data["charpoly"],
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
    write_json(OUT_DIR / "gamma_character.json", payloads["gamma_character"])
    (OUT_DIR / "gamma_modular_character_table.csv").write_text(
        payloads["character_csv"], encoding="utf-8"
    )
    (OUT_DIR / "primitive_idempotent.csv").write_text(
        payloads["idempotent_csv"], encoding="utf-8"
    )
    (OUT_DIR / "six_orbit_permutation_decomposition.csv").write_text(
        payloads["decomposition_csv"], encoding="utf-8"
    )
    (OUT_DIR / "balanced_Ei_irrep_decomposition.csv").write_text(
        payloads["e_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        char_table=payloads["char_table"],
        idempotent_table=payloads["idempotent_table"],
        decomp_table=payloads["decomp_table"],
        e_table=payloads["e_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        characters=payloads["characters"],
        idempotents=payloads["idempotents"],
        central_characters=payloads["central_characters"],
        degrees=payloads["degrees"],
        roots=payloads["roots"],
        split_weights=payloads["weights"],
        charpoly=payloads["charpoly"],
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
