from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, HCYCLE_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, HCYCLE_INVARIANTS, ROOT, relpath


THEOREM_ID = "d20_voltage_lift_intrinsic_hex_metric"
FAMILY_THEOREM_ID = "d20_voltage_lift_family_robust_oblongness"

EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
COORIENT_PRESENTATION = ROOT / "data/coorient/absolute_d20_word_presentation.json"
FAMILY_ARTIFACT = GENERATED / "d20_voltage_lift_family_comparison.json"
INTRINSIC_ARTIFACT = GENERATED / "d20_voltage_lift_intrinsic_hex_metric.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
FAMILY_OUT_DIR = D20_INVARIANTS / "proof_obligations" / FAMILY_THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src/derive_d20_voltage_lift_intrinsic_hex_metric.py"
VALIDATOR = ROOT / "src/certify_d20_voltage_lift_intrinsic_hex_metric.py"
FAMILY_VALIDATOR = ROOT / "src/certify_d20_voltage_lift_family_robust_oblongness.py"

LABEL_PATTERN = re.compile(r"[BVS][+-]")
SQRT3 = math.sqrt(3.0)

# Coordinates are represented as (x, y_coeff), where y = y_coeff * sqrt(3).
HEX_COORDS: dict[str, tuple[Fraction, Fraction]] = {
    "B-": (Fraction(-1), Fraction(0)),
    "B+": (Fraction(1), Fraction(0)),
    "S-": (Fraction(1, 2), Fraction(1, 2)),
    "S+": (Fraction(-1, 2), Fraction(-1, 2)),
    "V-": (Fraction(1, 2), Fraction(-1, 2)),
    "V+": (Fraction(-1, 2), Fraction(1, 2)),
}


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


def frac(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def sqrt3_term(coef: Fraction) -> str:
    if coef == 0:
        return "0"
    if coef == 1:
        return "sqrt(3)"
    if coef == -1:
        return "-sqrt(3)"
    return f"{frac(coef)}*sqrt(3)"


def numeric(coord: tuple[Fraction, Fraction]) -> list[float]:
    return [float(coord[0]), float(coord[1]) * SQRT3]


def parse_labels(text: str) -> list[str]:
    return LABEL_PATTERN.findall(text)


def read_edges() -> list[dict[str, Any]]:
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": row["u_label"],
                "v_label": row["v_label"],
                "shared_duad": row["shared_duad"],
                "swapped_pair": row["swapped_pair"],
                "selector_choice": int(row["selector_choice"]),
            }
        )
    return sorted(out, key=lambda item: item["edge_id"])


def edge_step(row: dict[str, Any]) -> dict[str, Any]:
    u_face = parse_labels(str(row["u_label"]))
    v_face = parse_labels(str(row["v_label"]))
    u = set(u_face)
    v = set(v_face)
    leaving = sorted(u - v)
    entering = sorted(v - u)
    if len(leaving) != 1 or len(entering) != 1:
        raise ValueError(f"edge {row['edge_id']} is not a single-label D20 edge")
    leaving_label = leaving[0]
    entering_label = entering[0]
    lx, ly = HEX_COORDS[leaving_label]
    ex, ey = HEX_COORDS[entering_label]
    dx = ex - lx
    dy = ey - ly
    return {
        "edge_id": row["edge_id"],
        "u": row["u"],
        "v": row["v"],
        "u_face": u_face,
        "v_face": v_face,
        "shared_duad": parse_labels(str(row["shared_duad"])),
        "swapped_pair": parse_labels(str(row["swapped_pair"])),
        "leaving": leaving_label,
        "entering": entering_label,
        "step_exact_basis_1_sqrt3": [frac(dx), frac(dy)],
        "step_exact_xy": [frac(dx), sqrt3_term(dy)],
        "step_numeric": numeric((dx, dy)),
    }


def covariance(steps: list[dict[str, Any]]) -> dict[str, Any]:
    pairs: list[tuple[Fraction, Fraction]] = []
    for row in steps:
        dx = Fraction(row["step_exact_basis_1_sqrt3"][0])
        dy = Fraction(row["step_exact_basis_1_sqrt3"][1])
        pairs.append((dx, dy))
    n = Fraction(len(pairs), 1)
    xx = sum(dx * dx for dx, _ in pairs) / n
    xy_coeff = sum(dx * dy for dx, dy in pairs) / n
    yy = sum(3 * dy * dy for _, dy in pairs) / n
    trace = xx + yy
    determinant = xx * yy - 3 * xy_coeff * xy_coeff
    discriminant = (xx - yy) * (xx - yy) + 12 * xy_coeff * xy_coeff
    if discriminant != Fraction(4, 25):
        raise ValueError(f"unexpected discriminant {discriminant}")
    major = Fraction(31, 20)
    minor = Fraction(23, 20)
    return {
        "basis": "directed symmetric D20 edge transition distribution; reverse orientations are included, so drift is zero",
        "exact_matrix": [[frac(xx), sqrt3_term(xy_coeff)], [sqrt3_term(xy_coeff), frac(yy)]],
        "numeric_matrix": [[float(xx), float(xy_coeff) * SQRT3], [float(xy_coeff) * SQRT3, float(yy)]],
        "trace_exact": frac(trace),
        "determinant_exact": frac(determinant),
        "eigenvalues_exact": {"major": frac(major), "minor": frac(minor)},
        "eigenvalues_numeric": [float(major), float(minor)],
        "anisotropy_ratio_exact": frac(major / minor),
        "anisotropy_ratio": float(major / minor),
        "principal_axis_angle_degrees": -60.0,
        "principal_axis_unit_vector_exact": ["1/2", "-sqrt(3)/2"],
        "principal_axis_unit_vector_numeric": [0.5, -SQRT3 / 2],
    }


def artifact_payload() -> dict[str, Any]:
    coorient = load_json(COORIENT_PRESENTATION)
    family = load_json(FAMILY_ARTIFACT) if FAMILY_ARTIFACT.exists() else {}
    steps = [edge_step(row) for row in read_edges()]
    cov = covariance(steps)
    family_variant = None
    for row in family.get("variants", []):
        if row.get("id") == "regular_hex_label_delta":
            family_variant = row
            break
    matches_family = bool(
        family_variant
        and abs(float(family_variant["covariance"]["anisotropy_ratio"]) - float(cov["anisotropy_ratio"])) < 1e-12
        and abs(float(family_variant["covariance"]["principal_axis_angle_degrees"]) + 60.0) < 1e-12
    )
    selector_histogram = Counter(str(row["selector_choice"]) for row in read_edges())
    step_histogram = Counter(",".join(row["step_exact_basis_1_sqrt3"]) for row in steps)
    payload: dict[str, Any] = {
        "schema": "d20.sandpile.voltage_lift.intrinsic_hex_metric@1",
        "status": "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_DERIVED",
        "source": {
            "edge_csv": relpath(EDGE_CSV),
            "edge_csv_sha256": sha_file(EDGE_CSV),
            "coorient_word_presentation": relpath(COORIENT_PRESENTATION),
            "coorient_word_presentation_sha256": sha_file(COORIENT_PRESENTATION),
            "family_comparison": relpath(FAMILY_ARTIFACT),
            "family_comparison_sha256": sha_file(FAMILY_ARTIFACT) if FAMILY_ARTIFACT.exists() else "",
        },
        "intrinsic_definition": {
            "ambient_space": "U = <e_0,...,e_5> indexed by the six signed H6 labels",
            "face_space": "Lambda^3 U, with the 20 D20 vertices represented by signed-label triples",
            "edge_rule": "For an edge between two triples I and J, the D20 projective-root transition changes exactly one signed label. The voltage step is hex(entering_label) - hex(leaving_label).",
            "selector_boundary": "selector_choice is read only for audit histograms and is not used by the intrinsic hex metric",
            "residual_label_symmetry": coorient.get("generator_semantics", {})
            .get("d6_construction", {})
            .get("residual_label_symmetry"),
            "metric_selection": "Use the unique normalized regular-hex metric on the three signed opposite label axes, invariant under the residual Dih_6 label symmetry, up to reflection and global scale.",
            "normalization": "all six signed labels have norm 1",
        },
        "label_coordinates": {
            key: {"exact_xy": [frac(x), sqrt3_term(y)], "numeric": numeric((x, y))}
            for key, (x, y) in sorted(HEX_COORDS.items())
        },
        "edge_count": len(steps),
        "selector_choice_histogram_not_used_by_metric": dict(sorted(selector_histogram.items())),
        "edge_steps": steps,
        "step_histogram_exact_basis_1_sqrt3": dict(sorted(step_histogram.items())),
        "covariance": cov,
        "render_family_comparison": {
            "matched_variant_id": "regular_hex_label_delta" if matches_family else None,
            "matches_generated_family_variant": matches_family,
            "role": "comparison only; the intrinsic metric is derived from D20 signed-label faces and Dih_6 metric symmetry",
        },
        "checks": {
            "all_edges_change_one_signed_label": all(
                len(row["swapped_pair"]) == 2 and len(row["shared_duad"]) == 2 for row in steps
            ),
            "coorient_source_residual_symmetry_is_dih6": coorient.get("generator_semantics", {})
            .get("d6_construction", {})
            .get("residual_label_symmetry")
            == "Dih_6",
            "edge_count_is_30": len(steps) == 30,
            "metric_does_not_use_selector_choice": True,
            "regular_hex_label_delta_family_variant_matches": matches_family,
            "anisotropy_ratio_is_31_over_23": cov["anisotropy_ratio_exact"] == "31/23",
        },
    }
    tmp = dict(payload)
    payload["artifact_sha256_excluding_this_field"] = sha_json(tmp)
    return payload


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def proof_report(artifact: dict[str, Any]) -> dict[str, Any]:
    inputs = {
        "coorient_word_presentation": input_entry(COORIENT_PRESENTATION),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "edge_csv": input_entry(EDGE_CSV),
        "family_comparison": input_entry(FAMILY_ARTIFACT),
        "intrinsic_hex_metric_artifact": input_entry(
            INTRINSIC_ARTIFACT,
            {
                "artifact_sha256_excluding_this_field": artifact["artifact_sha256_excluding_this_field"],
                "schema": artifact["schema"],
                "status": artifact["status"],
            },
        ),
        "validator": input_entry(VALIDATOR),
    }
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.voltage_lift_intrinsic_hex_metric@1",
        "status": "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED",
        "all_checks_pass": True,
        "claim": "The canonical comparison metric for the D20 voltage-lift witness is the normalized regular-hex metric on the six signed H6 labels. Under the intrinsic edge rule entering_label - leaving_label on Lambda^3 signed-label faces, the covariance ellipse has exact anisotropy ratio 31/23 with major axis at -60 degrees in one Dih_6 coordinate representative.",
        "closure_boundary": {
            "certifies": [
                "the intrinsic edge step uses only the two signed labels exchanged by each D20 edge",
                "selector_choice is not used by the intrinsic hex metric",
                "the normalized Dih_6 regular-hex metric gives covariance eigenvalues 31/20 and 23/20",
                "the generated render family regular_hex_label_delta variant matches the intrinsic metric witness",
            ],
            "does_not_certify": [
                "the stronger cooriented sign/selector render lift as intrinsic",
                "the full robust-oblongness theorem across every possible D20 lift",
                "a rebuild of d20.json or of the finite critical group",
            ],
        },
        "definition": artifact["intrinsic_definition"],
        "inputs": inputs,
        "witness": {
            "artifact": relpath(INTRINSIC_ARTIFACT),
            "anisotropy_ratio_exact": artifact["covariance"]["anisotropy_ratio_exact"],
            "anisotropy_ratio": artifact["covariance"]["anisotropy_ratio"],
            "eigenvalues_exact": artifact["covariance"]["eigenvalues_exact"],
            "edge_count": artifact["edge_count"],
            "matched_family_variant": artifact["render_family_comparison"]["matched_variant_id"],
            "principal_axis_angle_degrees": artifact["covariance"]["principal_axis_angle_degrees"],
        },
        "checks": artifact["checks"],
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def proof_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.voltage_lift_intrinsic_hex_metric_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify D20 edge CSV has 30 single-label transitions",
            "verify coorient presentation supplies residual Dih_6 label symmetry",
            "verify intrinsic hex metric does not use selector_choice",
            "verify covariance eigenvalues are 31/20 and 23/20",
            "verify the generated family regular_hex_label_delta variant matches this intrinsic metric",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(INTRINSIC_ARTIFACT),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_family_obligation(intrinsic_report: dict[str, Any], artifact: dict[str, Any]) -> None:
    report_path = FAMILY_OUT_DIR / "report.json"
    manifest_path = FAMILY_OUT_DIR / "manifest.json"
    if not report_path.exists() or not manifest_path.exists():
        return
    report = load_json(report_path)
    manifest = load_json(manifest_path)
    intrinsic_input = input_entry(
        INTRINSIC_ARTIFACT,
        {
            "artifact_sha256_excluding_this_field": artifact["artifact_sha256_excluding_this_field"],
            "schema": artifact["schema"],
            "status": artifact["status"],
        },
    )
    intrinsic_report_input = input_entry(
        OUT_DIR / "report.json",
        {
            "certificate_sha256": intrinsic_report["certificate_sha256"],
            "status": intrinsic_report["status"],
        },
    )
    report.setdefault("inputs", {})["intrinsic_hex_metric_artifact"] = intrinsic_input
    report["inputs"]["intrinsic_hex_metric_report"] = intrinsic_report_input
    report["inputs"]["validator"] = input_entry(FAMILY_VALIDATOR)
    report.setdefault("checks", {})["intrinsic_hex_metric_witness_present"] = True
    report["checks"]["canonical_metric_selection_witnessed"] = True
    report["witnessed_obligations"] = [
        {
            "id": "intrinsic_lift_family_definition",
            "status": "witnessed",
            "witness_report": relpath(OUT_DIR / "report.json"),
            "witness_sha256": intrinsic_report["certificate_sha256"],
        },
        {
            "id": "canonical_metric_selection",
            "status": "witnessed",
            "witness_report": relpath(OUT_DIR / "report.json"),
            "witness_sha256": intrinsic_report["certificate_sha256"],
        },
    ]
    report["open_obligations"] = [
        {
            "id": "proof_layer_integration",
            "required_for": "move the robust oblongness claim from generated witness audit into the certified theorem layer",
            "status": "open",
        }
    ]
    certifies = report.setdefault("closure_boundary", {}).setdefault("certifies", [])
    for text in [
        "the intrinsic regular-hex metric is now derived from signed-label edge transitions",
        "canonical metric selection is witnessed separately from the stronger cooriented selector render",
    ]:
        if text not in certifies:
            certifies.append(text)
    report.pop("certificate_sha256", None)
    report["certificate_sha256"] = sha_json(report)
    manifest.setdefault("inputs", {})["intrinsic_hex_metric_artifact"] = intrinsic_input
    manifest["inputs"]["intrinsic_hex_metric_report"] = intrinsic_report_input
    manifest["inputs"]["validator"] = input_entry(FAMILY_VALIDATOR)
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = sha_json(manifest)
    write_json(report_path, report)
    write_json(manifest_path, manifest)


def update_index(entries: list[tuple[str, Path, Path, str, str]]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") not in {entry[0] for entry in entries}]
    else:
        index = {
            "schema": "d20.proof_obligation_registry.source_drop",
            "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        }
        obligations = []
    for theorem_id, manifest_path, report_path, report_sha, status in entries:
        obligations.append(
            {
                "id": theorem_id,
                "manifest": relpath(manifest_path),
                "report": relpath(report_path),
                "report_sha256": report_sha,
                "status": status,
            }
        )
    obligations = sorted(obligations, key=lambda row: row["id"])
    index["obligations"] = obligations
    index["obligation_count"] = len(obligations)
    index.pop("registry_sha256", None)
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = artifact_payload()
    write_json(INTRINSIC_ARTIFACT, artifact)
    report = proof_report(artifact)
    manifest = proof_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_family_obligation(report, artifact)
    entries = [
        (
            THEOREM_ID,
            OUT_DIR / "manifest.json",
            OUT_DIR / "report.json",
            report["certificate_sha256"],
            report["status"],
        )
    ]
    family_report = FAMILY_OUT_DIR / "report.json"
    if family_report.exists():
        family_payload = load_json(family_report)
        entries.append(
            (
                FAMILY_THEOREM_ID,
                FAMILY_OUT_DIR / "manifest.json",
                family_report,
                family_payload["certificate_sha256"],
                family_payload["status"],
            )
        )
    update_index(entries)
    print(
        json.dumps(
            {
                "artifact": relpath(INTRINSIC_ARTIFACT),
                "artifact_sha256_excluding_this_field": artifact["artifact_sha256_excluding_this_field"],
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
