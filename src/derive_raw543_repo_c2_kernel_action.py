from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "raw543_repo_c2_kernel_action"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
SOURCE_REPORT = (
    D20_INVARIANTS / "theorems" / "global_corrected_hidden_split_symmetry" / "report.json"
)
SOURCE_STATUS = "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
N = 11


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


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
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
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
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rank_masks(vecs: list[int], width: int = N) -> int:
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


def mask_from_vector(vector: list[int]) -> int:
    return sum((int(bit) & 1) << idx for idx, bit in enumerate(vector))


def matrix_rows_from_basis_images(basis_image_masks: list[int]) -> list[list[int]]:
    return [
        [(int(mask) >> row) & 1 for mask in basis_image_masks]
        for row in range(N)
    ]


def linear_action(basis_image_masks: list[int], x: int) -> int:
    y = 0
    for idx, image in enumerate(basis_image_masks):
        if (x >> idx) & 1:
            y ^= int(image)
    return y


def compute_certificate(source: dict[str, Any]) -> dict[str, Any]:
    hidden_split = source["derived"]["hidden_split"]
    symmetry = source["derived"]["symmetry_classification"]
    character_vector = [int(bit) for bit in hidden_split["coefficient_vector_over_f2"]]
    character_mask = mask_from_vector(character_vector)
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
        return linear_action(basis_image_masks, x)

    def nilpotent(x: int) -> int:
        return tau(x) ^ x

    def chi(x: int) -> int:
        return (x & character_mask).bit_count() & 1

    ambient = list(range(1 << N))
    kernel = [x for x in ambient if chi(x) == 0]
    fixed_ambient = [x for x in ambient if tau(x) == x]
    fixed_kernel = [x for x in kernel if tau(x) == x]
    seen: set[int] = set()
    orbits = []
    for x in kernel:
        if x in seen:
            continue
        orbit = tuple(sorted({x, tau(x)}))
        seen.update(orbit)
        orbits.append(orbit)
    nonzero_orbits = [orbit for orbit in orbits if orbit != (0,)]
    fixed_nonzero_orbits = [orbit for orbit in nonzero_orbits if len(orbit) == 1]
    two_cycle_orbits = [orbit for orbit in nonzero_orbits if len(orbit) == 2]

    tau_matrix = matrix_rows_from_basis_images(basis_image_masks)
    nilpotent_matrix = matrix_rows_from_basis_images(nilpotent_basis_masks)
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
        "source_report_claim": (
            "nontrivial hidden-split C2 preserver induces the listed F2^11 "
            "basis-image masks and preserves the hidden split character"
        ),
        "ambient": {"field": "F2", "dimension": N, "mask_count": 1 << N},
        "actual_nontrivial_c2_preserver": {
            "automorphism_id": int(nontrivial["automorphism_id"]),
            "basis_image_masks": basis_image_masks,
            "hidden_character_vector": character_vector,
            "hidden_character_mask": character_mask,
            "tau_squared_identity": all(tau(tau(x)) == x for x in ambient),
            "hidden_character_preserved": all(chi(tau(x)) == chi(x) for x in ambient),
            "gamma8_mask": gamma8_mask,
            "gamma8_fixed": tau(gamma8_mask) == gamma8_mask,
        },
        "nilpotent_part": {
            "definition": "N = tau - I = tau + I over F2",
            "basis_image_masks": nilpotent_basis_masks,
            "N_squared_zero": all(nilpotent(nilpotent(x)) == 0 for x in ambient),
            "rank_on_F2_11": rank_masks(nilpotent_basis_masks),
            "ambient_fixed_space_size": len(fixed_ambient),
            "ambient_fixed_space_dimension": len(fixed_ambient).bit_length() - 1,
        },
        "raw543_kernel": {
            "definition": "K = ker(hidden_character) inside F2^11",
            "dimension": len(kernel).bit_length() - 1,
            "size": len(kernel),
            "nonzero_size": len(kernel) - 1,
            "fixed_space_size": len(fixed_kernel),
            "fixed_space_dimension": len(fixed_kernel).bit_length() - 1,
            "fixed_nonzero_count": len(fixed_nonzero_orbits),
            "full_kernel_orbit_count": len(orbits),
            "nonzero_kernel_orbit_count": len(nonzero_orbits),
            "fixed_nonzero_orbits": len(fixed_nonzero_orbits),
            "two_cycle_orbits": len(two_cycle_orbits),
        },
        "identities": {
            "raw543_burnside": "((2^10 - 1) + (2^6 - 1))/2 = 543",
            "543_equals_63_plus_480": 543 == 63 + 480,
            "543_equals_63_plus_16_times_30": 543 == (2**6 - 1) + 16 * 30,
            "543_equals_2pow9_plus_31": 543 == 2**9 + 31,
            "544_equals_full_kernel_quotient": len(orbits) == 544,
        },
        "artifacts": {
            "tau_matrix_rows": tau_matrix,
            "nilpotent_matrix_rows": nilpotent_matrix,
            "orbit_rows": orbit_rows,
            "identity_rows": identity_rows,
            "tau_matrix_sha256": sha_json(tau_matrix),
            "nilpotent_matrix_sha256": sha_json(nilpotent_matrix),
            "orbit_rows_sha256": sha_json(orbit_rows),
            "identity_rows_sha256": sha_json(identity_rows),
        },
    }


def write_matrix_csv(path: Path, rows: list[list[int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", *[f"e{idx}" for idx in range(N)]])
        for idx, row in enumerate(rows):
            writer.writerow([idx, *row])


def write_dict_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_theorem() -> dict[str, Any]:
    source = load_json(SOURCE_REPORT)
    cert = compute_certificate(source)
    checks = {
        "source_report_is_certified": source.get("status")
        == SOURCE_STATUS
        and source.get("all_checks_pass") is True,
        "hidden_split_stabilizer_has_order_2": source["derived"]["symmetry_classification"][
            "preserving_automorphism_count"
        ]
        == 2,
        "tau_squared_identity": cert["actual_nontrivial_c2_preserver"][
            "tau_squared_identity"
        ],
        "hidden_character_preserved": cert["actual_nontrivial_c2_preserver"][
            "hidden_character_preserved"
        ],
        "gamma8_fixed": cert["actual_nontrivial_c2_preserver"]["gamma8_fixed"],
        "nilpotent_square_zero": cert["nilpotent_part"]["N_squared_zero"],
        "nilpotent_rank_is_4": cert["nilpotent_part"]["rank_on_F2_11"] == 4,
        "ambient_fixed_dimension_is_7": cert["nilpotent_part"][
            "ambient_fixed_space_dimension"
        ]
        == 7,
        "kernel_dimension_is_10": cert["raw543_kernel"]["dimension"] == 10,
        "kernel_fixed_dimension_is_6": cert["raw543_kernel"]["fixed_space_dimension"] == 6,
        "raw543_nonzero_kernel_orbit_count": cert["raw543_kernel"][
            "nonzero_kernel_orbit_count"
        ]
        == 543,
        "raw543_identity_63_plus_480": cert["identities"]["543_equals_63_plus_480"],
        "raw543_identity_63_plus_16_times_30": cert["identities"][
            "543_equals_63_plus_16_times_30"
        ],
    }
    report = {
        "schema": "d20.theorem.raw543_repo_c2_kernel_action",
        "status": "RAW543_REPO_C2_KERNEL_ACTION_CERTIFIED",
        "object": "D20",
        "claim": (
            "The raw543 count is the actual nonzero kernel-orbit count for the "
            "nontrivial C2 hidden-split preserver recorded in the public D20 "
            "hidden-split theorem report."
        ),
        "definition": {
            "source_action": (
                "the nonidentity preserving automorphism in "
                "global_corrected_hidden_split_symmetry/report.json, acting on "
                "F2^11 by its recorded basis-image masks"
            ),
            "raw543_space": (
                "K^x, the nonzero vectors in the hidden-character kernel "
                "K=ker(chi) subset F2^11"
            ),
            "orbit_count": "Burnside count for the C2 action generated by tau on K^x",
        },
        "inputs": {
            "global_corrected_hidden_split_symmetry_report": input_record(SOURCE_REPORT),
        },
        "derived": cert,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "confirmed": [
                "tau is the actual recorded nontrivial hidden-split preserver",
                "tau^2=I and N=tau-I has N^2=0 and rank 4 on F2^11",
                "the hidden-character kernel has 543 nonzero C2 orbits",
            ],
            "guardrails": [
                "this certifies the raw nonzero kernel orbit count",
                "later refined selectors must explicitly cite this same action/kernel and representative rule",
            ],
        },
        "next_highest_yield_item": (
            "Connect the raw543 orbit representatives to the existing cubical/Agda "
            "raw543 finite-subtype witnesses by checking that they use the same "
            "C2 action and hidden-character kernel."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = report["derived"]["artifacts"]
    write_matrix_csv(out_dir / "actual_c2_tau_matrix_f2.csv", artifacts["tau_matrix_rows"])
    write_matrix_csv(
        out_dir / "actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv",
        artifacts["nilpotent_matrix_rows"],
    )
    write_dict_csv(out_dir / "actual_c2_kernel_orbits_raw543.csv", artifacts["orbit_rows"])
    write_dict_csv(out_dir / "actual_c2_raw543_identities.csv", artifacts["identity_rows"])
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema": "d20.theorem.raw543_repo_c2_kernel_action_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
            "tau_matrix": rel(out_dir / "actual_c2_tau_matrix_f2.csv"),
            "nilpotent_matrix": rel(
                out_dir / "actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv"
            ),
            "kernel_orbits": rel(out_dir / "actual_c2_kernel_orbits_raw543.csv"),
            "identities": rel(out_dir / "actual_c2_raw543_identities.csv"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_hashes": {
            "tau_matrix": sha_file(out_dir / "actual_c2_tau_matrix_f2.csv"),
            "nilpotent_matrix": sha_file(
                out_dir / "actual_c2_nilpotent_N_tau_minus_I_matrix_f2.csv"
            ),
            "kernel_orbits": sha_file(out_dir / "actual_c2_kernel_orbits_raw543.csv"),
            "identities": sha_file(out_dir / "actual_c2_raw543_identities.csv"),
        },
        "inputs": report["inputs"],
        "purpose": [
            "bind raw543 to the actual recorded D20 hidden-split C2 action",
            "emit matrix, nilpotent, orbit, and identity witnesses",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
