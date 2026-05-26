#!/usr/bin/env python3
"""
Hamming-Gaussian dual-distance / Krawtchouk audit.

This refines the Hamming-Gaussian morphism from signed sparse brute probes to a theorem-grade
finite invariant:

  dual distance d^perp = 8 at the Golay endpoint
  => every coordinate projection of size < 8 is uniform
  => every real coefficient sparse projection of support < 8 equals the independent Rademacher baseline
  => all extra Hamming-root convex-order obstruction below weight 8 vanishes at the endpoint.

The script builds H8 = RM(1,3), runs the same Type-II neighbor chain used in the earlier audits,
and computes MacWilliams/Krawtchouk dual weight enumerators plus affected support counts.
"""
from __future__ import annotations
from itertools import product, combinations
from math import comb, log2, sqrt, pi
from pathlib import Path
import csv, hashlib, json, os, zipfile

OUT = Path(__file__).resolve().parent
N = 24


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bits_to_int(bits):
    x = 0
    for i, b in enumerate(bits):
        if b:
            x |= 1 << i
    return x


def wt(x: int) -> int:
    return int(x).bit_count()


def gf2_rank(rows: list[int], n: int) -> int:
    rows = rows[:]
    rank = 0
    for col in range(n - 1, -1, -1):
        pivot = None
        for r in range(rank, len(rows)):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(len(rows)):
            if r != rank and ((rows[r] >> col) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def span_from_generators(gens: list[int]) -> list[int]:
    C = [0]
    for g in gens:
        C += [c ^ g for c in C]
        C = sorted(set(C))
    return C


def basis_from_code(C: list[int], n: int) -> list[int]:
    basis = []
    rank = 0
    target = int(round(log2(len(C))))
    for c in sorted(C):
        if c == 0:
            continue
        r = gf2_rank(basis + [c], n)
        if r > rank:
            basis.append(c)
            rank = r
        if rank == target:
            break
    return basis


def rm13_h8() -> list[int]:
    pts = list(product([0, 1], repeat=3))
    C = []
    for a in product([0, 1], repeat=3):
        for b in [0, 1]:
            bits = []
            for p in pts:
                val = (sum(ai * pi for ai, pi in zip(a, p)) + b) % 2
                bits.append(val)
            C.append(bits_to_int(bits))
    return sorted(set(C))


def direct_sum(codes: list[list[int]], lengths: list[int]) -> list[int]:
    res = [0]
    shift = 0
    for C, L in zip(codes, lengths):
        res = [r | (c << shift) for r in res for c in C]
        shift += L
    return sorted(set(res))


def vector_from_one_based_support(support: list[int]) -> int:
    x = 0
    for j in support:
        x |= 1 << (j - 1)
    return x


def type_ii_neighbor(C: list[int], x: int) -> list[int]:
    C0 = [c for c in C if wt(c & x) % 2 == 0]
    return sorted(set(C0 + [c ^ x for c in C0]))


def weight_hist(C: list[int], n: int = N) -> list[int]:
    h = [0] * (n + 1)
    for c in C:
        h[wt(c)] += 1
    return h


def self_orthogonal(C: list[int], n: int = N) -> bool:
    B = basis_from_code(C, n)
    return all(wt(a & b) % 2 == 0 for a in B for b in B)


def min_nonzero_weight(C: list[int]) -> int | None:
    vals = [wt(c) for c in C if c]
    return min(vals) if vals else None


def codeword_sha(C: list[int]) -> str:
    body = "\n".join(f"{c:06x}" for c in sorted(C)).encode()
    return sha256_bytes(body)


def krawtchouk(n: int, j: int, w: int) -> int:
    s = 0
    lo = max(0, j - (n - w))
    hi = min(j, w)
    for ell in range(lo, hi + 1):
        s += ((-1) ** ell) * comb(w, ell) * comb(n - w, j - ell)
    return s


def macwilliams_dual_counts(A: list[int], n: int = N) -> list[int]:
    size = sum(A)
    B = []
    for j in range(n + 1):
        total = sum(A[w] * krawtchouk(n, j, w) for w in range(n + 1))
        if total % size != 0:
            raise AssertionError(f"MacWilliams coefficient nonintegral j={j} total={total} size={size}")
        B.append(total // size)
    return B


def dual_distance_from_counts(B: list[int]) -> int | None:
    for i, v in enumerate(B):
        if i > 0 and v:
            return i
    return None


def support_mask_from_tuple(tup: tuple[int, ...]) -> int:
    m = 0
    for i in tup:
        m |= 1 << i
    return m


def affected_support_counts_by_roots(roots: list[int], n: int = N, kmax: int = 7) -> list[dict]:
    """Count k-supports containing at least one weight-4 root."""
    rows = []
    root_set = sorted(set(roots))
    for k in range(1, kmax + 1):
        total = comb(n, k)
        affected = 0
        if k >= 4 and root_set:
            for S in combinations(range(n), k):
                mask = support_mask_from_tuple(S)
                for r in root_set:
                    if (mask & r) == r:
                        affected += 1
                        break
        rows.append({
            "k": k,
            "total_supports": total,
            "affected_supports_containing_weight4_root": affected,
            "unaffected_supports": total - affected,
            "affected_fraction": affected / total if total else 0.0,
        })
    return rows


def build_stages():
    neighbor_supports = [
        [2,4,9,10,12,13,14,16,17,18,20,22],
        [3,4,9,13,15,16,19,20],
        [2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23],
    ]
    H8 = rm13_h8()
    C = direct_sum([H8, H8, H8], [8, 8, 8])
    stages = [("C0_H8_oplus_3", C, None)]
    for i, supp in enumerate(neighbor_supports, start=1):
        C = type_ii_neighbor(C, vector_from_one_based_support(supp))
        label = f"C{i}_neighbor_{i}" if i < 3 else "C3_Golay_endpoint"
        stages.append((label, C, supp))
    return stages


def stage_record(label: str, C: list[int], neighbor_support=None) -> dict:
    A = weight_hist(C)
    B = macwilliams_dual_counts(A)
    rank = gf2_rank(C, N)
    roots4 = [c for c in C if wt(c) == 4]
    dual_d = dual_distance_from_counts(B)
    d = min_nonzero_weight(C)
    affected = affected_support_counts_by_roots(roots4, N, 7)
    return {
        "label": label,
        "length": N,
        "size": len(C),
        "dimension": rank,
        "sha256_hex_words": codeword_sha(C),
        "minimum_distance": d,
        "dual_distance_from_macwilliams": dual_d,
        "self_orthogonal": self_orthogonal(C, N),
        "self_dual": rank == N // 2 and self_orthogonal(C, N),
        "doubly_even": all(wt(c) % 4 == 0 for c in C),
        "weight_enumerator": {str(i): v for i, v in enumerate(A) if v},
        "dual_weight_enumerator": {str(i): v for i, v in enumerate(B) if v},
        "macwilliams_self_dual_enumerator": A == B,
        "weight4_roots": len(roots4),
        "low_weight_dual_counts_1_to_7": {str(i): B[i] for i in range(1, 8)},
        "sparse_projection_uniform_for_all_supports_k_less_than_dual_distance": dual_d is not None and dual_d >= 8,
        "affected_support_counts_k_le_7": affected,
        "neighbor_support_one_based": neighbor_support,
    }


def write_csvs(stage_records: list[dict]):
    # Stage summary
    with (OUT / "dual_distance_stage_summary.csv").open("w", newline="") as f:
        fieldnames = [
            "stage", "size", "dimension", "min_distance", "dual_distance", "wt4_roots",
            "macwilliams_self_dual", "uniform_all_k_le_7", "sha256_hex_words"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in stage_records:
            w.writerow({
                "stage": rec["label"],
                "size": rec["size"],
                "dimension": rec["dimension"],
                "min_distance": rec["minimum_distance"],
                "dual_distance": rec["dual_distance_from_macwilliams"],
                "wt4_roots": rec["weight4_roots"],
                "macwilliams_self_dual": rec["macwilliams_self_dual_enumerator"],
                "uniform_all_k_le_7": rec["sparse_projection_uniform_for_all_supports_k_less_than_dual_distance"],
                "sha256_hex_words": rec["sha256_hex_words"],
            })
    # Affected support counts
    with (OUT / "affected_sparse_support_counts.csv").open("w", newline="") as f:
        fieldnames = ["stage", "k", "total_supports", "affected_supports_containing_weight4_root", "unaffected_supports", "affected_fraction"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in stage_records:
            for row in rec["affected_support_counts_k_le_7"]:
                rr = dict(row)
                rr["stage"] = rec["label"]
                w.writerow(rr)
    # Endpoint Krawtchouk/MacWilliams rows for j=0..8
    endpoint = stage_records[-1]
    with (OUT / "endpoint_krawtchouk_macwilliams_low_weight.csv").open("w", newline="") as f:
        fieldnames = ["j", "dual_weight_count_B_j"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for j in range(0, 9):
            w.writerow({"j": j, "dual_weight_count_B_j": endpoint["dual_weight_enumerator"].get(str(j), 0)})


def write_report(report: dict):
    lines = []
    lines.append("# Hamming Gaussian dual-distance / Krawtchouk audit\n")
    lines.append(f"Status: `{report['status']}`\n")
    lines.append("## Main theorem-grade finite bridge\n")
    lines.append("At the Golay endpoint, the MacWilliams/Krawtchouk dual enumerator has no weights `1..7` and first nonzero dual weight `8`. Because the endpoint is self-dual, this is the same as the extended Golay minimum distance. Therefore every projection to fewer than eight coordinates is uniform.\n")
    lines.append("Consequently, for every support `S` with `|S| < 8` and every real coefficient vector `a`,\n")
    lines.append("```text\nL_C(a,S)=sum_{i in S} a_i (-1)^{c_i}, c uniform in G24\n```\n")
    lines.append("has exactly the same distribution as the independent Rademacher sum\n")
    lines.append("```text\nL_Rad(a,S)=sum_{i in S} a_i eps_i.\n```\n")
    lines.append("This proves that the Golay endpoint removes all extra code-induced sparse signed projection obstructions below weight 8.\n")
    lines.append("## Stage summary\n")
    lines.append("| stage | min d | dual d | wt4 roots | affected k<=7 supports | uniform all k<=7 |\n")
    lines.append("|---|---:|---:|---:|---:|---:|\n")
    for rec in report["stages"]:
        affected_total = sum(r["affected_supports_containing_weight4_root"] for r in rec["affected_support_counts_k_le_7"])
        lines.append(f"| {rec['label']} | {rec['minimum_distance']} | {rec['dual_distance_from_macwilliams']} | {rec['weight4_roots']} | {affected_total} | {rec['sparse_projection_uniform_for_all_supports_k_less_than_dual_distance']} |\n")
    lines.append("\n## Endpoint low dual weights\n")
    ep = report["stages"][-1]
    lines.append("```json\n")
    lines.append(json.dumps(ep["low_weight_dual_counts_1_to_7"], indent=2))
    lines.append("\n```\n")
    lines.append("## Interpretation\n")
    lines.append("The prior brute sparse signed audit observed one baseline distribution per support size at the Golay endpoint through k<=5. This audit explains why that must persist for every support size k<8 and every real coefficient vector: it is forced by dual distance 8.\n")
    lines.append("## Boundary\n")
    lines.append("This still does not prove full multivariate convex order or Talagrand equivalence. It proves the complete below-weight-8 sparse projection collapse to the independent Rademacher baseline. The remaining analytic bridge is Rademacher-to-Gaussian convex-order calibration, then extension from sparse projections to arbitrary projections.\n")
    (OUT / "hamming_gaussian_dual_distance_report.md").write_text("".join(lines))


def make_manifest():
    files = sorted([p for p in OUT.iterdir() if p.is_file() and p.name != "hamming_gaussian_dual_distance_package.zip"])
    records = []
    for p in files:
        records.append({"path": p.name, "sha256": sha256_bytes(p.read_bytes()), "bytes": p.stat().st_size})
    manifest = {"schema": "hamming_gaussian_dual_distance.manifest", "files": records}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))


def make_zip():
    zip_path = OUT.parent / "hamming_gaussian_dual_distance_package.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():
                z.write(p, arcname=f"hamming_gaussian_dual_distance/{p.name}")
    return zip_path


def main():
    stages = []
    for label, C, supp in build_stages():
        stages.append(stage_record(label, C, supp))
    # Validation
    root_sequence = [r["weight4_roots"] for r in stages]
    endpoint = stages[-1]
    endpoint_low_zero = all(endpoint["dual_weight_enumerator"].get(str(i), 0) == 0 for i in range(1, 8))
    endpoint_dual_8 = endpoint["dual_distance_from_macwilliams"] == 8
    endpoint_weight_enumerator_expected = endpoint["weight_enumerator"] == {"0":1,"8":759,"12":2576,"16":759,"24":1}
    report = {
        "status": "HAMMING_GAUSSIAN_DUAL_DISTANCE_KRAWTCHOUK_PASS" if (root_sequence == [42,18,6,0] and endpoint_low_zero and endpoint_dual_8 and endpoint_weight_enumerator_expected) else "FAIL",
        "scope": "MacWilliams/Krawtchouk dual-distance audit and theorem-grade sparse projection collapse for the Golay endpoint. This proves all <8 coordinate projections are independent Rademacher baselines; it does not prove full Talagrand equivalence.",
        "root_sequence": root_sequence,
        "expected_root_sequence": [42,18,6,0],
        "root_sequence_pass": root_sequence == [42,18,6,0],
        "endpoint": {
            "weight_enumerator_expected_pass": endpoint_weight_enumerator_expected,
            "dual_weights_1_to_7_zero": endpoint_low_zero,
            "dual_distance_is_8": endpoint_dual_8,
            "uniform_marginals_for_all_coordinate_sets_size_less_than_8": endpoint_dual_8,
            "real_coefficient_projection_reduction": "For every support S with |S|<8 and every real coefficient vector a, sum_{i in S} a_i (-1)^{c_i} for c uniform in G24 has the same law as an independent Rademacher sum.",
        },
        "krawtchouk_macwilliams_formula": {
            "B_j": "B_j = |C|^{-1} sum_w A_w K_j(w)",
            "K_j(w)": "sum_l (-1)^l binom(w,l) binom(n-w,j-l)",
            "interpretation": "B_j are dual weight counts. B_1=...=B_7=0 at the Golay endpoint proves dual distance 8.",
        },
        "rademacher_gaussian_boundary": {
            "necessary_global_scale_from_one_coordinate_call_at_zero": sqrt(2/pi),
            "claim_boundary": "The finite code audit reduces <8 sparse real projections to independent Rademacher sums. It does not certify the optimal universal convex-order scale from Rademacher sums to Gaussians for all real coefficients.",
        },
        "stages": stages,
        "theorem_statement": "For the endpoint C=G24, dual distance 8 implies every marginal on fewer than 8 coordinates is uniform on F2^k. Therefore all sparse signed or real coefficient projections with support <8 are exactly independent Rademacher projections. Thus H8^3 -> G24 kills every extra below-weight-8 Hamming/Gaussian sparse projection obstruction; the remaining discrepancy is the universal Rademacher-to-Gaussian baseline.",
        "remaining_obligations": [
            "Calibrate independent Rademacher sparse projections against Gaussian convex order for arbitrary real coefficient vectors.",
            "Extend sparse projection control to all real coefficient vectors in R^24, not only support <8.",
            "Relate the resulting convex-order control to the martingale/Laguerre coupling mechanism in the Talagrand convexity proof.",
            "Lift the code-level projection theorem through G24^(12), A985, and the d20 boundary automaton.",
        ],
    }
    (OUT / "hamming_gaussian_dual_distance_certificate.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    write_csvs(stages)
    write_report(report)
    make_manifest()
    zp = make_zip()
    print(json.dumps({"status": report["status"], "zip": str(zp), "endpoint_dual_distance": endpoint["dual_distance_from_macwilliams"]}, indent=2))


if __name__ == "__main__":
    main()
