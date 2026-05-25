from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "packet239_arithmetic_resonance"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_canonical_labelled_frame"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_graph"
    / "report.json"
)

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


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


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for p in range(3, math.isqrt(n) + 1, 2):
        if n % p == 0:
            return False
    return True


def next_prime(n: int) -> int:
    value = n + 1
    while not is_prime(value):
        value += 1
    return value


def prime_count_below(limit: int) -> int:
    return sum(1 for value in range(2, limit) if is_prime(value))


def base_repr(n: int, base: int) -> str:
    if n == 0:
        return "0"
    value = n
    chars = []
    while value:
        chars.append(DIGITS[value % base])
        value //= base
    return "".join(reversed(chars))


def has_max_digit_in_bases(n: int, first_base: int = 2, last_base: int = 12) -> bool:
    return all(DIGITS[base - 1] in base_repr(n, base) for base in range(first_base, last_base + 1))


def happy_trajectory(n: int) -> tuple[bool, list[int]]:
    seen = []
    value = n
    while value not in seen:
        seen.append(value)
        if value == 1:
            return True, seen
        value = sum(int(digit) ** 2 for digit in str(value))
    seen.append(value)
    return False, seen


def multiplicative_order_mod(base: int, modulus: int) -> int | None:
    if math.gcd(base, modulus) != 1:
        return None
    value = 1
    for order in range(1, modulus + 1):
        value = (value * base) % modulus
        if value == 1:
            return order
    return None


def min_power_count(n: int, power: int) -> int:
    powers = [value**power for value in range(1, int(n ** (1 / power)) + 2) if value**power <= n]
    dp = [10**9] * (n + 1)
    dp[0] = 0
    for total in range(1, n + 1):
        dp[total] = 1 + min(dp[total - item] for item in powers if item <= total)
    return dp[n]


def nsw_numbers_until(limit: int) -> list[int]:
    values = [1, 1]
    while values[-1] < limit:
        values.append(2 * values[-1] + values[-2])
    return values


def squarefree_part(n: int) -> int:
    value = n
    factor = 2
    while factor * factor <= value:
        square = factor * factor
        while value % square == 0:
            value //= square
        factor += 1
    return value


def field_discriminant_for_q_sqrt_minus_d(d: int) -> int:
    sf = squarefree_part(d)
    return -sf if sf % 4 == 3 else -4 * sf


def reduced_forms_for_negative_discriminant(discriminant: int) -> list[tuple[int, int, int]]:
    forms = []
    max_a = int(math.sqrt(abs(discriminant) / 3)) + 2
    for a in range(1, max_a + 1):
        for b in range(-a, a + 1):
            if (b - discriminant) % 2:
                continue
            numerator = b * b - discriminant
            denominator = 4 * a
            if numerator % denominator:
                continue
            c = numerator // denominator
            if a > c:
                continue
            if math.gcd(a, math.gcd(abs(b), c)) != 1:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            if b * b - 4 * a * c == discriminant:
                forms.append((a, b, c))
    return forms


@lru_cache(maxsize=None)
def class_number_q_sqrt_minus_d(d: int) -> int:
    return len(reduced_forms_for_negative_discriminant(field_discriminant_for_q_sqrt_minus_d(d)))


def machin_tangent_identity() -> dict[str, int]:
    tan_a_num = 1
    tan_a_den = 5
    tan_2a_num = 2 * tan_a_num * tan_a_den
    tan_2a_den = tan_a_den * tan_a_den - tan_a_num * tan_a_num
    tan_4a_num = 2 * tan_2a_num * tan_2a_den
    tan_4a_den = tan_2a_den * tan_2a_den - tan_2a_num * tan_2a_num
    # tan(4a - b) with tan(b)=1/239
    numerator = tan_4a_num * 239 - tan_4a_den
    denominator = tan_4a_den * 239 + tan_4a_num
    divisor = math.gcd(abs(numerator), abs(denominator))
    return {
        "tan_4_arctan_1_5_numerator": tan_4a_num,
        "tan_4_arctan_1_5_denominator": tan_4a_den,
        "tan_difference_numerator_reduced": numerator // divisor,
        "tan_difference_denominator_reduced": denominator // divisor,
    }


def bounded_diophantine_solutions(max_x: int) -> list[dict[str, int]]:
    rows = []
    for x in range(1, max_x + 1):
        y2 = 2 * x**4 - 1
        y = math.isqrt(y2)
        if y * y == y2:
            rows.append({"x": x, "y": y})
    return rows


def build_arithmetic_profile(n: int) -> dict[str, Any]:
    happy, happy_path = happy_trajectory(n)
    base_rows = [
        {
            "base": base,
            "representation": base_repr(n, base),
            "max_digit": DIGITS[base - 1],
            "contains_max_digit": DIGITS[base - 1] in base_repr(n, base),
        }
        for base in range(2, 13)
    ]
    literal_digit_property_hits = [
        value
        for value in range(1, 6000)
        if has_max_digit_in_bases(value)
    ]
    discriminant = field_discriminant_for_q_sqrt_minus_d(n)
    class_forms = reduced_forms_for_negative_discriminant(discriminant)
    earlier_class15 = [
        value
        for value in range(1, n)
        if squarefree_part(value) == value and class_number_q_sqrt_minus_d(value) == 15
    ]
    return {
        "n": n,
        "prime": {
            "is_prime": is_prime(n),
            "next_prime": next_prime(n),
            "is_twin_prime_with_next": next_prime(n) == n + 2,
            "is_chen_prime_by_prime_plus_two": is_prime(n + 2),
            "is_sophie_germain_prime": is_prime(2 * n + 1),
            "safe_prime_target": 2 * n + 1,
            "is_eisenstein_integer_prime": is_prime(n) and n % 3 == 2,
            "prime_count_below_1500": prime_count_below(1500),
        },
        "newman_shanks_williams": {
            "sequence_until_n": nsw_numbers_until(n),
            "contains_n": n in nsw_numbers_until(n),
        },
        "repunit": {
            "repunit_7": 1_111_111,
            "other_factor": 1_111_111 // n,
            "factorization_holds": n * (1_111_111 // n) == 1_111_111,
            "other_factor_is_prime": is_prime(1_111_111 // n),
            "decimal_period_order_10_mod_n": multiplicative_order_mod(10, n),
        },
        "happy_number": {
            "is_happy": happy,
            "trajectory": happy_path,
        },
        "class_number": {
            "field": f"Q(sqrt(-{n}))",
            "fundamental_discriminant": discriminant,
            "class_number": len(class_forms),
            "reduced_form_count": len(class_forms),
            "reduced_forms": [list(row) for row in class_forms],
            "earlier_squarefree_d_with_class_number_15": earlier_class15,
        },
        "digit_sweep": {
            "base_rows": base_rows,
            "contains_max_digit_in_bases_2_to_12": all(
                row["contains_max_digit"] for row in base_rows
            ),
            "literal_property_hits_below_6000": literal_digit_property_hits,
            "literal_next_hit_after_239": (
                literal_digit_property_hits[1]
                if len(literal_digit_property_hits) > 1
                else None
            ),
            "quoted_next_5927_is_literal_next": (
                len(literal_digit_property_hits) > 1
                and literal_digit_property_hits[1] == 5927
            ),
        },
        "hakmem_arithmetic": {
            "min_square_count": min_power_count(n, 2),
            "min_positive_cube_count": min_power_count(n, 3),
            "min_positive_fourth_power_count": min_power_count(n, 4),
            "pell": {
                "x": 239,
                "y": 169,
                "identity_holds": 239 * 239 == 2 * 169 * 169 - 1,
            },
            "machin_tangent_identity": machin_tangent_identity(),
            "base_power_subtractions": {
                "2": {"exponents": [8, 4], "value": 2**8 - 2**4 - 1},
                "3": {"exponents": [5, 1], "value": 3**5 - 3 - 1},
                "4": {"exponents": [4, 2], "value": 4**4 - 4**2 - 1},
            },
            "diophantine_y2_plus_1_equals_2x4": {
                "bounded_solutions_x_le_13": bounded_diophantine_solutions(13),
                "packet_integer_solution": {"x": 13, "y": n},
                "packet_integer_solution_holds": n * n + 1 == 2 * 13**4,
                "global_uniqueness_is_external_number_theory": True,
            },
        },
    }


def build_theorem() -> dict[str, Any]:
    frame = load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT)
    charge = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)

    selection = frame.get("derived", {}).get("packet239_selection", {})
    selected_packet_ids = selection.get("selected_packet_ids", [])
    n = int(selected_packet_ids[0]) if selected_packet_ids else -1
    arithmetic = build_arithmetic_profile(n)
    charge_rows = {
        int(row["packet_id"]): row
        for row in charge.get("derived", {}).get("charge_frame_rows", [])
    }
    selected_charge_row = charge_rows.get(n, {})
    twin_successor_row = charge_rows.get(n + 2, {})
    component_rows = graph.get("derived", {}).get("component_rows", [])
    selected_component = [
        row for row in component_rows if n in {int(item) for item in row.get("packet_pair", [])}
    ]
    selected_component_row = selected_component[0] if selected_component else {}
    resonance_summary = {
        "id_free_selected_packet_id": n,
        "arithmetic_twin_successor": n + 2,
        "graph_active_partner": (
            [item for item in selected_component_row.get("packet_pair", []) if item != n] or [None]
        )[0],
        "twin_successor_is_full_exposure": bool(
            twin_successor_row.get("full_loop297_atom_exposure")
        ),
        "twin_successor_charge_frame_key": twin_successor_row.get("charge_frame_key"),
        "packet239_charge_frame_key": selected_charge_row.get("charge_frame_key"),
        "packet239_zero_pair_signature": selection.get("selected_signature"),
        "nontrivial_links": [
            "the packet id is obtained from the id-free zero-pair fixed rule before arithmetic is evaluated",
            "the selected id is prime, twin-prime lower member, Chen, Sophie Germain, Eisenstein, happy, and a Newman-Shanks-Williams prime",
            "the arithmetic twin successor 241 is not the graph active partner and is not full-exposure; the certified graph partner is 238",
            "239 is the class-number-15 field discriminant witness for Q(sqrt(-239)) under direct reduced-form enumeration",
            "239 supplies both the Pell/Machin denominator and the y-coordinate in y^2+1=2*13^4; the global uniqueness theorem is recorded as external",
        ],
        "noncertified_or_qualified_claims": [
            "Under the literal max-digit-in-every-base-2-to-12 predicate, 2591 also qualifies before 5927, so the quoted 'next is 5927' statement is not certified without an additional condition.",
            "The global statement that 239 is the largest factorial-product integer is not certified here.",
            "The global uniqueness of the Ljunggren equation y^2+1=2x^4 is not reproved here; only the bounded witness x<=13 and the (13,239) solution are checked.",
        ],
    }

    checks = {
        "canonical_labelled_frame_is_certified": frame.get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and frame.get("all_checks_pass") is True,
        "charge_frame_classifier_is_certified": charge.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "packet_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "packet239_is_selected_id_free_before_arithmetic": n == 239
        and selection.get("uses_external_packet_id") is False,
        "prime_cluster_properties_hold": arithmetic["prime"]
        == {
            "is_prime": True,
            "next_prime": 241,
            "is_twin_prime_with_next": True,
            "is_chen_prime_by_prime_plus_two": True,
            "is_sophie_germain_prime": True,
            "safe_prime_target": 479,
            "is_eisenstein_integer_prime": True,
            "prime_count_below_1500": 239,
        },
        "nsw_repdigit_happy_properties_hold": arithmetic["newman_shanks_williams"][
            "contains_n"
        ]
        is True
        and arithmetic["repunit"]["factorization_holds"] is True
        and arithmetic["repunit"]["other_factor"] == 4649
        and arithmetic["repunit"]["other_factor_is_prime"] is True
        and arithmetic["repunit"]["decimal_period_order_10_mod_n"] == 7
        and arithmetic["happy_number"]["is_happy"] is True,
        "class_number_15_minimal_squarefree_witness_holds": arithmetic["class_number"][
            "class_number"
        ]
        == 15
        and arithmetic["class_number"]["earlier_squarefree_d_with_class_number_15"] == [],
        "digit_sweep_literal_property_holds_but_next_5927_is_not_literal": arithmetic[
            "digit_sweep"
        ]["contains_max_digit_in_bases_2_to_12"]
        is True
        and arithmetic["digit_sweep"]["literal_next_hit_after_239"] == 2591
        and arithmetic["digit_sweep"]["quoted_next_5927_is_literal_next"] is False,
        "hakmem_local_arithmetic_witnesses_hold": arithmetic["hakmem_arithmetic"][
            "min_square_count"
        ]
        == 4
        and arithmetic["hakmem_arithmetic"]["min_positive_cube_count"] == 9
        and arithmetic["hakmem_arithmetic"]["min_positive_fourth_power_count"] == 19
        and arithmetic["hakmem_arithmetic"]["pell"]["identity_holds"] is True
        and arithmetic["hakmem_arithmetic"]["machin_tangent_identity"][
            "tan_difference_numerator_reduced"
        ]
        == 1
        and arithmetic["hakmem_arithmetic"]["machin_tangent_identity"][
            "tan_difference_denominator_reduced"
        ]
        == 1
        and arithmetic["hakmem_arithmetic"]["diophantine_y2_plus_1_equals_2x4"][
            "packet_integer_solution_holds"
        ]
        is True,
        "arithmetic_twin_successor_is_not_the_graph_partner": resonance_summary[
            "arithmetic_twin_successor"
        ]
        == 241
        and resonance_summary["graph_active_partner"] == 238
        and resonance_summary["twin_successor_is_full_exposure"] is False,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PACKET239_ARITHMETIC_RESONANCE_CERTIFIED"
        if all_checks_pass
        else "D20_PACKET239_ARITHMETIC_RESONANCE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.packet239_arithmetic_resonance",
        "status": status,
        "object": "d20",
        "claim": (
            "After packet 239 is selected by the certified id-free full-exposure sector-26 zero-pair "
            "condition, its integer label carries a dense arithmetic resonance profile. The resonance is "
            "nontrivial as a post-selection invariant screen, but it is not used to select the packet."
        ),
        "definition": {
            "post_selection_arithmetic_screen": (
                "First recover the packet id from certified D20 labels, then evaluate arithmetic predicates "
                "on that recovered integer."
            ),
            "nontrivial_link": (
                "A locally verified arithmetic predicate attached to the id-free selected packet, plus an "
                "explicit comparison with packet-frame data such as active partner and full-exposure status."
            ),
        },
        "inputs": {
            "full_exposure_canonical_labelled_frame_report": {
                "path": rel(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
            "full_exposure_packet_propagation_graph_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
            },
        },
        "derived": {
            "resonance_summary": resonance_summary,
            "arithmetic_profile": arithmetic,
            "selected_packet_charge_row": selected_charge_row,
            "twin_successor_charge_row": twin_successor_row,
        },
        "interpretation": {
            "what_this_proves": [
                "packet 239 is selected by D20 labels before any arithmetic property is evaluated",
                "the selected integer satisfies the locally checkable prime, repunit, happy, class-number, digit-sweep, Pell, Machin, and Waring-count witnesses recorded in the profile",
                "the arithmetic twin successor 241 is external to the full-exposure packet graph, while the certified graph partner of packet 239 is 238",
            ],
            "what_this_does_not_prove": (
                "This does not prove that D20 causes the arithmetic properties of 239. It certifies a "
                "post-selection resonance screen and explicitly leaves external global number-theory claims "
                "outside the local proof boundary."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the canonical labelled frame to express the full-exposure two-step transition operator in "
            "intrinsic label coordinates instead of packet ids."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.packet239_arithmetic_resonance_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "recover packet 239 from the id-free canonical labelled frame selection",
            "verify prime, twin-prime, Chen, Sophie Germain, Eisenstein, NSW, repunit, and happy predicates",
            "enumerate reduced binary quadratic forms for Q(sqrt(-239)) and scan earlier squarefree d",
            "verify the base-2-through-base-12 max-digit property and flag the literal next-hit discrepancy",
            "verify local HAKMEM arithmetic witnesses while keeping external global theorems out of scope",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
