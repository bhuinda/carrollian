from __future__ import annotations

from pathlib import Path
from .derive_d20_etendue import derive as derive_etendue
from .derive_d20_complement_pairs import derive as derive_complement
from .derive_d20_snell import derive as derive_snell
from .derive_d20_caustic_resolvent import derive as derive_caustic
from .d20_optics_common import sha_json, write_json


def derive(root: Path, out_json: Path) -> dict:
    etendue = derive_etendue(root / "generated/d20_etendue.npz", root / "generated/d20_etendue_report.json")
    complement = derive_complement(root / "generated/d20_complement_pairs.npz", root / "generated/d20_complement_pairs_report.json")
    snell = derive_snell(root / "generated/d20_snell.npz", root / "generated/d20_snell_report.json")
    caustic = derive_caustic(root / "layers/17_wu_golay_quintic_resolvent/certificate.json", root / "layers/18_canonical_24_syzygy_frame/certificate.json", root / "generated/generated_sector_alignment_report.json", root / "generated/d20_caustic_resolvent_report.json")
    ok = all(r["constructor_status"].endswith("PASS") for r in [etendue, complement, snell, caustic])
    report = {
        "schema": "d20.optics.all@1",
        "constructor_status": "D20_OPTICS_PASS" if ok else "D20_OPTICS_PARTIAL",
        "object": "d20",
        "ultimate_concept": "d20 is the normalized public concept; Code(d20)=A985 is the hidden tensor body.",
        "subreports": {
            "etendue": etendue,
            "complement_pairs": complement,
            "snell": snell,
            "caustic_resolvent": caustic,
        },
        "summary": {
            "E_d20": etendue["E_d20"],
            "epsilon0": etendue["epsilon0"],
            "E_d20_over_epsilon0": etendue["E_d20_over_epsilon0"],
            "complement_product_over_epsilon0_squared": complement["product_over_epsilon0_squared"],
            "snell_verified": snell["all_checks_pass"],
            "caustic_resolvent_status": caustic["constructor_status"],
        },
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    write_json(out_json, report)
    return report
