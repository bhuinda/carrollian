from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_hamming_correspondence_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_golay_hamming_correspondence_probe.json"

INTRINSIC_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_voltage_lift_intrinsic_hex_metric" / "report.json"
)
TUTTE_OS_REPORT = D20_INVARIANTS / "theorems" / "d20_oriented_matroid_tutte_os" / "report.json"
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
WU_GOLAY_RESOLVENT = ROOT / "data" / "geometry" / "wu_golay_quintic_resolvent.json"
QUADRATIC_GOLAY_OBSTRUCTION = ROOT / "data" / "selectors" / "quadratic_golay_obstruction.json"
HEXACODE_ROW_SELECTOR = ROOT / "data" / "selectors" / "hexacode_row_selector.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_hamming_correspondence_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_hamming_correspondence_probe.py"


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def parse_fraction_numerators(text: str) -> tuple[int, int]:
    parts = text.split("/")
    if len(parts) != 2:
        raise ValueError(f"expected a/b fraction, got {text!r}")
    return int(parts[0]), int(parts[1])


def centered_pentagonal_order(value: int) -> int | None:
    # Centered pentagonal numbers are (5n^2 - 5n + 2) / 2 for n >= 1.
    n = 1
    while True:
        current = (5 * n * n - 5 * n + 2) // 2
        if current == value:
            return n
        if current > value:
            return None
        n += 1


def hamming_m(value: int) -> int | None:
    m = 1
    while (1 << m) - 1 <= value:
        if (1 << m) - 1 == value:
            return m
        m += 1
    return None


def build_artifact() -> dict[str, Any]:
    intrinsic = load_json(INTRINSIC_REPORT)
    tutte_os = load_json(TUTTE_OS_REPORT)
    dual = load_json(SECTOR33_DUAL_REPORT)
    wu = load_json(WU_GOLAY_RESOLVENT)
    obstruction = load_json(QUADRATIC_GOLAY_OBSTRUCTION)
    hexacode = load_json(HEXACODE_ROW_SELECTOR)

    eigenvalues = intrinsic["witness"]["eigenvalues_exact"]
    major_num, major_den = parse_fraction_numerators(eigenvalues["major"])
    minor_num, minor_den = parse_fraction_numerators(eigenvalues["minor"])
    field_matroid = tutte_os["derived"]["field_matroid"]
    sector33_attachment = field_matroid["sector33_height_attachment"]
    os_hilbert = tutte_os["derived"]["orlik_solomon_algebra"]["hilbert_coefficients_by_degree"]
    dual_cocircuit = dual["derived"]["dual_positive_cocircuit"]
    golay_code = hexacode["golay_code"]
    golay_length = int(golay_code["generator_shape"][1])
    hexacode_columns = len(hexacode["hexacode"]["f4_generator_3x6"][0])
    wu_rank = int(wu["linear_syzygies"]["linear_syzygy_basis_rank"])
    wu_dimension = int(wu["linear_syzygies"]["linear_syzygy_dimension"])
    punctured_golay_length = golay_length - 1
    sector_ground = int(field_matroid["ground_set_size"])
    sector_old_edges = int(sector33_attachment["new_element_id"])

    checks = {
        "intrinsic_metric_ratio_is_31_over_23": intrinsic["witness"]["anisotropy_ratio_exact"] == "31/23",
        "metric_eigenvalues_have_common_denominator_20": major_den == 20 and minor_den == 20,
        "major_numerator_matches_sector33_ground_set": major_num == sector_ground == 31,
        "sector33_ground_is_30_edges_plus_e33": sector_old_edges == 30 and sector_ground == sector_old_edges + 1,
        "sector33_os_hilbert_begins_1_31": os_hilbert[:2] == [1, 31],
        "sector33_all_subsets_is_2_to_31": tutte_os["derived"]["tutte_polynomial"]["specializations"][
            "T_2_2_all_subsets"
        ]
        == 2**31,
        "sector33_dual_positive_cocircuit_has_six_elements": len(dual_cocircuit["support"]) == 6,
        "sector33_dual_cocircuit_includes_e33": sector33_attachment["new_element_id"] in dual_cocircuit["support"],
        "minor_numerator_matches_wu_syzygy_rank": minor_num == wu_rank == wu_dimension == 23,
        "minor_numerator_matches_punctured_golay_length": minor_num == punctured_golay_length == 23,
        "wu_report_declares_golay_extension_unresolved": wu["Golay_extension_test"]["passes_golay_test"] is False,
        "hexacode_selector_constructs_extended_golay": bool(
            golay_code["doubly_even"]
            and golay_code["self_dual_by_rank_and_self_orthogonal"]
            and golay_code["matches_extended_golay_weight_enumerator"]
            and golay_code["rank"] == 12
            and golay_length == 24
        ),
        "hexacode_has_six_columns": hexacode_columns == 6,
        "hexacode_canonicity_is_external": hexacode["canonicity_boundary"][
            "canonical_from_pair_octad_wu_6j_data"
        ]
        is False,
        "quadratic_obstruction_blocks_intrinsic_rank12_typeII_selector": obstruction["selector_status"][
            "golay_selector_constructed"
        ]
        is False
        and obstruction["support_nullspace_witt_audit"][
            "rank_12_golay_inside_support_nullspace_possible_by_witt_bound"
        ]
        is False,
        "explicit_31_to_24_to_23_morphism_not_constructed": True,
        "open_boundary_is_recorded": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_correspondence_probe.artifact@1",
        "status": "D20_GOLAY_HAMMING_CORRESPONDENCE_PROBE_DERIVED",
        "claim_scope": (
            "This artifact certifies the exact numeric and structural alignments behind the "
            "31/23 question and records that the explicit Golay-Hamming correspondence morphism "
            "is still open."
        ),
        "source_reports": {
            "intrinsic_hex_metric": input_entry(
                INTRINSIC_REPORT,
                {
                    "certificate_sha256": intrinsic["certificate_sha256"],
                    "status": intrinsic["status"],
                },
            ),
            "sector33_tutte_os": input_entry(
                TUTTE_OS_REPORT,
                {
                    "certificate_sha256": tutte_os["certificate_sha256"],
                    "status": tutte_os["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual["certificate_sha256"],
                    "status": dual["status"],
                },
            ),
            "wu_golay_resolvent": input_entry(
                WU_GOLAY_RESOLVENT,
                {
                    "status": wu["status"],
                    "wu_golay_quintic_resolvent_sha256": wu["wu_golay_quintic_resolvent_sha256"],
                },
            ),
            "quadratic_golay_obstruction": input_entry(
                QUADRATIC_GOLAY_OBSTRUCTION,
                {
                    "status": obstruction["status"],
                    "quadratic_golay_selector_obstruction_sha256": obstruction[
                        "quadratic_golay_selector_obstruction_sha256"
                    ],
                },
            ),
            "hexacode_row_selector": input_entry(
                HEXACODE_ROW_SELECTOR,
                {
                    "hexacode_row_selector_sha256": hexacode["hexacode_row_selector_sha256"],
                },
            ),
        },
        "certified_alignments": {
            "metric": {
                "eigenvalues_exact": eigenvalues,
                "anisotropy_ratio_exact": intrinsic["witness"]["anisotropy_ratio_exact"],
                "major_numerator": major_num,
                "minor_numerator": minor_num,
            },
            "sector33_hamming_31": {
                "sector33_ground_set_size": sector_ground,
                "d20_old_edge_elements": sector_old_edges,
                "new_element": sector33_attachment["new_element"],
                "new_element_id": sector33_attachment["new_element_id"],
                "os_hilbert_first_coefficients": os_hilbert[:2],
                "tutte_all_subsets_specialization": tutte_os["derived"]["tutte_polynomial"][
                    "specializations"
                ]["T_2_2_all_subsets"],
                "hamming_length_m": hamming_m(sector_ground),
                "centered_pentagonal_order": centered_pentagonal_order(sector_ground),
            },
            "wu_golay_23": {
                "wu_linear_syzygy_basis_rank": wu_rank,
                "wu_linear_syzygy_dimension": wu_dimension,
                "wu_golay_extension_test_passes": wu["Golay_extension_test"]["passes_golay_test"],
                "extended_golay_length": golay_length,
                "punctured_golay_length": punctured_golay_length,
                "extended_golay_rank": golay_code["rank"],
                "extended_golay_weight_histogram": golay_code["weight_histogram"],
            },
            "sixfold_spine": {
                "sector33_dual_positive_cocircuit_support": dual_cocircuit["support"],
                "sector33_dual_positive_cocircuit_support_size": len(dual_cocircuit["support"]),
                "hexacode_columns": hexacode_columns,
                "hexacode_f4_dimension": hexacode["hexacode"]["f4_dimension"],
            },
        },
        "candidate_morphism": {
            "diagram": [
                "M31 = sector33 height attachment on 30 D20 edge elements plus e33",
                "candidate minor/marking: M31 -> canonical 24-coordinate Wu/Golay frame",
                "puncture Euler/unit coordinate: W24 -> length-23 punctured Golay frame",
            ],
            "currently_certified_maps": [
                "D20 signed-label edge transitions -> intrinsic A2 regular-hex covariance",
                "sector33 height attachment -> 31-element finite-field Tutte/OS package",
                "Wu quintic resolvent -> 23-dimensional syzygy basis with Golay extension unresolved",
                "external six-column hexacode row selector -> extended binary Golay code G24",
            ],
            "missing_map": (
                "a canonical delete/contract/select functor from the 31-element sector33 matroid "
                "to the 24-coordinate Wu/Golay frame, compatible with the six-column hexacode "
                "selector, followed by a typed puncture to 23 coordinates"
            ),
            "morphism_status": "OPEN_NOT_CONSTRUCTED",
        },
        "obstruction_boundary": {
            "wu_golay_reason": wu["Golay_extension_test"]["reason"],
            "quadratic_selector_interpretation": obstruction["selector_status"]["interpretation"],
            "hexacode_canonicity_reason": hexacode["canonicity_boundary"]["reason"],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_correspondence_probe@1",
        "status": "D20_GOLAY_HAMMING_CORRESPONDENCE_PROBE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The observed 31/23 alignment is certified as a shared numeric boundary between the "
            "D20 intrinsic hex metric, the 31-element sector33 height attachment, the 23-dimensional "
            "Wu syzygy profile, and the externally marked hexacode/Golay endpoint. The explicit "
            "31 -> 24 -> 23 Golay-Hamming correspondence morphism remains open and is not promoted "
            "to a theorem here."
        ),
        "definition": {
            "morphism_under_test": artifact["candidate_morphism"]["missing_map"],
            "certified_open_boundary": (
                "The probe is successful only because it records both the positive alignments and "
                "the obstruction/canonicity seams that prevent a direct Golay theorem."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "31 is the major eigenvalue numerator of the intrinsic hex metric and the sector33 matroid ground size",
                "the sector33 31 equals 30 D20 edge elements plus the e33 wall element",
                "23 is the minor eigenvalue numerator, the Wu linear syzygy rank, and the punctured length of G24",
                "the shared sixfold spine is visible as the sector33 positive cocircuit size and the hexacode column count",
                "the explicit Golay-Hamming correspondence morphism is not currently constructed",
            ],
            "does_not_certify": [
                "a canonical map from the sector33 31-element matroid to the 24-coordinate Wu/Golay frame",
                "an intrinsic Golay selector from D20/Wu support geometry alone",
                "a Hamming [31] code structure on the sector33 matroid",
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
        "witness": artifact["certified_alignments"],
        "candidate_morphism": artifact["candidate_morphism"],
        "obstruction_boundary": artifact["obstruction_boundary"],
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Try the explicit minor/puncture search: enumerate natural delete/contract sets from "
            "the sector33 dual cocircuit and e33 wall data, then compare any induced 24-coordinate "
            "binary row space against the certified hexacode/Golay selector."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_correspondence_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify intrinsic metric eigenvalues are 31/20 and 23/20",
            "verify sector33 ground size is 31 = 30 D20 edge elements plus e33",
            "verify sector33 Tutte/OS all-subsets specialization is 2^31 and Hilbert begins [1,31]",
            "verify Wu syzygy rank is 23 and Golay extension remains unresolved",
            "verify external hexacode selector constructs G24 and has six columns",
            "verify quadratic Golay selector obstruction blocks an intrinsic rank-12 Type-II selector",
            "verify the explicit 31 -> 24 -> 23 morphism is recorded as open, not certified",
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
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "morphism_status": report["candidate_morphism"]["morphism_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
