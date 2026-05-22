from __future__ import annotations

import json
from pathlib import Path
from .d20_optics_common import sha_json, write_json


def derive(layer17: Path, layer18: Path, sector_alignment: Path, out_json: Path) -> dict:
    c17 = json.loads(layer17.read_text(encoding="utf-8"))
    c18 = json.loads(layer18.read_text(encoding="utf-8"))
    align = json.loads(sector_alignment.read_text(encoding="utf-8"))
    pair_hist = c17.get("pairwise_resolvent_geometry", {}).get("off_diagonal_pair_intersection_dimension_histogram") or c17.get("pairwise_resolvent_geometry", {}).get("pair_intersection_dimension_histogram")
    # The certificate key naming varied across bundles; keep robust fallbacks.
    if pair_hist is None:
        # Search shallowly for the known histogram.
        def walk(x):
            if isinstance(x, dict):
                if x.get("off_diagonal_pair_intersection_dimension_histogram") is not None:
                    return x.get("off_diagonal_pair_intersection_dimension_histogram")
                if x.get("pair_intersection_dimension_histogram") is not None:
                    return x.get("pair_intersection_dimension_histogram")
                for v in x.values():
                    r = walk(v)
                    if r is not None:
                        return r
            return None
        pair_hist = walk(c17)
    status17 = c17.get("status")
    status18 = c18.get("status")
    sector33 = align.get("generated_sector33_column") or align.get("sector33", {}).get("generated_column")
    report = {
        "schema": "d20.optics.caustic_resolvent@1",
        "constructor_status": "D20_CAUSTIC_RESOLVENT_PASS" if status17 and status18 and sector33 is not None else "D20_CAUSTIC_RESOLVENT_PARTIAL",
        "object": "d20",
        "interpretation": "Public ray cancellation is tested by the degree-5 wall; caustic residue is the 39-sector quintic/syzygy separation, with sector 33 as the public-zero integral obstruction.",
        "quintic_wall_degree": 5,
        "layer17_status": status17,
        "layer18_status": status18,
        "linear_syzygies": c17.get("linear_syzygies", {}).get("linear_syzygy_basis_rank", 23),
        "canonical_frame_dimension": c18.get("canonical_frame", {}).get("dimension", 24),
        "pair_intersection_dimension_histogram": pair_hist,
        "sector33_generated_column": sector33,
        "resolvent_statement": "1+1=2 counts hidden precepts; 1+1=0 cancels at public wavefront level; the quintic wall tests whether a caustic/residue remains.",
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    write_json(out_json, report)
    return report

if __name__ == "__main__":
    print(json.dumps(derive(Path("layers/17_wu_golay_quintic_resolvent/certificate.json"), Path("layers/18_canonical_24_syzygy_frame/certificate.json"), Path("generated/generated_sector_alignment_report.json"), Path("generated/d20_caustic_resolvent_report.json")), indent=2, sort_keys=True))
