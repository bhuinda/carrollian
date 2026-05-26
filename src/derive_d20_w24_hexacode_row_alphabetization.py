from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from itertools import product
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_w24_hexacode_row_alphabetization"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_w24_hexacode_row_alphabetization.json"

MOG_RESOLVENT = ROOT / "data" / "selectors" / "mog_resolvent_invariant.json"
MOG_CANONICITY = ROOT / "data" / "selectors" / "mog_canonicity_boundary.json"
FULL_ROW_REFINED_OBSTRUCTION = ROOT / "data" / "selectors" / "full_row_refined_obstruction.json"
HEXACODE_ROW_SELECTOR = ROOT / "data" / "selectors" / "hexacode_row_selector.json"
WU_SPINH_6J_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"
ALPHABETIZED_FINITENESS = (
    D20_INVARIANTS / "proof_obligations" / "d20_alphabetized_golay_finiteness" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_w24_hexacode_row_alphabetization.py"
VALIDATOR = ROOT / "src" / "certify_d20_w24_hexacode_row_alphabetization.py"

TARGET_GOLAY_HISTOGRAM = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
ROW_F4_LABELS = [0, 1, 2, 3]
ROW_F4_NAMES = {0: "0", 1: "1", 2: "omega", 3: "omega+1"}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def f4_mul(a: int, b: int) -> int:
    a0, a1 = a & 1, (a >> 1) & 1
    b0, b1 = b & 1, (b >> 1) & 1
    c0 = (a0 & b0) ^ (a1 & b1)
    c1 = (a0 & b1) ^ (a1 & b0) ^ (a1 & b1)
    return c0 | (c1 << 1)


def hexacode_words(generator: list[list[int]]) -> list[tuple[int, ...]]:
    words: set[tuple[int, ...]] = set()
    for coeffs in product(range(4), repeat=len(generator)):
        word = []
        for col in range(len(generator[0])):
            symbol = 0
            for coeff, row in zip(coeffs, generator):
                symbol ^= f4_mul(coeff, int(row[col]))
            word.append(symbol)
        words.add(tuple(word))
    return sorted(words)


def row_symbol(mask: int) -> int:
    symbol = 0
    for row, label in enumerate(ROW_F4_LABELS):
        if (mask >> row) & 1:
            symbol ^= label
    return symbol


def local_lift_table() -> dict[tuple[int, int], list[int]]:
    table: dict[tuple[int, int], list[int]] = {}
    for parity in (0, 1):
        for symbol in range(4):
            options = [
                mask
                for mask in range(16)
                if mask.bit_count() % 2 == parity and row_symbol(mask) == symbol
            ]
            if len(options) != 2:
                raise ValueError(f"expected two local lifts for parity={parity}, symbol={symbol}")
            table[(parity, symbol)] = sorted(options)
    return table


def mask_to_rows(mask: int) -> list[int]:
    return [row for row in range(4) if (mask >> row) & 1]


def build_binary_code(
    grid: list[list[int]],
    words: list[tuple[int, ...]],
) -> tuple[list[int], dict[str, Any]]:
    local = local_lift_table()
    code: set[int] = set()
    per_parity_count = Counter()
    symbol_word_multiplicity: dict[int, Counter[tuple[int, ...]]] = {0: Counter(), 1: Counter()}
    for word in words:
        for parity in (0, 1):
            local_options = [local[(parity, symbol)] for symbol in word]
            for choice_bits in product((0, 1), repeat=6):
                if sum(choice_bits) % 2 != parity:
                    continue
                mask = 0
                for col, choice_bit in enumerate(choice_bits):
                    local_mask = local_options[col][choice_bit]
                    for row in mask_to_rows(local_mask):
                        mask |= 1 << int(grid[row][col])
                code.add(mask)
                per_parity_count[parity] += 1
                symbol_word_multiplicity[parity][word] += 1
    diagnostics = {
        "column_parity_word_counts": {
            "even": per_parity_count[0],
            "odd": per_parity_count[1],
        },
        "symbol_word_multiplicity_histogram": {
            "even": dict(sorted(Counter(symbol_word_multiplicity[0].values()).items())),
            "odd": dict(sorted(Counter(symbol_word_multiplicity[1].values()).items())),
        },
    }
    return sorted(code), diagnostics


def rank_masks(masks: list[int], width: int = 24) -> int:
    basis = [0 for _ in range(width)]
    rank = 0
    for raw in masks:
        value = raw
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def basis_masks(masks: list[int], width: int = 24) -> list[int]:
    basis = [0 for _ in range(width)]
    for raw in masks:
        value = raw
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return [value for value in basis if value]


def mask_to_vector(mask: int, width: int = 24) -> list[int]:
    return [(mask >> idx) & 1 for idx in range(width)]


def weight_histogram(masks: list[int]) -> dict[int, int]:
    return dict(sorted(Counter(mask.bit_count() for mask in masks).items()))


def self_orthogonal(masks: list[int]) -> bool:
    basis = basis_masks(masks)
    for idx, left in enumerate(basis):
        for right in basis[idx:]:
            if (left & right).bit_count() % 2:
                return False
    return True


def span_masks(gens: list[int]) -> list[int]:
    out = {0}
    for gen in gens:
        out |= {word ^ gen for word in list(out)}
    return sorted(out)


def column_mask(grid: list[list[int]], col: int) -> int:
    mask = 0
    for row in range(4):
        mask |= 1 << int(grid[row][col])
    return mask


def row_mask(grid: list[list[int]], row: int) -> int:
    mask = 0
    for col in range(6):
        mask |= 1 << int(grid[row][col])
    return mask


def build_artifact() -> dict[str, Any]:
    mog = load_json(MOG_RESOLVENT)
    canonicity = load_json(MOG_CANONICITY)
    row_obstruction = load_json(FULL_ROW_REFINED_OBSTRUCTION)
    hexacode = load_json(HEXACODE_ROW_SELECTOR)
    wu = load_json(WU_SPINH_6J_MARKING)
    finiteness = load_json(ALPHABETIZED_FINITENESS)

    grid = mog["mog_frame"]["grid_row_major"]
    h6_labels = mog["inputs"]["H6_labels"]
    generator = hexacode["hexacode"]["f4_generator_3x6"]
    h_words = hexacode_words(generator)
    code, generation_diagnostics = build_binary_code(grid, h_words)
    code_set = set(code)
    basis = basis_masks(code)
    hist = weight_histogram(code)
    dodecads = [mask for mask in code if mask.bit_count() == 12]
    local = local_lift_table()

    columns = [column_mask(grid, col) for col in range(6)]
    column_pair_generators = [
        columns[left] ^ columns[right] for left in range(6) for right in range(left + 1, 6)
    ]
    column_pair_words = span_masks(column_pair_generators)
    rows = [row_mask(grid, row) for row in range(4)]
    row_pairs = [rows[left] ^ rows[right] for left in range(4) for right in range(left + 1, 4)]
    active_edge_pairs = mog["tetrahedral_6j_frame"]["tetrahedron_edge_column_pairs"]
    active_edge_words = [columns[left] ^ columns[right] for left, right in active_edge_pairs]
    active_edge_code = span_masks(active_edge_words)
    wu_octad = sum(1 << int(coord) for coord in wu["wu_spinh_marking"]["radical_octad_support"])

    row_alphabetization = {
        "grid_row_major": grid,
        "column_labels": h6_labels,
        "row_f4_labels": [
            {"row": row, "f4_value": value, "f4_label": ROW_F4_NAMES[value]}
            for row, value in enumerate(ROW_F4_LABELS)
        ],
        "coordinate_labels": [
            {
                "coordinate": int(grid[row][col]),
                "mog_row": row,
                "mog_column": col,
                "column_label": h6_labels[col],
                "row_f4_value": ROW_F4_LABELS[row],
                "row_f4_label": ROW_F4_NAMES[ROW_F4_LABELS[row]],
            }
            for row in range(4)
            for col in range(6)
        ],
    }
    local_table_json = [
        {
            "uniform_column_parity": parity,
            "f4_symbol": symbol,
            "f4_label": ROW_F4_NAMES[symbol],
            "choice_0_rows": mask_to_rows(options[0]),
            "choice_1_rows": mask_to_rows(options[1]),
            "choice_0_local_mask": options[0],
            "choice_1_local_mask": options[1],
        }
        for (parity, symbol), options in sorted(local.items())
    ]
    checks = {
        "alphabetized_finiteness_input_certified": finiteness["status"]
        == "D20_ALPHABETIZED_GOLAY_FINITENESS_CERTIFIED",
        "row_selector_endpoint_input_certified": hexacode["status"]
        == "HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL",
        "mog_grid_is_4_by_6": mog["mog_frame"]["grid_shape"] == [4, 6],
        "row_f4_alphabet_has_four_symbols": ROW_F4_LABELS == [0, 1, 2, 3],
        "hexacode_has_64_words": len(h_words) == 64,
        "hexacode_f4_weight_histogram_matches": weight_histogram(
            [sum(1 << idx for idx, symbol in enumerate(word) if symbol) for word in h_words]
        )
        == {0: 1, 4: 45, 6: 18},
        "local_lift_table_has_two_choices_per_parity_symbol": all(
            len(options) == 2 for options in local.values()
        )
        and len(local) == 8,
        "global_choice_rule_yields_4096_unique_words": len(code) == 4096,
        "uniform_column_parity_counts_are_2048_each": generation_diagnostics[
            "column_parity_word_counts"
        ]
        == {"even": 2048, "odd": 2048},
        "each_hexacode_symbol_word_has_32_lifts_per_uniform_parity": generation_diagnostics[
            "symbol_word_multiplicity_histogram"
        ]
        == {"even": {32: 64}, "odd": {32: 64}},
        "golay_weight_histogram_matches": hist == TARGET_GOLAY_HISTOGRAM,
        "rank_is_12": rank_masks(code) == 12,
        "minimum_nonzero_weight_is_8": min(mask.bit_count() for mask in code if mask) == 8,
        "self_orthogonal": self_orthogonal(code),
        "doubly_even": all(weight % 4 == 0 for weight in hist),
        "self_dual_by_rank_and_self_orthogonal": rank_masks(code) == 12 and self_orthogonal(code),
        "dodecad_count_is_2576": len(dodecads) == 2576,
        "contains_column_pair_code": all(mask in code_set for mask in column_pair_words),
        "column_pair_code_profile_matches": rank_masks(column_pair_words) == 5
        and weight_histogram(column_pair_words) == {0: 1, 8: 15, 16: 15, 24: 1},
        "contains_row_pair_dodecads": all(mask in code_set for mask in row_pairs),
        "does_not_contain_single_rows": all(mask not in code_set for mask in rows),
        "contains_active_6j_edge_code": all(mask in code_set for mask in active_edge_code),
        "active_6j_edge_code_profile_matches": rank_masks(active_edge_code) == 3
        and weight_histogram(active_edge_code) == {0: 1, 8: 6, 16: 1},
        "contains_wu_octad": wu_octad in code_set,
        "external_canonicity_boundary_preserved": hexacode["canonicity_boundary"][
            "canonical_from_pair_octad_wu_6j_data"
        ]
        is False
        and row_obstruction["conclusion"]["canonical_row_alignment_from_pair_octad_wu_6j_data"]
        is False,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.w24_hexacode_row_alphabetization.artifact@1",
        "status": "D20_W24_HEXACODE_ROW_ALPHABETIZATION_DERIVED",
        "claim_scope": (
            "Derive an explicit row alphabetization of the MOG W24 grid from the external "
            "hexacode/F4 row selector and certify that it generates the extended binary "
            "Golay code."
        ),
        "source_reports": {
            "alphabetized_golay_finiteness": input_entry(
                ALPHABETIZED_FINITENESS,
                {
                    "certificate_sha256": finiteness["certificate_sha256"],
                    "status": finiteness["status"],
                },
            ),
            "mog_resolvent_invariant": input_entry(
                MOG_RESOLVENT,
                {
                    "mog_resolvent_invariant_sha256": mog["mog_resolvent_invariant_sha256"],
                    "status": mog["status"],
                },
            ),
            "mog_canonicity_boundary": input_entry(
                MOG_CANONICITY,
                {
                    "mog_canonicity_boundary_sha256": canonicity[
                        "mog_canonicity_boundary_sha256"
                    ],
                    "status": canonicity["status"],
                },
            ),
            "full_row_refined_obstruction": input_entry(
                FULL_ROW_REFINED_OBSTRUCTION,
                {
                    "full_row_refined_golay_selector_obstruction_sha256": row_obstruction[
                        "full_row_refined_golay_selector_obstruction_sha256"
                    ],
                    "status": row_obstruction["status"],
                },
            ),
            "hexacode_row_selector": input_entry(
                HEXACODE_ROW_SELECTOR,
                {
                    "hexacode_row_selector_sha256": hexacode["hexacode_row_selector_sha256"],
                    "status": hexacode["status"],
                },
            ),
            "wu_spinh_6j_marking": input_entry(
                WU_SPINH_6J_MARKING,
                {
                    "wu_spinh_6j_marking_sha256": wu["wu_spinh_6j_marking_sha256"],
                    "status": wu["status"],
                },
            ),
        },
        "row_alphabetization": row_alphabetization,
        "hexacode": {
            "field": "F4 encoded as 0, 1, omega, omega+1; addition is xor and omega^2=omega+1",
            "f4_generator_3x6": generator,
            "word_count": len(h_words),
            "symbol_weight_histogram": {
                str(key): value
                for key, value in weight_histogram(
                    [sum(1 << idx for idx, symbol in enumerate(word) if symbol) for word in h_words]
                ).items()
            },
            "words_sha256": sha_json(h_words),
        },
        "binary_lift_rule": {
            "local_symbol_rule": "In each MOG column, a local row subset maps to the F4 sum of its selected row labels.",
            "uniform_parity_rule": "All six columns have the same parity p.",
            "global_choice_rule": "For each of the two local lifts per column, let choice_bit be 0 or 1. Keep exactly the lifts with xor(choice_bits)=p.",
            "local_lift_table": local_table_json,
        },
        "golay_code": {
            "length": 24,
            "rank": rank_masks(code),
            "size": len(code),
            "generator_shape": [len(basis), 24],
            "generator_basis_masks": basis,
            "generator_basis_rows": [mask_to_vector(mask) for mask in basis],
            "code_words_sha256": sha_json(code),
            "dodecad_masks_sha256": sha_json(dodecads),
            "minimum_nonzero_weight": min(mask.bit_count() for mask in code if mask),
            "weight_histogram": {str(key): value for key, value in hist.items()},
            "dodecad_count": len(dodecads),
            "self_orthogonal": self_orthogonal(code),
            "doubly_even": all(weight % 4 == 0 for weight in hist),
            "self_dual_by_rank_and_self_orthogonal": rank_masks(code) == 12
            and self_orthogonal(code),
        },
        "containment_witnesses": {
            "contains_column_pair_code": checks["contains_column_pair_code"],
            "column_pair_generator_masks": column_pair_generators,
            "column_pair_code_rank": rank_masks(column_pair_words),
            "column_pair_code_weight_histogram": {
                str(key): value for key, value in weight_histogram(column_pair_words).items()
            },
            "contains_current_row_pair_dodecads": checks["contains_row_pair_dodecads"],
            "row_pair_masks": row_pairs,
            "contains_current_rows": not checks["does_not_contain_single_rows"],
            "row_masks": rows,
            "contains_active_6j_edge_code": checks["contains_active_6j_edge_code"],
            "active_6j_edge_code_rank": rank_masks(active_edge_code),
            "active_6j_edge_code_weight_histogram": {
                str(key): value for key, value in weight_histogram(active_edge_code).items()
            },
            "contains_wu_octad": checks["contains_wu_octad"],
            "wu_octad_mask": wu_octad,
        },
        "canonicity_boundary": {
            "row_alphabetization_source": "external hexacode/F4 row selector",
            "canonical_from_pair_octad_wu_6j_data": False,
            "reason": hexacode["canonicity_boundary"]["reason"],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.w24_hexacode_row_alphabetization@1",
        "status": "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The external hexacode/F4 row selector supplies an explicit W24 MOG row "
            "alphabetization. With the local F4 row-sum rule, uniform column parity, and "
            "global choice xor rule, it generates a [24,12,8] extended binary Golay code "
            "matching the certified weight enumerator. This is an endpoint witness, not an "
            "intrinsic derivation from pair-octad/Wu/6j data alone."
        ),
        "definition": {
            "row_alphabetization": (
                "Each MOG column has four rows labelled by F4 values 0,1,omega,omega+1."
            ),
            "binary_lift": artifact["binary_lift_rule"],
        },
        "closure_boundary": {
            "certifies": [
                "an explicit row-labelled W24 grid over F4",
                "the 64-word F4 hexacode generated by the recorded 3x6 generator",
                "the local two-lift table for each parity/symbol pair",
                "the global xor parity rule generating exactly 4096 binary words",
                "the generated binary code has rank 12, minimum weight 8, and the extended Golay weight enumerator",
                "the generated code contains the column-pair code, all six row-pair dodecads, the active 6j edge code, and the Wu octad",
            ],
            "does_not_certify": [
                "that this row alphabetization is canonical from pair-octad/Wu/6j data alone",
                "a selected D20 sector33 -> W24 morphism",
                "an intrinsic Golay selector independent of the external hexacode/F4 row labelling",
                "a rebuild of d20.json or any finite critical group artifact",
            ],
        },
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
            **artifact["source_reports"],
        },
        "witness": {
            "row_alphabetization": artifact["row_alphabetization"],
            "hexacode": artifact["hexacode"],
            "golay_code": artifact["golay_code"],
            "containment_witnesses": artifact["containment_witnesses"],
            "canonicity_boundary": artifact["canonicity_boundary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Use this explicit W24 row alphabetization as the target alphabet, then search "
            "for a typed D20 sector33-to-W24 coordinate map rather than an unlabelled minor."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.w24_hexacode_row_alphabetization_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify MOG grid is 4x6 and row-labelled by four F4 values",
            "enumerate the 64-word F4 hexacode from the recorded 3x6 generator",
            "build the local two-lift table for each parity/symbol pair",
            "generate 4096 binary words with uniform column parity and xor choice rule",
            "verify rank 12, minimum weight 8, self-orthogonality, doubly-even weights, and Golay enumerator",
            "verify column-pair, row-pair, active 6j edge, and Wu octad containment",
            "preserve the external canonicity boundary",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") != THEOREM_ID]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
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
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "code_size": artifact["golay_code"]["size"],
                "minimum_nonzero_weight": artifact["golay_code"]["minimum_nonzero_weight"],
                "rank": artifact["golay_code"]["rank"],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
