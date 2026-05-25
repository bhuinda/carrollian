from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/report.json"
MANIFEST_REL = "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/manifest.json"
SOURCE_REL = (
    "data/invariants/d20/theorems/global_corrected_hidden_split_symmetry/report.json"
)
SOURCE_STATUS = "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
EXPECTED_STATUS = "RAW543_REPO_C2_KERNEL_ACTION_CERTIFIED"
EXPECTED_BASIS_IMAGE_MASKS = [16, 2, 512, 1034, 1, 64, 32, 128, 256, 4, 1024]
EXPECTED_CHARACTER_VECTOR = [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
N = 11


def _load_report() -> dict[str, Any]:
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    cached = cached_core_block("raw543_repo_c2_kernel_action")
    if cached is not None:
        return cached
    raise FileNotFoundError("missing raw543 repo C2 kernel action certificate")


def _load_json_rel(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _mask_from_vector(vector: list[int]) -> int:
    return sum((int(bit) & 1) << idx for idx, bit in enumerate(vector))


def _matrix_rows_from_basis_images(basis_image_masks: list[int]) -> list[list[int]]:
    return [
        [(int(mask) >> row) & 1 for mask in basis_image_masks]
        for row in range(N)
    ]


def _linear_action(basis_image_masks: list[int], x: int) -> int:
    y = 0
    for idx, image in enumerate(basis_image_masks):
        if (x >> idx) & 1:
            y ^= int(image)
    return y


def _rank_masks(vecs: list[int], width: int = N) -> int:
    work = [value for value in vecs if value]
    rank = 0
    for col in range(width):
        pivot = None
        for idx in range(rank, len(work)):
            if (work[idx] >> col) & 1:
                pivot = idx
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for idx in range(len(work)):
            if idx != rank and ((work[idx] >> col) & 1):
                work[idx] ^= work[rank]
        rank += 1
    return rank


def _computed_witness(source: dict[str, Any]) -> dict[str, Any]:
    hidden_split = source["derived"]["hidden_split"]
    symmetry = source["derived"]["symmetry_classification"]
    character_vector = [int(bit) for bit in hidden_split["coefficient_vector_over_f2"]]
    character_mask = _mask_from_vector(character_vector)
    gamma8_mask = int(hidden_split["gamma8_mask"])
    preservers = symmetry["preserving_automorphisms"]
    nontrivial = next(
        row
        for row in preservers
        if row["basis_image_masks"] != [1 << idx for idx in range(N)]
    )
    basis_image_masks = [int(mask) for mask in nontrivial["basis_image_masks"]]
    nilpotent_basis_masks = [
        int(image) ^ (1 << idx) for idx, image in enumerate(basis_image_masks)
    ]

    def tau(x: int) -> int:
        return _linear_action(basis_image_masks, x)

    def nilpotent(x: int) -> int:
        return tau(x) ^ x

    def chi(x: int) -> int:
        return (x & character_mask).bit_count() & 1

    ambient = list(range(1 << N))
    kernel = [x for x in ambient if chi(x) == 0]
    fixed_ambient = [x for x in ambient if tau(x) == x]
    fixed_kernel = [x for x in kernel if tau(x) == x]
    seen: set[int] = set()
    orbits: list[tuple[int, ...]] = []
    for x in kernel:
        if x in seen:
            continue
        orbit = tuple(sorted({x, tau(x)}))
        seen.update(orbit)
        orbits.append(orbit)
    nonzero_orbits = [orbit for orbit in orbits if orbit != (0,)]
    fixed_nonzero_orbits = [orbit for orbit in nonzero_orbits if len(orbit) == 1]
    two_cycle_orbits = [orbit for orbit in nonzero_orbits if len(orbit) == 2]
    orbit_rows = [
        {
            "orbit_id": idx,
            "size": len(orbit),
            "representative": orbit[0],
            "member_a": orbit[0],
            "member_b": orbit[-1],
            "fixed": len(orbit) == 1,
            "nonzero": orbit != (0,),
        }
        for idx, orbit in enumerate(nonzero_orbits)
    ]
    identity_rows = [
        {"identity": "tau_squared_identity", "value": all(tau(tau(x)) == x for x in ambient)},
        {"identity": "N_squared_zero", "value": all(nilpotent(nilpotent(x)) == 0 for x in ambient)},
        {"identity": "hidden_character_preserved", "value": all(chi(tau(x)) == chi(x) for x in ambient)},
        {"identity": "gamma8_fixed", "value": tau(gamma8_mask) == gamma8_mask},
        {"identity": "raw543_burnside", "value": ((2**10 - 1) + (2**6 - 1)) // 2 == 543},
        {"identity": "543_equals_63_plus_480", "value": 543 == 63 + 480},
        {"identity": "543_equals_63_plus_16_times_30", "value": 543 == (2**6 - 1) + 16 * 30},
        {"identity": "543_equals_2pow9_plus_31", "value": 543 == 2**9 + 31},
    ]
    return {
        "automorphism_id": int(nontrivial["automorphism_id"]),
        "basis_image_masks": basis_image_masks,
        "character_vector": character_vector,
        "character_mask": character_mask,
        "gamma8_mask": gamma8_mask,
        "nilpotent_basis_masks": nilpotent_basis_masks,
        "tau_matrix_rows": _matrix_rows_from_basis_images(basis_image_masks),
        "nilpotent_matrix_rows": _matrix_rows_from_basis_images(nilpotent_basis_masks),
        "orbit_rows": orbit_rows,
        "identity_rows": identity_rows,
        "tau_squared_identity": all(tau(tau(x)) == x for x in ambient),
        "hidden_character_preserved": all(chi(tau(x)) == chi(x) for x in ambient),
        "gamma8_fixed": tau(gamma8_mask) == gamma8_mask,
        "N_squared_zero": all(nilpotent(nilpotent(x)) == 0 for x in ambient),
        "rank_on_F2_11": _rank_masks(nilpotent_basis_masks),
        "ambient_fixed_space_size": len(fixed_ambient),
        "ambient_fixed_space_dimension": len(fixed_ambient).bit_length() - 1,
        "kernel_size": len(kernel),
        "kernel_dimension": len(kernel).bit_length() - 1,
        "fixed_kernel_size": len(fixed_kernel),
        "fixed_kernel_dimension": len(fixed_kernel).bit_length() - 1,
        "full_kernel_orbit_count": len(orbits),
        "nonzero_kernel_orbit_count": len(nonzero_orbits),
        "fixed_nonzero_orbits": len(fixed_nonzero_orbits),
        "two_cycle_orbits": len(two_cycle_orbits),
    }


def _read_matrix_csv(rel_path: str) -> list[list[int]]:
    with (ROOT / rel_path).open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != ["row", *[f"e{idx}" for idx in range(N)]]:
            raise AssertionError(f"raw543 matrix CSV header mismatch: {rel_path}")
        rows: list[list[int]] = []
        for expected_idx, row in enumerate(reader):
            if int(row[0]) != expected_idx:
                raise AssertionError(f"raw543 matrix CSV row index mismatch: {rel_path}")
            rows.append([int(value) for value in row[1:]])
    return rows


def _parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise AssertionError(f"raw543 CSV boolean mismatch: {value}")


def _read_orbit_csv(rel_path: str) -> list[dict[str, Any]]:
    with (ROOT / rel_path).open("r", newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            rows.append(
                {
                    "orbit_id": int(row["orbit_id"]),
                    "size": int(row["size"]),
                    "representative": int(row["representative"]),
                    "member_a": int(row["member_a"]),
                    "member_b": int(row["member_b"]),
                    "fixed": _parse_bool(row["fixed"]),
                    "nonzero": _parse_bool(row["nonzero"]),
                }
            )
    return rows


def _read_identity_csv(rel_path: str) -> list[dict[str, Any]]:
    with (ROOT / rel_path).open("r", newline="", encoding="utf-8") as f:
        return [
            {"identity": row["identity"], "value": _parse_bool(row["value"])}
            for row in csv.DictReader(f)
        ]


def _validate_manifest(report: dict[str, Any]) -> None:
    path = ROOT / MANIFEST_REL
    if not path.exists():
        raise FileNotFoundError("missing raw543 repo C2 kernel manifest")
    manifest = _load_json_rel(MANIFEST_REL)
    if manifest.get("status") != EXPECTED_STATUS:
        raise AssertionError("raw543 manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("raw543 manifest report hash mismatch")
    artifacts = manifest.get("artifacts", {})
    expected_artifacts = {
        "report": REPORT_REL,
        "manifest": MANIFEST_REL,
        "tau_matrix": "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_tau_matrix_f2.csv",
        "nilpotent_matrix": "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv",
        "kernel_orbits": "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_kernel_orbits_raw543.csv",
        "identities": "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_raw543_identities.csv",
    }
    if artifacts != expected_artifacts:
        raise AssertionError("raw543 manifest artifact path mismatch")
    hashes = manifest.get("artifact_hashes", {})
    for key, rel_path in expected_artifacts.items():
        if key == "manifest":
            continue
        if key == "report":
            continue
        if h_file(ROOT / rel_path) != hashes.get(key):
            raise AssertionError(f"raw543 manifest artifact hash mismatch: {key}")
    tmp = dict(manifest)
    tmp.pop("manifest_sha256", None)
    if h_json(tmp) != manifest.get("manifest_sha256"):
        raise AssertionError("raw543 manifest self hash mismatch")


def validate_raw543_repo_c2_kernel_action() -> Dict[str, Any]:
    rec = _load_report()
    if rec.get("status") != EXPECTED_STATUS:
        raise AssertionError("raw543 repo C2 kernel action status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("raw543 repo C2 kernel action checks did not pass")

    source_input = rec.get("inputs", {}).get("global_corrected_hidden_split_symmetry_report", {})
    if source_input.get("path") != SOURCE_REL:
        raise AssertionError("raw543 source report path mismatch")
    source_path = ROOT / SOURCE_REL
    if h_file(source_path) != source_input.get("sha256"):
        raise AssertionError("raw543 source report hash mismatch")
    source = _load_json_rel(SOURCE_REL)
    if source.get("status") != SOURCE_STATUS or source.get("all_checks_pass") is not True:
        raise AssertionError("raw543 source report is not certified")

    symmetry = source["derived"]["symmetry_classification"]
    if symmetry.get("preserving_automorphism_count") != 2:
        raise AssertionError("raw543 source stabilizer order mismatch")
    if source["derived"]["hidden_split"].get("coefficient_vector_over_f2") != EXPECTED_CHARACTER_VECTOR:
        raise AssertionError("raw543 source hidden character mismatch")

    witness = _computed_witness(source)
    if witness["basis_image_masks"] != EXPECTED_BASIS_IMAGE_MASKS:
        raise AssertionError("raw543 actual basis-image masks mismatch")
    if witness["character_vector"] != EXPECTED_CHARACTER_VECTOR:
        raise AssertionError("raw543 hidden character vector mismatch")
    expected_scalars = {
        "tau_squared_identity": True,
        "hidden_character_preserved": True,
        "gamma8_fixed": True,
        "N_squared_zero": True,
        "rank_on_F2_11": 4,
        "ambient_fixed_space_size": 128,
        "ambient_fixed_space_dimension": 7,
        "kernel_size": 1024,
        "kernel_dimension": 10,
        "fixed_kernel_size": 64,
        "fixed_kernel_dimension": 6,
        "full_kernel_orbit_count": 544,
        "nonzero_kernel_orbit_count": 543,
        "fixed_nonzero_orbits": 63,
        "two_cycle_orbits": 480,
    }
    for key, expected in expected_scalars.items():
        if witness[key] != expected:
            raise AssertionError(f"raw543 computed {key} mismatch")

    derived = rec.get("derived", {})
    actual = derived.get("actual_nontrivial_c2_preserver", {})
    if actual.get("basis_image_masks") != EXPECTED_BASIS_IMAGE_MASKS:
        raise AssertionError("raw543 report basis-image masks mismatch")
    if actual.get("hidden_character_vector") != EXPECTED_CHARACTER_VECTOR:
        raise AssertionError("raw543 report hidden character mismatch")
    if actual.get("hidden_character_mask") != witness["character_mask"]:
        raise AssertionError("raw543 report hidden character mask mismatch")
    if actual.get("gamma8_mask") != witness["gamma8_mask"]:
        raise AssertionError("raw543 report gamma8 mask mismatch")

    nilpotent = derived.get("nilpotent_part", {})
    if nilpotent.get("basis_image_masks") != witness["nilpotent_basis_masks"]:
        raise AssertionError("raw543 nilpotent basis masks mismatch")
    if nilpotent.get("rank_on_F2_11") != 4:
        raise AssertionError("raw543 nilpotent rank mismatch")

    kernel = derived.get("raw543_kernel", {})
    kernel_expectations = {
        "dimension": 10,
        "size": 1024,
        "nonzero_size": 1023,
        "fixed_space_size": 64,
        "fixed_space_dimension": 6,
        "full_kernel_orbit_count": 544,
        "nonzero_kernel_orbit_count": 543,
        "fixed_nonzero_orbits": 63,
        "two_cycle_orbits": 480,
    }
    for key, expected in kernel_expectations.items():
        if kernel.get(key) != expected:
            raise AssertionError(f"raw543 report kernel {key} mismatch")

    artifacts = derived.get("artifacts", {})
    if artifacts.get("tau_matrix_rows") != witness["tau_matrix_rows"]:
        raise AssertionError("raw543 tau matrix rows mismatch")
    if artifacts.get("nilpotent_matrix_rows") != witness["nilpotent_matrix_rows"]:
        raise AssertionError("raw543 nilpotent matrix rows mismatch")
    if artifacts.get("orbit_rows") != witness["orbit_rows"]:
        raise AssertionError("raw543 orbit rows mismatch")
    if artifacts.get("identity_rows") != witness["identity_rows"]:
        raise AssertionError("raw543 identity rows mismatch")
    for key, rows_key in {
        "tau_matrix_sha256": "tau_matrix_rows",
        "nilpotent_matrix_sha256": "nilpotent_matrix_rows",
        "orbit_rows_sha256": "orbit_rows",
        "identity_rows_sha256": "identity_rows",
    }.items():
        if artifacts.get(key) != h_json(artifacts.get(rows_key)):
            raise AssertionError(f"raw543 artifact JSON hash mismatch: {key}")

    if _read_matrix_csv(
        "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_tau_matrix_f2.csv"
    ) != witness["tau_matrix_rows"]:
        raise AssertionError("raw543 tau matrix CSV mismatch")
    if _read_matrix_csv(
        "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv"
    ) != witness["nilpotent_matrix_rows"]:
        raise AssertionError("raw543 nilpotent matrix CSV mismatch")
    if _read_orbit_csv(
        "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_kernel_orbits_raw543.csv"
    ) != witness["orbit_rows"]:
        raise AssertionError("raw543 orbit CSV mismatch")
    if _read_identity_csv(
        "data/invariants/d20/theorems/raw543_repo_c2_kernel_action/actual_c2_raw543_identities.csv"
    ) != witness["identity_rows"]:
        raise AssertionError("raw543 identity CSV mismatch")

    checks = rec.get("checks", {})
    for key, value in checks.items():
        if value is not True:
            raise AssertionError(f"raw543 report check failed: {key}")
    if not all(row.get("value") is True for row in witness["identity_rows"]):
        raise AssertionError("raw543 identity witness row failed")

    _validate_manifest(rec)
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != rec.get("certificate_sha256"):
        raise AssertionError("raw543 repo C2 kernel action self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_raw543_repo_c2_kernel_action()
    print(rec["status"])
    print(rec["certificate_sha256"])
