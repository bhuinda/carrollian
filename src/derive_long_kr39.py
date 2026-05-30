from __future__ import annotations

import csv
import hashlib
import json
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


THEOREM_ID = "long_kr39"
STATUS = "LONG_KR39_DIRECT_SECTOR_HADAMARD_SCREEN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

FIELD_PRIME = 1_000_003
TARGET_MOD = (135 * pow(2, -1, FIELD_PRIME)) % FIELD_PRIME

LONG_KREIN = PROOF_ROOT / "long_krein" / "report.json"
CENTRAL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_orbital_central_idempotents"
    / "report.json"
)
CENTRAL_NPZ = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_orbital_central_idempotents"
    / "a985_center_and_primitive_central_idempotents.npz"
)
CENTRAL_TABLE = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_orbital_central_idempotents"
    / "primitive_central_idempotent_table.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_kr39.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_kr39.py"

PAIR_COLUMNS = [
    "pair_id",
    "i",
    "j",
    "product_support",
    "zero_product_flag",
    "closed_in_sector_span_flag",
    "projection_nonzero_coeff_count",
    "projection_coeff_2_mod",
    "accepted_coeff_2_mod",
    "accepted_coeff_2_valid_flag",
    "target_pair_flag",
    "target_expected_mod",
    "target_135_over_2_verified_flag",
]
TARGET_COLUMNS = [
    "target_id",
    "i",
    "j",
    "k",
    "product_support",
    "zero_product_flag",
    "closed_in_sector_span_flag",
    "projection_coeff_k_mod",
    "accepted_coeff_k_mod",
    "accepted_coeff_k_valid_flag",
    "expected_numerator",
    "expected_denominator",
    "expected_mod",
    "direct_sector_target_verified_flag",
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
    "central_idempotent_input",
    "direct_sector_hadamard_screen",
    "direct_sector_target_mismatch",
    "eight_module_decomposition_missing",
    "krein_acceptance_closure",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "field_prime",
    "sector_count",
    "relation_count",
    "pair_count",
    "closed_pair_count",
    "not_closed_pair_count",
    "zero_product_pair_count",
    "nonzero_product_pair_count",
    "target_pair_count",
    "target_closed_pair_count",
    "target_zero_product_pair_count",
    "target_verified_135_over_2_count",
    "target_projection_coeff_2_nonzero_count",
    "sector5_support",
    "sector6_support",
    "sector5_sector6_overlap",
    "direct_label_mismatch_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

TARGETS = [(5, 5, 2), (5, 6, 2), (6, 5, 2), (6, 6, 2)]


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def inv_mod_matrix(matrix: np.ndarray, prime: int) -> np.ndarray:
    n = int(matrix.shape[0])
    if matrix.shape != (n, n):
        raise AssertionError("matrix inverse requires a square matrix")
    aug = np.concatenate(
        [matrix.astype(np.int64) % prime, np.eye(n, dtype=np.int64)], axis=1
    )
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if int(aug[row, col]) % prime:
                pivot = row
                break
        if pivot is None:
            raise AssertionError("coordinate matrix is singular")
        if pivot != col:
            aug[[col, pivot]] = aug[[pivot, col]]
        inv = pow(int(aug[col, col]), -1, prime)
        aug[col, :] = (aug[col, :] * inv) % prime
        for row in range(n):
            if row != col and int(aug[row, col]) % prime:
                aug[row, :] = (aug[row, :] - int(aug[row, col]) * aug[col, :]) % prime
    return aug[:, n:]


def load_central_arrays() -> dict[str, np.ndarray]:
    with np.load(CENTRAL_NPZ, allow_pickle=False) as payload:
        return {key: np.asarray(payload[key], dtype=np.int64) for key in payload.files}


def build_rows() -> dict[str, Any]:
    long_krein = load_json(LONG_KREIN)
    central_report = load_json(CENTRAL_REPORT)
    _, central_table_rows = read_csv_rows(CENTRAL_TABLE)
    arrays = load_central_arrays()
    idempotents = arrays["idempotents"] % FIELD_PRIME
    coord_cols = arrays["coord_cols"].astype(np.int64)
    sector_count, relation_count = idempotents.shape
    coord_matrix = idempotents[:, coord_cols] % FIELD_PRIME
    coord_inv = inv_mod_matrix(coord_matrix, FIELD_PRIME)
    targets = {(i, j): k for i, j, k in TARGETS}

    pair_rows = []
    target_rows = []
    pair_id = 0
    for i in range(sector_count):
        for j in range(sector_count):
            product = (idempotents[i] * idempotents[j]) % FIELD_PRIME
            product_support = int(np.count_nonzero(product))
            coeff = (product[coord_cols] @ coord_inv) % FIELD_PRIME
            recon = (coeff @ idempotents) % FIELD_PRIME
            closed = int(np.array_equal(recon, product))
            projection_coeff_2 = int(coeff[2])
            accepted_coeff_2 = projection_coeff_2 if closed else -1
            target_pair_flag = int((i, j) in targets)
            target_verified = int(
                target_pair_flag == 1
                and closed == 1
                and accepted_coeff_2 == TARGET_MOD
            )
            pair_rows.append(
                {
                    "pair_id": pair_id,
                    "i": i,
                    "j": j,
                    "product_support": product_support,
                    "zero_product_flag": int(product_support == 0),
                    "closed_in_sector_span_flag": closed,
                    "projection_nonzero_coeff_count": int(np.count_nonzero(coeff)),
                    "projection_coeff_2_mod": projection_coeff_2,
                    "accepted_coeff_2_mod": accepted_coeff_2,
                    "accepted_coeff_2_valid_flag": closed,
                    "target_pair_flag": target_pair_flag,
                    "target_expected_mod": TARGET_MOD if target_pair_flag else -1,
                    "target_135_over_2_verified_flag": target_verified,
                }
            )
            if target_pair_flag:
                k = targets[(i, j)]
                accepted_coeff_k = int(coeff[k]) if closed else -1
                target_rows.append(
                    {
                        "target_id": len(target_rows),
                        "i": i,
                        "j": j,
                        "k": k,
                        "product_support": product_support,
                        "zero_product_flag": int(product_support == 0),
                        "closed_in_sector_span_flag": closed,
                        "projection_coeff_k_mod": int(coeff[k]),
                        "accepted_coeff_k_mod": accepted_coeff_k,
                        "accepted_coeff_k_valid_flag": closed,
                        "expected_numerator": 135,
                        "expected_denominator": 2,
                        "expected_mod": TARGET_MOD,
                        "direct_sector_target_verified_flag": int(
                            closed == 1 and accepted_coeff_k == TARGET_MOD
                        ),
                    }
                )
            pair_id += 1

    sector5_support = int(np.count_nonzero(idempotents[5]))
    sector6_support = int(np.count_nonzero(idempotents[6]))
    sector5_sector6_overlap = int(
        np.count_nonzero((idempotents[5] != 0) & (idempotents[6] != 0))
    )
    obs = {
        "field_prime": FIELD_PRIME,
        "sector_count": sector_count,
        "relation_count": relation_count,
        "pair_count": len(pair_rows),
        "closed_pair_count": sum(row["closed_in_sector_span_flag"] for row in pair_rows),
        "not_closed_pair_count": sum(
            int(row["closed_in_sector_span_flag"] == 0) for row in pair_rows
        ),
        "zero_product_pair_count": sum(row["zero_product_flag"] for row in pair_rows),
        "nonzero_product_pair_count": sum(
            int(row["zero_product_flag"] == 0) for row in pair_rows
        ),
        "target_pair_count": len(target_rows),
        "target_closed_pair_count": sum(
            row["closed_in_sector_span_flag"] for row in target_rows
        ),
        "target_zero_product_pair_count": sum(
            row["zero_product_flag"] for row in target_rows
        ),
        "target_verified_135_over_2_count": sum(
            row["direct_sector_target_verified_flag"] for row in target_rows
        ),
        "target_projection_coeff_2_nonzero_count": sum(
            int(row["projection_coeff_k_mod"] != 0) for row in target_rows
        ),
        "sector5_support": sector5_support,
        "sector6_support": sector6_support,
        "sector5_sector6_overlap": sector5_sector6_overlap,
        "direct_label_mismatch_flag": 1,
        "next_gap_code": GAP_CODES["eight_module_decomposition_missing"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["central_idempotent_input"],
            "gap_code": GAP_CODES["central_idempotent_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["direct_sector_hadamard_screen"],
            "gap_code": GAP_CODES["direct_sector_hadamard_screen"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["direct_sector_target_mismatch"],
            "gap_code": GAP_CODES["direct_sector_target_mismatch"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["eight_module_decomposition_missing"],
            "gap_code": GAP_CODES["eight_module_decomposition_missing"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["krein_acceptance_closure"],
            "gap_code": GAP_CODES["krein_acceptance_closure"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "long_krein": long_krein,
        "central_report": central_report,
        "central_table_rows": central_table_rows,
        "idempotents": idempotents,
        "coord_cols": coord_cols,
        "pair_rows": pair_rows,
        "target_rows": target_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    target_table = table_from_rows(TARGET_COLUMNS, rows["target_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "inputs_checked": rows["long_krein"].get("all_checks_pass") is True
        and certified(rows["central_report"]),
        "central_idempotent_shape_exact": obs["field_prime"] == FIELD_PRIME
        and obs["sector_count"] == 39
        and obs["relation_count"] == 985
        and len(rows["central_table_rows"]) == 39,
        "complete_pair_screen_shape": obs["pair_count"] == 1_521
        and obs["closed_pair_count"] == 402
        and obs["not_closed_pair_count"] == 1_119
        and obs["zero_product_pair_count"] == 370
        and obs["nonzero_product_pair_count"] == 1_151,
        "direct_target_rows_mismatch": obs["target_pair_count"] == 4
        and obs["target_closed_pair_count"] == 2
        and obs["target_zero_product_pair_count"] == 2
        and obs["target_verified_135_over_2_count"] == 0
        and obs["target_projection_coeff_2_nonzero_count"] == 0
        and obs["direct_label_mismatch_flag"] == 1,
        "sector5_sector6_disjoint": obs["sector5_support"] == 12
        and obs["sector6_support"] == 133
        and obs["sector5_sector6_overlap"] == 0,
        "table_shapes_match": pair_table.shape == (1_521, len(PAIR_COLUMNS))
        and target_table.shape == (4, len(TARGET_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "direct_a985_sector_hadamard_screen",
        "summary": {
            "sector_count": obs["sector_count"],
            "relation_count": obs["relation_count"],
            "pair_count": obs["pair_count"],
            "closed_pair_count": obs["closed_pair_count"],
            "not_closed_pair_count": obs["not_closed_pair_count"],
            "target_pair_count": obs["target_pair_count"],
            "target_verified_135_over_2_count": obs[
                "target_verified_135_over_2_count"
            ],
            "sector5_support": obs["sector5_support"],
            "sector6_support": obs["sector6_support"],
            "sector5_sector6_overlap": obs["sector5_sector6_overlap"],
            "next_gap_code": obs["next_gap_code"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "target_mod": TARGET_MOD,
        "idempotent_table_sha256": sha_array(rows["idempotents"]),
        "pair_table_sha256": sha_array(pair_table),
        "pair_text_sha256": sha_text(csv_text(PAIR_COLUMNS, rows["pair_rows"])),
        "target_table_sha256": sha_array(target_table),
        "target_text_sha256": sha_text(
            csv_text(TARGET_COLUMNS, rows["target_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    kr39 = {
        "schema": "long.kr39@1",
        "object": "direct_a985_sector_hadamard_screen",
        "status": STATUS if all(checks.values()) else "LONG_KR39_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.kr39.report@1",
        "status": kr39["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_kr39 certifies that the handoff Krein target rows cannot be "
            "read as direct canonical A985 sector labels. The complete 39 by "
            "39 coordinatewise product screen has 402 pairs closed in the "
            "central-sector span and 1119 pairs outside it. For raw sector "
            "labels 5 and 6, the four requested k=2 target rows verify zero "
            "times against 135/2; sectors 5 and 6 are disjoint, and the mixed "
            "products are zero."
        ),
        "stage_protocol": {
            "draft": "read long_krein and the canonical A985 central-idempotent certificate",
            "witness": "emit the 1521-pair direct sector Hadamard screen, four target rows, gaps, and observables",
            "coherence": "check closure counts, target-row coefficients, sector 5/6 supports, and table hashes",
            "closure": "certify direct A985 sector labels are not the E5/E6 labels needed for the handoff Krein target",
            "emit": "write long_kr39 artifacts and verifier hook",
        },
        "inputs": {
            "long_krein": input_entry(
                LONG_KREIN,
                {
                    "status": rows["long_krein"].get("status"),
                    "certificate_sha256": rows["long_krein"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "central_report": input_entry(
                CENTRAL_REPORT,
                {
                    "status": rows["central_report"].get("status"),
                    "certificate_sha256": rows["central_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "central_npz": input_entry(
                CENTRAL_NPZ,
                {
                    "sector_count": obs["sector_count"],
                    "relation_count": obs["relation_count"],
                },
            ),
            "central_table": input_entry(
                CENTRAL_TABLE,
                {"row_count": len(rows["central_table_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "kr39": relpath(OUT_DIR / "kr39.json"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "target_csv": relpath(OUT_DIR / "target.csv"),
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
                "the direct 39-sector A985 Hadamard screen covers all 1521 ordered sector pairs",
                "402 ordered pairs close in the direct central-sector span and 1119 do not",
                "raw A985 sectors 5 and 6 are disjoint under coordinatewise support",
                "the direct raw-sector readings of q_55^2, q_56^2, q_65^2, and q_66^2 do not verify the 135/2 target",
                "the handoff E5/E6 labels require a separate eight-module acceptance decomposition rather than raw A985 sector ids",
            ],
            "does_not_certify_because_open": [
                "the widetilde B3 character table",
                "the E0..E7 module decomposition",
                "all Krein parameters in the acceptance scaffold",
                "the four 135/2 target rows under the correct E-label basis",
                "any denominator-clearing cover or acceptance-ladder closure",
            ],
        },
        "next_highest_yield_item": (
            "Materialize the widetilde B3 character table and E0..E7 module "
            "decomposition, then compute the Krein table in that acceptance "
            "basis instead of the raw A985 sector-label basis."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.kr39.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.kr39.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "kr39": kr39,
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "target_csv": csv_text(TARGET_COLUMNS, rows["target_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pair_table": pair_table,
        "target_table": target_table,
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
    write_json(OUT_DIR / "kr39.json", payloads["kr39"])
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "target.csv").write_text(payloads["target_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pair_table=payloads["pair_table"],
        target_table=payloads["target_table"],
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
