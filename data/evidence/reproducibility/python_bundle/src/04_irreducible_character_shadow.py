import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
from pathlib import Path
import argparse, json
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out) / "04_irreducible_character_shadow"; out.mkdir(parents=True, exist_ok=True)

    d20 = json.loads(Path(args.d20).read_text())
    lift = d20["layer_certificates"]["06_drinfeld_full_A985_lift"]
    ict = lift["irreducible_character_table"]
    wd = d20["layer_certificates"]["05_drinfeld_wedderburn_trace"]
    dims = lift["Wedderburn_recovery"]["block_dimensions_by_sector"]

    rows = []
    for i, dim in enumerate(dims):
        s = wd["sector_profiles"][i]
        rows.append({"sector": i, "block_dimension_d": dim, "unit_character_value": ict["unit_character_values"][i], "unit_character_equals_d": ict["unit_character_values"][i] == dim, "active_objects": ",".join(s.get("active_objects", [])), "q42_nonzero_count": s.get("q42_nonzero_count"), "q12_nonzero_count": s.get("q12_nonzero_count")})
    hist_rows = [{"support_size": int(k), "sector_count": v} for k,v in sorted(ict["character_support_histogram"].items(), key=lambda kv:int(kv[0]))]
    checks = [
        {"check": "shape_39_985", "pass": ict["shape"] == [39,985], "value": str(ict["shape"])},
        {"check": "unit_chars_equal_dims", "pass": ict["unit_character_values_equal_block_dimensions"], "value": ict["unit_character_values_equal_block_dimensions"]},
        {"check": "central_character_diagonal", "pass": ict["central_character_on_primitive_idempotents_is_diagonal"], "value": ict["central_character_on_primitive_idempotents_is_diagonal"]},
        {"check": "regular_character_reconstructs_regular_trace", "pass": ict["regular_character_reconstructs_regular_trace_on_all_985_basis_relations"], "value": ict["regular_character_reconstructs_regular_trace_on_all_985_basis_relations"]},
    ]
    write_csv(out / "irreducible_sector_expression_table.csv", rows)
    write_csv(out / "character_support_histogram.csv", hist_rows)
    write_csv(out / "validation_checks.csv", checks)
    cert = {"schema": "repro.irreducible_character_shadow@1", "status": "PASS" if all(c["pass"] for c in checks) else "FAIL", "checks": checks}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
