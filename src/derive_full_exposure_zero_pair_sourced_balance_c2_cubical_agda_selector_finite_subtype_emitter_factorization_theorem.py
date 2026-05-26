from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
)
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge"
    / "report.json"
)
SHARED_EMITTER_SOURCE = ROOT / "src" / "c2_selector_finite_subtype_emitter.py"

FINITE_SUBTYPE_GENERATORS = [
    {
        "name": "singletons",
        "module": "src.derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_theorem",
        "path": ROOT
        / "src"
        / "derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_theorem.py",
        "report": D20_INVARIANTS
        / "theorems"
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons"
        / "report.json",
        "certified_status": "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_CERTIFIED",
    },
    {
        "name": "lazy63",
        "module": "src.derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_theorem",
        "path": ROOT
        / "src"
        / "derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_theorem.py",
        "report": D20_INVARIANTS
        / "theorems"
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
        / "report.json",
        "certified_status": "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED",
    },
    {
        "name": "paired_lazy480",
        "module": "src.derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_theorem",
        "path": ROOT
        / "src"
        / "derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_theorem.py",
        "report": D20_INVARIANTS
        / "theorems"
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480"
        / "report.json",
        "certified_status": "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED",
    },
    {
        "name": "raw543",
        "module": "src.derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_theorem",
        "path": ROOT
        / "src"
        / "derive_full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_theorem.py",
        "report": D20_INVARIANTS
        / "theorems"
        / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543"
        / "report.json",
        "certified_status": "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_CERTIFIED",
    },
]


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
    return json.loads(path.read_text(encoding="utf-8"))


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
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generator_row(bridge: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    module = importlib.import_module(str(spec["module"]))
    report = load_json(spec["report"])
    source_path = module.CUBICAL_AGDA_SOURCE
    interface_path = module.CUBICAL_AGDA_INTERFACE
    generated_source = module.generate_agda_source(bridge)
    current_source = source_path.read_text(encoding="utf-8")
    generator_text = spec["path"].read_text(encoding="utf-8")
    interface_exists = interface_path.exists()
    return {
        "name": spec["name"],
        "generator": {
            "path": rel(spec["path"]),
            "sha256": sha_file(spec["path"]),
            "uses_shared_emitter": (
                "generate_selector_finite_subtype_agda" in generator_text
                or "generate_singleton_finite_subtype_agda" in generator_text
            ),
        },
        "report": {
            "path": rel(spec["report"]),
            "sha256": sha_file(spec["report"]),
            "status": report.get("status"),
            "all_checks_pass": report.get("all_checks_pass"),
        },
        "agda_source": {
            "path": rel(source_path),
            "sha256": sha_file(source_path),
            "line_count": len(current_source.splitlines()),
            "generated_matches_current": generated_source == current_source,
        },
        "agda_interface": {
            "path": rel(interface_path),
            "sha256": sha_file(interface_path) if interface_exists else None,
            "fresh_for_source": (
                interface_exists
                and interface_path.stat().st_size > 0
                and interface_path.stat().st_mtime >= source_path.stat().st_mtime
            ),
        },
        "expected_status": spec["certified_status"],
    }


def build_theorem() -> dict[str, Any]:
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    emitter_text = SHARED_EMITTER_SOURCE.read_text(encoding="utf-8")
    rows = [generator_row(bridge, spec) for spec in FINITE_SUBTYPE_GENERATORS]
    checks = {
        "univalent_foundation_bridge_is_certified": bridge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED"
        and bridge.get("all_checks_pass") is True,
        "shared_emitter_source_exists": SHARED_EMITTER_SOURCE.exists(),
        "shared_emitter_exposes_non_singleton_emitter": (
            "def generate_selector_finite_subtype_agda" in emitter_text
        ),
        "shared_emitter_exposes_singleton_emitter": (
            "def generate_singleton_finite_subtype_agda" in emitter_text
        ),
        "all_generators_use_shared_emitter": all(
            row["generator"]["uses_shared_emitter"] for row in rows
        ),
        "all_prior_finite_subtype_reports_certified": all(
            row["report"]["status"] == row["expected_status"]
            and row["report"]["all_checks_pass"] is True
            for row in rows
        ),
        "shared_emitter_reproduces_certified_agda_sources": all(
            row["agda_source"]["generated_matches_current"] for row in rows
        ),
        "all_agda_interfaces_remain_fresh": all(
            row["agda_interface"]["fresh_for_source"] for row in rows
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization",
        "status": status,
        "object": "d20",
        "claim": (
            "The singleton, lazy63, paired-lazy480, and raw543 Cubical Agda finite-subtype "
            "generators are factored through one shared emitter without changing their certified Agda sources."
        ),
        "inputs": {
            "c2_univalent_foundation_bridge_report": {
                "path": rel(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT),
                "sha256": sha_file(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT),
            },
            "shared_emitter_source": {
                "path": rel(SHARED_EMITTER_SOURCE),
                "sha256": sha_file(SHARED_EMITTER_SOURCE),
            },
            "finite_subtype_generators": [
                {
                    "name": row["name"],
                    "path": row["generator"]["path"],
                    "sha256": row["generator"]["sha256"],
                }
                for row in rows
            ],
        },
        "derived": {
            "factorized_generators": rows,
            "factorized_generator_count": len(rows),
            "agda_source_change_policy": (
                "generated source equality is byte-for-byte against current certified Agda files, so "
                "existing typechecked interface artifacts remain valid"
            ),
        },
        "interpretation": {
            "what_this_proves": [
                "the finite-subtype proof generators now share one source emitter",
                "the shared emitter reproduces all four certified Agda modules exactly",
                "no large Agda re-typecheck is required for this refactor because the Agda source files did not change",
            ],
            "what_remains": [
                "replace large constructor-normal forms with a compact indexed-vector proof layer",
                "use the shared emitter as the base for future selector-fiber finite subtype proofs",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Replace the large generated FinData constructor normal forms with a compact indexed-vector "
            "proof layer to reduce Agda source size and typecheck time."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem_manifest",
        "theorem_id": THEOREM_ID,
        "status": report["status"],
        "report": rel(out_dir / "report.json"),
        "inputs": report["inputs"],
        "checks": report["checks"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
