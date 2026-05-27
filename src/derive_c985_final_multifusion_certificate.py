from __future__ import annotations

import json
from typing import Any

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_final_multifusion_certificate"
STATUS = "C985_FINITE_SEMISIMPLE_MULTIFUSION_CATEGORY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
CORE_A985_JSON = ROOT / "data" / "core" / "a985.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_c985_final_multifusion_certificate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_final_multifusion_certificate.py"

REPORTS = {
    "typed_registry": PROOF_ROOT / "c985_typed_simple_object_registry" / "report.json",
    "fusion_multiplicity": PROOF_ROOT / "c985_fusion_multiplicity_typing" / "report.json",
    "associator_oracle": PROOF_ROOT / "c985_associator_rebracketing_oracle" / "report.json",
    "unit_tensor_laws": PROOF_ROOT / "c985_unit_tensor_laws" / "report.json",
    "unit_triangle": PROOF_ROOT / "c985_unit_triangle_coherence" / "report.json",
    "duality_support": PROOF_ROOT / "c985_duality_support" / "report.json",
    "pentagon": PROOF_ROOT / "c985_pentagon_chain_normal_form" / "report.json",
    "zigzag": PROOF_ROOT / "c985_zigzag_identities" / "report.json",
}

EXPECTED_STATUSES = {
    "typed_registry": "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
    "fusion_multiplicity": "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
    "associator_oracle": "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
    "unit_tensor_laws": "C985_UNIT_TENSOR_LAWS_CERTIFIED",
    "unit_triangle": "C985_UNIT_TRIANGLE_COHERENCE_CERTIFIED",
    "duality_support": "C985_DUALITY_SUPPORT_CERTIFIED",
    "pentagon": "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
    "zigzag": "C985_ZIGZAG_IDENTITIES_CERTIFIED",
}


def report_payloads() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, path in REPORTS.items()}


def build_payloads() -> dict[str, Any]:
    reports = report_payloads()
    core = load_json(CORE_A985_JSON)
    registry_witness = reports["typed_registry"].get("witness", {})
    fusion_witness = reports["fusion_multiplicity"].get("witness", {})
    pentagon_witness = reports["pentagon"].get("witness", {})
    zigzag_witness = reports["zigzag"].get("witness", {})

    layer_statuses = {name: reports[name].get("status") for name in REPORTS}
    layer_hashes = {name: reports[name].get("certificate_sha256") for name in REPORTS}
    all_layer_statuses_match = all(layer_statuses[name] == EXPECTED_STATUSES[name] for name in EXPECTED_STATUSES)

    checks = {
        "all_required_c985_layers_certified": all_layer_statuses_match,
        "simple_count_is_985": int(registry_witness.get("relation_count", 0)) == 985,
        "object_count_is_6": len(registry_witness.get("object_labels", [])) == 6,
        "finite_semisimple_skeleton_certified": "formal semisimple skeletal C-linear category before tensor coherence"
        in reports["typed_registry"].get("closure_boundary", {}).get("certifies", []),
        "fusion_multiplicities_match_a985": "agreement of the derived fusion tensor with the existing A985 tensor"
        in reports["fusion_multiplicity"].get("closure_boundary", {}).get("certifies", []),
        "k0_support_is_1414965": int(fusion_witness.get("tensor_support", 0)) == 1414965,
        "k0_coefficient_total_is_2537360": int(fusion_witness.get("coefficient_total", 0)) == 2537360,
        "associator_oracle_certifies_rebracketing": "deterministic left-bracketing to length-three-chain map"
        in reports["associator_oracle"].get("closure_boundary", {}).get("certifies", []),
        "pentagon_coherence_certified": "pentagon coherence for the certified associator rebracketing oracle"
        in reports["pentagon"].get("closure_boundary", {}).get("certifies", []),
        "pentagon_chain_count_matches": int(
            pentagon_witness.get("address_counts", {}).get("exact_length_four_chain_count", 0)
        )
        == 16837352591360,
        "decomposable_unit_certified": "six identity orbitals as decomposable tensor-unit summands"
        in reports["unit_tensor_laws"].get("closure_boundary", {}).get("certifies", []),
        "unit_triangle_certified": "unit triangle coherence on every one of the 2,537,360 fusion basis rows"
        in reports["unit_triangle"].get("closure_boundary", {}).get("certifies", []),
        "transpose_duality_support_certified": "transpose dual candidate for every C985 simple"
        in reports["duality_support"].get("closure_boundary", {}).get("certifies", []),
        "zigzag_identities_certified": "both zig-zag identities for every simple generator"
        in reports["zigzag"].get("closure_boundary", {}).get("certifies", []),
        "rigidity_certified": "rigidity of the certified semisimple monoidal C985 skeleton"
        in reports["zigzag"].get("closure_boundary", {}).get("certifies", []),
        "zigzag_failure_count_is_zero": int(zigzag_witness.get("zigzag_failure_count", -1)) == 0,
        "core_a985_certificate_present": core.get("status") is not None
        and core.get("certificate_sha256") is not None,
    }

    theorem_certificate = {
        "schema": "c985.final_multifusion_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_FINAL_MULTIFUSION_CERTIFICATE_PROVISIONAL",
        "theorem": (
            "C985 is a finite semisimple rigid C-linear monoidal category with "
            "decomposable unit; equivalently, C985 is a finite semisimple "
            "multi-fusion category, and K0(C985) ~= A985 as based rings."
        ),
        "layer_statuses": layer_statuses,
        "layer_certificate_sha256": layer_hashes,
        "checks": checks,
        "witness": {
            "simple_count": int(registry_witness.get("relation_count", 0)),
            "object_labels": registry_witness.get("object_labels", []),
            "identity_relations": registry_witness.get("identity_relations", []),
            "fusion_tensor_support": int(fusion_witness.get("tensor_support", 0)),
            "fusion_coefficient_total": int(fusion_witness.get("coefficient_total", 0)),
            "pentagon_length_four_chain_count": int(
                pentagon_witness.get("address_counts", {}).get("exact_length_four_chain_count", 0)
            ),
            "zigzag_simple_count": int(zigzag_witness.get("simple_count", 0)),
            "zigzag_failure_count": int(zigzag_witness.get("zigzag_failure_count", -1)),
        },
        "downstream_not_required_for_multifusion": [
            "spherical structure",
            "pivotal structure",
            "unitarity",
            "braiding",
            "ribbon twist",
            "Drinfeld center modular data",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.final_multifusion_certificate@1",
        "status": theorem_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": theorem_certificate["theorem"],
        "stage_protocol": {
            "draft": "collect all certified C985 proof-obligation reports",
            "witness": "record layer statuses, hashes, and theorem-critical counts",
            "coherence": "check finite semisimple skeleton, fusion tensor, associator, pentagon, units, triangles, and zig-zags",
            "closure": "certify the finite semisimple multi-fusion category theorem for C985",
            "emit": "emit final C985 certificate and downstream-not-required boundary",
        },
        "inputs": {
            **{
                name: input_entry(
                    path,
                    {
                        "status": reports[name].get("status"),
                        "certificate_sha256": reports[name].get("certificate_sha256"),
                    },
                )
                for name, path in REPORTS.items()
            },
            "core_a985": input_entry(
                CORE_A985_JSON,
                {
                    "status": core.get("status"),
                    "certificate_sha256": core.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "theorem_certificate": relpath(OUT_DIR / "theorem_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": theorem_certificate["witness"],
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "finite semisimple C-linear category with 985 simples",
                "bilinear tensor product with K0(C985) ~= A985",
                "associator satisfying pentagon coherence",
                "six-summand decomposable unit satisfying unit triangle coherence",
                "transpose duality with evaluation/coevaluation satisfying zig-zag identities",
                "finite semisimple multi-fusion category status for C985",
            ],
            "does_not_certify_because_not_required": theorem_certificate[
                "downstream_not_required_for_multifusion"
            ],
        },
        "next_highest_yield_item": (
            "Downstream work can now target optional structures: pivotal/spherical "
            "normalization, unitarity, braiding, or Drinfeld-center modular data."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.final_multifusion_certificate_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "require every prerequisite C985 proof-obligation status",
            "check finite simple count and six-object decomposable unit",
            "check K0 fusion tensor agreement with A985",
            "check pentagon and unit triangle coherence certificates",
            "check zig-zag identities and rigidity certificate",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "theorem_certificate": theorem_certificate,
        "report": report,
        "manifest": manifest,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "theorem_certificate.json", payloads["theorem_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
