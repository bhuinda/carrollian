from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, LAYERS, ROOT


THEOREM_ID = "minimal_composite_null_supports_transport"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility" / "report.json"
)
FULL_A985_LIFT = LAYERS / "drinfeld" / "full_a985_lift.json"

TARGET_MINIMAL_COMPOSITES = [[6, 26], [25, 26]]
PRIMITIVE_SUPPORT = [33]


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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sector_profiles_by_id(full_lift: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(profile["sector"]): profile
        for profile in full_lift["gluing_and_sector_profiles"]["sector_profiles"]
    }


def transport_rank(left: list[int], right: list[int], profiles: dict[int, dict[str, Any]]) -> dict[str, Any]:
    intersection = sorted(set(left).intersection(right))
    return {
        "left": left,
        "right": right,
        "intersection": intersection,
        "rank": int(sum(int(profiles[sector]["block_dimension"]) ** 2 for sector in intersection)),
    }


def support_profile(support: list[int], profiles: dict[int, dict[str, Any]]) -> dict[str, Any]:
    rows = [profiles[sector] for sector in support]
    block_dimensions = [int(row["block_dimension"]) for row in rows]
    active_objects = sorted({obj for row in rows for obj in row.get("active_objects", [])})
    active_cy_sectors = sorted({obj for row in rows for obj in row.get("active_cy_sectors", [])})
    return {
        "support": support,
        "block_dimensions": block_dimensions,
        "active_objects": active_objects,
        "active_cy_sectors": active_cy_sectors,
        "internal_dimension_sum_d_squared": int(sum(dim * dim for dim in block_dimensions)),
        "permutation_rank_sum": int(sum(int(row.get("permutation_rank", 0)) for row in rows)),
        "permutation_multiplicity_sum": int(
            sum(int(row.get("permutation_multiplicity", 0)) for row in rows)
        ),
        "individual_public_nonzero_count_sum_before_cancellation": int(
            sum(int(row.get("q42_nonzero_count", 0)) + int(row.get("q12_nonzero_count", 0)) for row in rows)
        ),
        "loop_coordinate_support_total": int(
            sum(int(row.get("loop_coordinate_support_total", 0)) for row in rows)
        ),
        "pre_idempotent_support_total": int(
            sum(int(row.get("pre_idempotent_support_size", 0)) for row in rows)
        ),
        "identity_coefficients_signed_by_sector": {
            str(sector): profiles[sector].get("identity_coefficients_signed")
            for sector in support
        },
        "spectral_signature_by_sector": {
            str(sector): profiles[sector].get("spectral_signature")
            for sector in support
        },
    }


def classification_for(support: list[int]) -> tuple[str, str]:
    if support == [25, 26]:
        return (
            "pure_Sminus_public_zero_superselection_doublet_isolated_from_pi33",
            "same active object S-, two scalar central blocks, nonzero self transport rank 2, zero mixed transport to Pi_33",
        )
    if support == [6, 26]:
        return (
            "mixed_S_channel_public_zero_superselection_support_isolated_from_pi33",
            "active objects S- and S+, one M2 block and one scalar block, nonzero self transport rank 5, zero mixed transport to Pi_33 despite object-level S+ overlap",
        )
    if support == [33]:
        return (
            "primitive_support_exact_residual_support",
            "unique primitive public-zero support selected by the certified sector-33 height transport",
        )
    return (
        "public_zero_composite_with_primitive_residual_component",
        "Boolean public-zero sector sum containing a previously classified component",
    )


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
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    admissibility = load_json(ADMISSIBILITY_REPORT)
    full_lift = load_json(FULL_A985_LIFT)
    profiles = sector_profiles_by_id(full_lift)
    derived = admissibility.get("derived", {})

    primitive_record = support_profile(PRIMITIVE_SUPPORT, profiles)
    primitive_record["self_transport"] = transport_rank(PRIMITIVE_SUPPORT, PRIMITIVE_SUPPORT, profiles)
    primitive_record["classification"], primitive_record["classification_reason"] = classification_for(
        PRIMITIVE_SUPPORT
    )

    records = []
    for support in TARGET_MINIMAL_COMPOSITES:
        record = support_profile(support, profiles)
        record["self_transport"] = transport_rank(support, support, profiles)
        record["transport_to_pi33"] = transport_rank(support, PRIMITIVE_SUPPORT, profiles)
        record["transport_from_pi33"] = transport_rank(PRIMITIVE_SUPPORT, support, profiles)
        record["couples_to_pi33"] = bool(
            record["transport_to_pi33"]["rank"] != 0
            or record["transport_from_pi33"]["rank"] != 0
        )
        record["not_gauge"] = bool(
            record["self_transport"]["rank"] > 0 and record["permutation_rank_sum"] > 0
        )
        record["classification"], record["classification_reason"] = classification_for(support)
        record["object_channel_overlap_with_pi33"] = sorted(
            set(record["active_objects"]).intersection(primitive_record["active_objects"])
        )
        records.append(record)

    boolean_public_zero_supports = derived.get("nonzero_public_zero_idempotent_supports", [])
    minimal_supports = derived.get("inclusion_minimal_nonzero_public_zero_idempotents", [])
    non_pi33_minimal_supports = [support for support in minimal_supports if support != PRIMITIVE_SUPPORT]

    checks = {
        "admissibility_report_is_certified": admissibility.get("status")
        == "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        and admissibility.get("all_checks_pass") is True,
        "upstream_pairwise_orthogonal_sector_idempotents": admissibility.get("checks", {}).get(
            "sector_idempotents_are_pairwise_orthogonal"
        )
        is True,
        "boolean_public_zero_supports_match_upstream": boolean_public_zero_supports
        == [[6, 26], [25, 26], [33], [6, 26, 33], [25, 26, 33]],
        "minimal_non_pi33_composites_match_targets": non_pi33_minimal_supports
        == TARGET_MINIMAL_COMPOSITES,
        "primitive_pi33_self_transport_rank_is_4": primitive_record["self_transport"]["rank"] == 4,
        "minimal_composite_self_transport_ranks_are_nonzero": {
            ",".join(map(str, record["support"])): record["self_transport"]["rank"]
            for record in records
        }
        == {"6,26": 5, "25,26": 2},
        "minimal_composites_have_zero_transport_to_and_from_pi33": all(
            record["transport_to_pi33"]["rank"] == 0
            and record["transport_from_pi33"]["rank"] == 0
            for record in records
        ),
        "minimal_composites_are_not_gauge_zero": all(record["not_gauge"] for record in records),
        "mixed_s_channel_overlap_does_not_imply_pi33_transport": next(
            record for record in records if record["support"] == [6, 26]
        )["object_channel_overlap_with_pi33"]
        == ["S+"]
        and next(record for record in records if record["support"] == [6, 26])["couples_to_pi33"]
        is False,
        "minimal_composites_classified_as_superselection_not_gauge": [
            record["classification"] for record in records
        ]
        == [
            "mixed_S_channel_public_zero_superselection_support_isolated_from_pi33",
            "pure_Sminus_public_zero_superselection_doublet_isolated_from_pi33",
        ],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_CLASSIFIED"
        if all_checks_pass
        else "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.minimal_composite_null_supports_transport.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The two minimal non-Pi_33 public-zero composite idempotent supports have nonzero self-transport "
            "and zero mixed transport to Pi_33. Thus neither is gauge zero; both are public-zero "
            "superselection supports isolated from the primitive residual support Pi_33."
        ),
        "definition": {
            "transport_rank_formula": (
                "For Boolean sums E_C=sum_{s in C} e_s of certified pairwise orthogonal central sector "
                "idempotents, dim(E_C A985 E_D)=sum_{s in C intersection D} dim(s)^2."
            ),
            "not_gauge_zero": "A public-zero support with positive self-transport rank and positive permutation rank.",
            "isolated_from_pi33": "Both E_C A985 e_33 and e_33 A985 E_C have rank zero.",
            "superselection_null_support": (
                "A public-zero support with nonzero internal transport that is isolated from the primitive "
                "height-residual support."
            ),
        },
        "inputs": {
            "sector_idempotent_support_admissibility_report": {
                "path": rel(ADMISSIBILITY_REPORT),
                "sha256": sha_file(ADMISSIBILITY_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "derived": {
            "primitive_support_pi33": primitive_record,
            "minimal_non_pi33_composite_supports": TARGET_MINIMAL_COMPOSITES,
            "minimal_non_pi33_composite_transport_classification": records,
            "transport_components": {
                "primitive_residual_atom": [33],
                "pure_Sminus_superselection_null_doublet": [25, 26],
                "mixed_S_channel_superselection_null_support": [6, 26],
            },
            "self_transport_ranks": {
                ",".join(map(str, record["support"])): record["self_transport"]["rank"]
                for record in records
            },
            "transport_to_pi33_ranks": {
                ",".join(map(str, record["support"])): record["transport_to_pi33"]["rank"]
                for record in records
            },
            "transport_from_pi33_ranks": {
                ",".join(map(str, record["support"])): record["transport_from_pi33"]["rank"]
                for record in records
            },
        },
        "interpretation": {
            "pure_Sminus_doublet": (
                "{25,26} is a pure S- public-zero superselection doublet: two scalar blocks, self-rank 2, "
                "and zero transport to/from Pi_33."
            ),
            "mixed_S_channel_support": (
                "{6,26} is a mixed S-/S+ public-zero superselection support: one M2 block plus one scalar "
                "block, self-rank 5, and zero transport to/from Pi_33 despite object-level S+ overlap."
            ),
            "public_zero_fiber": (
                "The public-zero fiber splits into one primitive residual atom Pi_33 and two minimal composite "
                "superselection supports."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Promote the two composite superselection labels into the finite boundary charge/flux balance "
            "state so hidden null sectors cannot be mistaken for public zero."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.minimal_composite_null_supports_transport_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "consume the certified Boolean public-zero idempotent support enumeration",
            "verify the two minimal non-Pi_33 composite supports are {6,26} and {25,26}",
            "apply the central-sector transport rank formula to the composite supports",
            "verify both minimal composites have positive self-transport rank",
            "verify both minimal composites have zero transport rank to and from Pi_33",
            "classify the composites as isolated public-zero superselection supports, not gauge zero",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
