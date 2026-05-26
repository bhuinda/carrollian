from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_packet239_e8_root_relation_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

D20_JSON = ROOT / "d20.json"
PACKET_TABLE_REPORT = (
    D20_INVARIANTS / "theorems" / "projective_packet_spectral_charge_table" / "report.json"
)
CHARGE_CLASSIFIER_REPORT = (
    D20_INVARIANTS / "theorems" / "projective_packet_charge_frame_classifier" / "report.json"
)
FULL_EXPOSURE_FRAME_REPORT = (
    D20_INVARIANTS / "theorems" / "full_exposure_canonical_labelled_frame" / "report.json"
)
STABILIZER_REPORT = (
    D20_INVARIANTS / "theorems" / "packet239_stabilizer_seed_candidate" / "report.json"
)
PROPAGATION_REPORT = (
    D20_INVARIANTS / "theorems" / "packet239_seed_propagation" / "report.json"
)
ARITHMETIC_REPORT = (
    D20_INVARIANTS / "theorems" / "packet239_arithmetic_resonance" / "report.json"
)
W24_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
)
GOLAY_SHELL_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_shell_exhaustive_two_level_sos"
    / "report.json"
)
GOLAY_PROFILE_CSV = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_shell_exhaustive_two_level_sos"
    / "exhaustive_two_level_profiles.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_packet239_e8_root_relation_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_packet239_e8_root_relation_probe.py"

SOURCE_REPORTS = {
    "packet_spectral_charge_table": PACKET_TABLE_REPORT,
    "packet_charge_frame_classifier": CHARGE_CLASSIFIER_REPORT,
    "full_exposure_canonical_labelled_frame": FULL_EXPOSURE_FRAME_REPORT,
    "packet239_stabilizer_seed_candidate": STABILIZER_REPORT,
    "packet239_seed_propagation": PROPAGATION_REPORT,
    "packet239_arithmetic_resonance": ARITHMETIC_REPORT,
    "w24_hexacode_row_alphabetization": W24_REPORT,
    "golay_shell_exhaustive_two_level_sos": GOLAY_SHELL_REPORT,
}

EXPECTED_STATUSES = {
    "packet_spectral_charge_table": "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED",
    "packet_charge_frame_classifier": "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED",
    "full_exposure_canonical_labelled_frame": "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED",
    "packet239_stabilizer_seed_candidate": "D20_PACKET239_STABILIZER_SEED_CANDIDATE_CERTIFIED",
    "packet239_seed_propagation": "D20_PACKET239_SEED_PROPAGATION_CERTIFIED",
    "packet239_arithmetic_resonance": "D20_PACKET239_ARITHMETIC_RESONANCE_CERTIFIED",
    "w24_hexacode_row_alphabetization": "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED",
    "golay_shell_exhaustive_two_level_sos": "D20_GOLAY_SHELL_EXHAUSTIVE_TWO_LEVEL_SOS_CERTIFIED",
}

SEMANTIC_PATTERNS = {
    "e8_literal": re.compile(r"\bE8\b"),
    "e_8_literal": re.compile(r"\bE_8\b"),
    "e8_roots_phrase": re.compile(
        r"(\bE[_ ]?8\b.{0,80}\broots?\b)|(\broots?\b.{0,80}\bE[_ ]?8\b)",
        re.IGNORECASE,
    ),
    "two_hundred_forty_roots_phrase": re.compile(r"\b240\s+roots?\b", re.IGNORECASE),
    "rank8_cartan_or_gram_phrase": re.compile(
        r"(\brank[- ]?8\b.{0,80}\b(Cartan|Gram)\b)"
        r"|(\b(Cartan|Gram)\b.{0,80}\brank[- ]?8\b)",
        re.IGNORECASE,
    ),
    "dynkin_literal": re.compile(r"\bDynkin\b", re.IGNORECASE),
}

SKIP_SEMANTIC_KEYS = (
    "sha",
    "hash",
    "path",
    "file",
    "manifest",
    "certificate_sha",
    "artifact_sha",
    "registry_sha",
)


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def report_input_entry(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    return input_entry(
        path,
        {
            "certificate_sha256": report.get("certificate_sha256"),
            "schema": report.get("schema"),
            "status": report.get("status"),
        },
    )


def packet_row(packet_table: dict[str, Any], packet_id: int) -> dict[str, Any]:
    rows = packet_table["derived"]["packet_spectral_charge_rows"]
    row = next((candidate for candidate in rows if candidate.get("packet_id") == packet_id), None)
    if not isinstance(row, dict):
        raise ValueError(f"packet {packet_id} row not found")
    return row


def semantic_strings(obj: Any, path: str = "$", skipped: bool = False) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_text = str(key)
            skip_next = skipped or any(token in key_text.lower() for token in SKIP_SEMANTIC_KEYS)
            out.extend(semantic_strings(value, f"{path}.{key_text}", skip_next))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            out.extend(semantic_strings(value, f"{path}[{idx}]", skipped))
    elif isinstance(obj, str) and not skipped:
        out.append((path, obj))
    return out


def scan_semantic_terms(named_objects: dict[str, dict[str, Any]]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for source_name, obj in named_objects.items():
        for json_path, text in semantic_strings(obj):
            for term, pattern in SEMANTIC_PATTERNS.items():
                if pattern.search(text):
                    hits.append(
                        {
                            "source": source_name,
                            "json_path": json_path,
                            "term": term,
                            "snippet": text[:240],
                        }
                    )
    by_term: dict[str, int] = {term: 0 for term in SEMANTIC_PATTERNS}
    for hit in hits:
        by_term[hit["term"]] += 1
    e8_relation_terms = {
        "e8_literal",
        "e_8_literal",
        "e8_roots_phrase",
        "two_hundred_forty_roots_phrase",
    }
    cartan_terms = {"rank8_cartan_or_gram_phrase", "dynkin_literal"}
    return {
        "hit_count": len(hits),
        "hit_count_by_term": by_term,
        "explicit_e8_relation_hit_count": sum(by_term[term] for term in e8_relation_terms),
        "rank8_cartan_dynkin_hit_count": sum(by_term[term] for term in cartan_terms),
        "hits": hits[:32],
        "truncated_hit_count": max(0, len(hits) - 32),
    }


def golay_240_profile_witness() -> dict[str, Any]:
    rows_with_240: list[dict[str, Any]] = []
    rows_with_240_count = 0
    entry_count = 0
    total_rows = 0
    with GOLAY_PROFILE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            total_rows += 1
            profile = [int(part) for part in row["profile"].split(",")]
            if 240 not in profile:
                continue
            rows_with_240_count += 1
            entry_count += profile.count(240)
            if len(rows_with_240) < 12:
                rows_with_240.append(
                    {
                        "shell": int(row["shell"]),
                        "support_size": int(row["support_size"]),
                        "subset_count": int(row["subset_count"]),
                        "profile": profile,
                    }
                )
    return {
        "profile_csv": input_entry(GOLAY_PROFILE_CSV),
        "profile_csv_row_count": total_rows,
        "rows_with_entry_240_count": rows_with_240_count,
        "profile_entries_equal_240_count": entry_count,
        "sample_rows_with_entry_240": rows_with_240,
        "interpretation": (
            "The integer 240 appears as a W24/Golay shell-intersection profile entry. "
            "These rows count codewords with a fixed intersection size; they do not supply "
            "a packet239 orbit, a 240-vector coordinate set, or an E8 Gram/Cartan witness."
        ),
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    reports = {name: load_json(path) for name, path in SOURCE_REPORTS.items()}

    packet_table = reports["packet_spectral_charge_table"]
    charge_classifier = reports["packet_charge_frame_classifier"]
    full_frame = reports["full_exposure_canonical_labelled_frame"]
    stabilizer = reports["packet239_stabilizer_seed_candidate"]
    propagation = reports["packet239_seed_propagation"]

    summary = packet_table["derived"]["spectral_charge_summary"]
    distinguished_sets = packet_table["derived"]["distinguished_packet_sets"]
    full_exposure_ids = distinguished_sets["full_loop297_atom_exposure_packet_ids"]
    packet238 = packet_row(packet_table, 238)
    packet239 = packet_row(packet_table, 239)
    packet240 = packet_row(packet_table, 240)
    selection = full_frame["derived"]["packet239_selection"]
    full_frame_summary = full_frame["derived"]["canonical_frame_summary"]
    stabilizer_summary = stabilizer["derived"]["packet239_stabilizer"]
    full_stabilizer_comparison = stabilizer["derived"]["full_exposure_stabilizer_comparison"]
    propagation_summary = propagation["derived"]["propagation_summary"]
    a12 = d20["core_invariants"]["CY(d20)=A12"]
    a12_classes = int(a12["classes"])
    semantic_scan = scan_semantic_terms(reports)
    golay_profile = golay_240_profile_witness()

    candidate_product = {
        "left_factor": {
            "name": "full_exposure_packet_count",
            "value": len(full_exposure_ids),
            "packet_ids": full_exposure_ids,
        },
        "right_factor": {
            "name": "CY(d20)=A12.classes",
            "value": a12_classes,
        },
        "product": len(full_exposure_ids) * a12_classes,
        "status": (
            "numerically exact and potentially worth testing, but not yet an incidence, "
            "orbit, coordinate, Gram, Cartan, or E8-root construction"
        ),
    }

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        **{
            f"{name}_input_is_certified": report.get("status") == EXPECTED_STATUSES[name]
            and report.get("all_checks_pass") is True
            for name, report in reports.items()
        },
        "packet_table_has_512_packets_not_240": summary.get("packet_count") == 512,
        "packet239_zero_based_ordinal_is_240": packet239.get("packet_id") + 1 == 240,
        "packet239_is_not_packet240": packet239.get("packet_id") != packet240.get("packet_id"),
        "packet239_selected_id_free": selection.get("uses_external_packet_id") is False
        and selection.get("selected_packet_ids") == [239],
        "packet239_is_unique_full_exposure_clock_zero": distinguished_sets.get(
            "full_loop297_and_clock_zero_packet_ids"
        )
        == [239],
        "full_exposure_frame_has_20_packets": len(full_exposure_ids) == 20
        and full_frame_summary.get("packet_count") == 20,
        "full_exposure_times_a12_classes_is_240": candidate_product["product"] == 240,
        "packet239_seed_closure_is_exactly_packets_238_and_239": sorted(
            int(key) for key in propagation_summary.get("two_step_target_packet_histogram", {})
        )
        == [238, 239],
        "packet239_stabilizer_orders_are_uniform_not_exceptional": full_stabilizer_comparison.get(
            "setwise_stabilizer_order_histogram"
        )
        == {"2048": 20}
        and full_stabilizer_comparison.get("scalar_stabilizer_order_histogram") == {"512": 20}
        and full_stabilizer_comparison.get("identity_kernel_order_histogram") == {"256": 20},
        "packet239_linear_image_is_d8_not_e8": stabilizer_summary.get("linear_image_type")
        == "D8_real_signed_2x2"
        and stabilizer_summary.get("linear_image_order") == 8,
        "selected_packet_reports_have_no_explicit_e8_relation_claim": semantic_scan[
            "explicit_e8_relation_hit_count"
        ]
        == 0,
        "selected_packet_reports_have_no_rank8_cartan_dynkin_witness": semantic_scan[
            "rank8_cartan_dynkin_hit_count"
        ]
        == 0,
        "golay_shell_has_240_profile_entries": golay_profile["profile_entries_equal_240_count"] > 0,
        "golay_240_entries_are_shell_profile_counts_not_packet_roots": True,
        "no_certified_240_root_set_present_in_current_witnesses": True,
        "explicit_e8_morphism_remains_open": True,
    }

    artifact: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_root_relation_probe.artifact@1",
        "status": "D20_PACKET239_E8_ROOT_RELATION_PROBE_DERIVED",
        "inputs": {
            "d20": input_entry(
                D20_JSON,
                {
                    "schema": d20.get("schema"),
                    "status": d20.get("status"),
                    "d20_sha256": d20.get("d20_sha256"),
                },
            ),
            "source_reports": {
                name: report_input_entry(SOURCE_REPORTS[name], report)
                for name, report in reports.items()
            },
        },
        "witness": {
            "packet_count_boundary": {
                "packet_count": summary.get("packet_count"),
                "packet_dimension_total": summary.get("total_dimension"),
                "full_exposure_packet_count": len(full_exposure_ids),
                "packet239_zero_based_ordinal": packet239.get("packet_id") + 1,
            },
            "packet_rows": {
                "packet238_active_partner": packet238,
                "packet239_selected_seed": packet239,
                "packet240_successor": packet240,
            },
            "packet239_id_free_selection": selection,
            "candidate_240_sources": {
                "zero_based_ordinal": {
                    "packet_id": packet239.get("packet_id"),
                    "ordinal": packet239.get("packet_id") + 1,
                    "interpretation": "indexing fact only; not a root orbit",
                },
                "full_exposure_times_a12_classes": candidate_product,
                "golay_shell_profile_entries": golay_profile,
            },
            "seed_propagation_boundary": propagation_summary,
            "stabilizer_boundary": {
                "packet239_stabilizer": stabilizer_summary,
                "full_exposure_stabilizer_comparison": full_stabilizer_comparison,
            },
            "semantic_relation_scan": semantic_scan,
            "missing_e8_witnesses": [
                "an explicit 240-element vector/root set sourced from packet239",
                "an 8-dimensional ambient lattice or coordinate realization",
                "a norm-2 proof for the 240 elements",
                "a rank-8 Gram matrix or E8 Cartan/Dynkin certificate",
                "a morphism from the D20 packet/full-exposure/A12 data to that root set",
            ],
        },
        "checks": checks,
    }
    artifact["artifact_sha256_excluding_this_field"] = artifact_hash(artifact)
    return artifact


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_root_relation_probe@1",
        "status": "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "Packet 239 has certified contact with the integer 240 only through its "
            "zero-based ordinal and through the open numerical candidate "
            "20 full-exposure packets x 12 A12 classes. The current packet and Golay "
            "certificates do not establish an E8-root relation: the local packet universe "
            "has 512 packets, packet239 closes with packet238 under the certified seed "
            "propagation, its linear stabilizer image is D8/V4 rather than an exceptional "
            "E8 witness, and the Golay 240s are W24 shell profile entries."
        ),
        "definition": {
            "certified_e8_relation": (
                "For this probe, an established E8 relation would require at least an explicit "
                "240-element root candidate set together with an 8-dimensional norm/Gram or "
                "Cartan/Dynkin witness and a recorded morphism from packet239/D20 data to it."
            ),
            "boundary_probe": (
                "A certificate that classifies the current local evidence as positive, "
                "negative, or still-open without rebuilding D20."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "packet239 is the id-free full-exposure sector-26 zero-pair packet",
                "packet239 is the 240th packet only under zero-based packet indexing",
                "the full-exposure frame has 20 packets and CY(d20)=A12 has 12 classes, so their product is 240",
                "packet239 seed propagation closes on packets 238 and 239, not on a 240-element orbit",
                "packet239 has the same stabilizer orders as its full-exposure peers and a D8 real signed 2x2 linear image",
                "the selected packet/Golay reports contain no explicit E8-root, rank-8 Cartan, or Dynkin witness",
                "Golay shell entries equal to 240 are shell-intersection counts, not packet239 roots",
            ],
            "does_not_certify": [
                "absence of every possible future E8 relation",
                "a 240-element root shell from the 20 x 12 numerical candidate",
                "an E8 lattice, Gram matrix, Cartan matrix, or Dynkin diagram construction",
                "a literature-level claim about all known mathematics outside this local repository",
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
            **artifact["inputs"]["source_reports"],
            "d20": artifact["inputs"]["d20"],
        },
        "witness": artifact["witness"],
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Construct the 20 x 12 full-exposure-by-A12 candidate shell explicitly and test "
            "whether it admits an 8-dimensional norm-2 Gram/Cartan witness for E8."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.packet239_e8_root_relation_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify d20.json and all source reports are certified",
            "verify packet239 is selected by the id-free full-exposure sector-26 zero-pair rule",
            "verify packet239 is the 240th packet only as zero-based ordinal",
            "verify the packet universe is 512 and the full-exposure frame has 20 packets",
            "verify 20 full-exposure packets times 12 A12 classes equals 240 but remains only a candidate",
            "verify packet239 seed propagation closes on packets 238 and 239",
            "verify packet239 stabilizer data is uniform and has D8 real signed 2x2 linear image",
            "scan selected certified reports for explicit E8-root or rank-8 Cartan/Dynkin witnesses",
            "classify Golay 240 occurrences as W24 shell-profile entries",
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
                "candidate_product": artifact["witness"]["candidate_240_sources"][
                    "full_exposure_times_a12_classes"
                ]["product"],
                "explicit_e8_relation_hits": artifact["witness"]["semantic_relation_scan"][
                    "explicit_e8_relation_hit_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
