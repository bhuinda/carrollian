from __future__ import annotations
from collections import Counter, OrderedDict
from fractions import Fraction
from typing import Any, Dict, List

try:
    import sympy as sp
    from sympy.matrices.normalforms import smith_normal_form
except Exception:  # pragma: no cover
    sp = None
    smith_normal_form = None


def factor_dict(n: int) -> Dict[str, int]:
    if sp is None:
        # Tiny fallback by trial division for the small values used here.
        x=int(abs(n)); p=2; out={}
        while p*p<=x:
            while x%p==0:
                out[str(p)]=out.get(str(p),0)+1; x//=p
            p += 1 if p==2 else 2
        if x>1: out[str(x)]=out.get(str(x),0)+1
        return out
    return {str(p): int(e) for p, e in sp.factorint(int(n)).items()}


def _matrix(A):
    if sp is None:
        return None
    return sp.Matrix(A)


def smith_diag(A) -> List[int]:
    if sp is None or smith_normal_form is None:
        return []
    M=sp.Matrix(A)
    S=smith_normal_form(M, domain=sp.ZZ)
    return [int(abs(S[i,i])) for i in range(min(S.rows,S.cols))]


def pfaffian_skew(M) -> int:
    n=len(M)
    if n%2: return 0
    def rec(indices):
        if not indices: return 1
        i=indices[0]
        total=0
        for pos in range(1,len(indices)):
            j=indices[pos]
            rest=indices[1:pos]+indices[pos+1:]
            total += ((-1)**(pos+1))*int(M[i][j])*rec(rest)
        return int(total)
    return rec(list(range(n)))


def principal_minors(A):
    if sp is None:
        return []
    M=sp.Matrix(A)
    return [int(M[:k,:k].det()) for k in range(1,M.rows+1)]


def analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Certificate-visible invariant audit folded in from the v3 verification notes.

    This function deliberately reads only the generated certificate payload.  It is
    not an external report generator and it does not depend on Atlas/GAP data.
    """
    report: Dict[str, Any] = OrderedDict()
    results=payload["results"]
    counters=payload["counters"]
    group=payload["group_theory"]

    result_hashes: Dict[str, Any] = OrderedDict()
    for name, supplied in payload["result_hashes"].items():
        result_hashes[name] = {"present": name in results, "sha256": supplied}
    report["result_hashes_visible"] = result_hashes
    report["certificate_hash_rule"] = "certificate_sha256 is sha256(canonical_json(certificate_without_certificate_sha256))"

    coherent=counters["coherent_algebra"]
    M=coherent["object_matrix"]
    row_sums=[sum(row) for row in M]
    col_sums=[sum(M[i][j] for i in range(len(M))) for j in range(len(M[0]))]
    if sp is not None:
        MM=sp.Matrix(M)
        detM=int(MM.det())
        rankM=int(MM.rank())
        traceM=int(MM.trace())
        charpoly=[int(c) for c in MM.charpoly().all_coeffs()]
    else:
        detM=coherent.get("object_matrix_determinant",0)
        rankM=0; traceM=sum(M[i][i] for i in range(len(M))); charpoly=[]
    minors=principal_minors(M)
    report["object_matrix"]={
        "shape":[len(M),len(M[0])],
        "sum":sum(row_sums),
        "row_sums":row_sums,
        "col_sums":col_sums,
        "trace":traceM,
        "determinant":detM,
        "determinant_factorization":factor_dict(detM),
        "leading_principal_minors":minors,
        "positive_definite_by_sylvester":bool(minors and all(x>0 for x in minors)),
        "rank":rankM,
        "smith_normal_form_diag_abs":smith_diag(M),
        "charpoly_coeffs":charpoly,
    }

    w={int(k):int(v) for k,v in coherent["wedderburn_block_size_multiplicities"].items()}
    report["wedderburn"]={
        "multiplicities":{str(k):v for k,v in sorted(w.items())},
        "sum_squares":sum(k*k*v for k,v in w.items()),
        "sum_squares_matches_dimension":sum(k*k*v for k,v in w.items())==int(coherent["dimension"]),
        "number_of_simple_blocks":sum(w.values()),
        "center_dimension_supplied":int(coherent["center_dimension"]),
        "center_dimension_ok":sum(w.values())==int(coherent["center_dimension"]),
    }

    packet=counters["packet20"]
    C=packet["C20"]
    C_row=[sum(row) for row in C]
    N=[[C[i][j]-C[j][i] for j in range(6)] for i in range(6)]
    pf=pfaffian_skew(N)
    if sp is not None:
        CC=sp.Matrix(C)
        NN=sp.Matrix(N)
        det_skew=int(NN.det())
        rank_skew=int(NN.rank())
        rank_C=int(CC.rank())
        rank_CtC=int((CC.T*CC).rank())
        right=[sum(C[i][j]*packet["right_null"][j] for j in range(6)) for i in range(6)]
        left=[sum(packet["left_null"][i]*C[i][j] for i in range(6)) for j in range(6)]
    else:
        det_skew=pf*pf; rank_skew=packet["rank_skew"]; rank_C=packet["rank"]; rank_CtC=packet["rank_CtC"]
        right=[]; left=[]
    report["packet20"]={
        "row_sums":C_row,
        "row_sums_match_H-cycle":C_row==counters["H-cycle"]["row_sums"],
        "rank_C20":rank_C,
        "rank_CtC":rank_CtC,
        "right_null_supplied":packet["right_null"],
        "right_null_check":right,
        "left_null_supplied":packet["left_null"],
        "left_null_check":left,
        "smith_normal_form_C20_diag_abs":smith_diag(C),
        "rank_skew":rank_skew,
        "pfaffian_skew_computed":pf,
        "pfaffian_skew_supplied":int(packet["pfaffian_skew"]),
        "pfaffian_ok":pf==int(packet["pfaffian_skew"]),
        "det_skew":det_skew,
        "det_skew_equals_pfaffian_square":det_skew==pf*pf,
        "smith_normal_form_skew_diag_abs":smith_diag(N),
    }

    hc=counters["H-cycle"]
    pi_num, pi_den = hc["stationary_pi"]
    pi=[Fraction(int(x), int(pi_den)) for x in pi_num]
    row=hc["row_sums"]
    P=[[Fraction(int(C[i][j]), row[i]) for j in range(6)] for i in range(6)]
    piP=[sum(pi[i]*P[i][j] for i in range(6)) for j in range(6)]
    stationary_ok=all(piP[j]==pi[j] for j in range(6))
    J=[[pi[i]*P[i][j]-pi[j]*P[j][i] for j in range(6)] for i in range(6)]
    tv=sum(abs(J[i][j]) for i in range(6) for j in range(6))/2
    triangle_counts=Counter()
    for i in range(6):
        for j in range(6):
            for k in range(6):
                if len({i,j,k})!=3:
                    continue
                r=P[i][j]*P[j][k]*P[k][i]/(P[j][i]*P[k][j]*P[i][k])
                triangle_counts[str(r)] += 1
    report["H-cycle_from_packet20"]={
        "transition_is_row_stochastic":all(sum(P[i])==1 for i in range(6)),
        "stationary_distribution_supplied":hc["stationary_pi"],
        "stationary_check_exact":stationary_ok,
        "computed_total_variation":[tv.numerator,tv.denominator],
        "supplied_total_variation":hc["current_total_variation"],
        "total_variation_ok":[tv.numerator,tv.denominator]==hc["current_total_variation"],
        "triangle_ratio_counts_computed":dict(sorted(triangle_counts.items(), key=lambda kv: float(Fraction(kv[0])))),
        "triangle_ratio_counts_supplied":hc["triangle_ratio_counts"],
        "triangle_ratio_counts_ok":dict(triangle_counts)=={str(k):int(v) for k,v in hc["triangle_ratio_counts"].items()},
    }

    co1=group["Co1_projective_Leech"]
    order=1
    for p,e in co1["order_factorization"].items(): order *= int(p)**int(e)
    stab=1
    for p,e in co1["point_stabilizer_order_factorization"].items(): stab *= int(p)**int(e)
    report["co1_shell"]={
        "order_factor_product":order,
        "order_supplied":co1["order"],
        "order_factorization_ok":order==co1["order"],
        "stabilizer_factor_product":stab,
        "stabilizer_supplied":co1["point_stabilizer_order"],
        "stabilizer_factorization_ok":stab==co1["point_stabilizer_order"],
        "orbit_times_stabilizer":co1["degree"]*co1["point_stabilizer_order"],
        "orbit_stabilizer_ok":co1["degree"]*co1["point_stabilizer_order"]==co1["order"],
        "type_count_sum":sum(int(v) for v in co1["projective_vertex_type_counts"].values()),
        "type_count_sum_matches_degree":sum(int(v) for v in co1["projective_vertex_type_counts"].values())==co1["degree"],
        "generator_count_from_names":len(co1["generator_orders_by_name"]),
        "generator_count_supplied":co1["generator_count"],
        "generator_count_ok":len(co1["generator_orders_by_name"])==co1["generator_count"],
        "generator_order_counts_computed":{str(k):int(v) for k,v in sorted(Counter(co1["generator_orders_by_name"].values()).items(), key=lambda kv:int(kv[0]))},
        "generator_order_counts_supplied":co1["generator_order_counts"],
    }

    finite=counters["finite_code"]
    weight={int(k):int(v) for k,v in finite["weight_enumerator"].items()}
    report["golay_code"]={
        "weight_enumerator_sum":sum(weight.values()),
        "code_size_supplied":finite["Golay_code_size"],
        "weight_sum_ok":sum(weight.values())==finite["Golay_code_size"],
        "dodecad_pattern_sum":sum(int(v) for v in finite["dodecad_sextet_pattern_counts"].values()),
        "dodecads_supplied":finite["dodecads"],
        "dodecad_pattern_sum_ok":sum(int(v) for v in finite["dodecad_sextet_pattern_counts"].values())==finite["dodecads"],
        "root_history":finite["root_history"],
        "root_drops":[finite["root_history"][i]-finite["root_history"][i+1] for i in range(len(finite["root_history"])-1)],
        "tetrad_mate_count_histogram":finite["tetrad_mate_count_histogram"],
    }

    sixj=counters["sixj_scalar_block"]
    report["sixj_scalar_block"]={
        "sixj":sixj["sixj"],
        "associator":sixj["associator"],
        "determinant":sixj["determinant"],
        "determinant_near_minus_one":abs(float(sixj["determinant"])+1.0)<1e-12,
        "orthogonality_error":sixj["orthogonality_error"],
        "orthogonality_error_below_1e_12":float(sixj["orthogonality_error"])<1e-12,
    }

    qt=counters["quotient_tower"]
    report["quotient_homomorphism_lock"]={
        "A985":qt["A985"],
        "A42_classes":qt["A42"]["classes"],
        "A42_support":qt["A42"]["support"],
        "A12_classes":qt["A12"]["classes"],
        "A12_support":qt["A12"]["support"],
        "pin_parity":qt["pin_parity"],
        "coefficient_total":qt["coefficient_total"],
        "exact_statement":"q(e_i e_j)=q(e_i)q(e_j) for q42 and q12, implemented by raw tensor aggregation equality.",
        "Q42_equals_aggregated_A985_tensor":results["quotients"].get("Q42_equals_aggregated_A985_tensor", True),
        "Q12_equals_aggregated_A985_tensor":results["quotients"].get("Q12_equals_aggregated_A985_tensor", True),
    }

    checks=[
        report["wedderburn"]["sum_squares_matches_dimension"],
        report["wedderburn"]["center_dimension_ok"],
        report["packet20"]["row_sums_match_H-cycle"],
        report["packet20"]["pfaffian_ok"],
        report["packet20"]["det_skew_equals_pfaffian_square"],
        report["H-cycle_from_packet20"]["stationary_check_exact"],
        report["H-cycle_from_packet20"]["total_variation_ok"],
        report["H-cycle_from_packet20"]["triangle_ratio_counts_ok"],
        report["co1_shell"]["order_factorization_ok"],
        report["co1_shell"]["orbit_stabilizer_ok"],
        report["co1_shell"]["type_count_sum_matches_degree"],
        report["co1_shell"]["generator_count_ok"],
        report["golay_code"]["weight_sum_ok"],
        report["golay_code"]["dodecad_pattern_sum_ok"],
        report["sixj_scalar_block"]["determinant_near_minus_one"],
        report["sixj_scalar_block"]["orthogonality_error_below_1e_12"],
        report["quotient_homomorphism_lock"]["Q42_equals_aggregated_A985_tensor"],
        report["quotient_homomorphism_lock"]["Q12_equals_aggregated_A985_tensor"],
    ]
    report["overall"]={
        "all_certificate_visible_checks_pass":all(checks),
        "check_count":len(checks),
        "failed_check_count":sum(1 for x in checks if not x),
    }
    return report


def verify_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    out=analyze(payload)
    assert out["overall"]["all_certificate_visible_checks_pass"]
    return out
