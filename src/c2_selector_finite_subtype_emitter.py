from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class SelectorFiniteSubtypeSpec:
    module_name: str
    selector_key: str
    selector_agda: str
    prefix: str
    membership_prefix: str
    fiber_count: int
    index_type_name: str
    fin_pattern_style: str = "prefix_suc"
    wrap_fin_lhs: bool = False
    use_from_nat_to_fin: bool = False
    use_nat_with_from: bool = False
    use_nat_with_right_inv: bool = False
    use_nat_lookup_right_inv: bool = False
    require_full_selector: bool = False


def fin_data_pattern(index: int, style: str = "prefix_suc") -> str:
    term = "FD.zero"
    for _ in range(index):
        if style == "call_suc":
            term = f"FD.suc ({term})"
        elif style == "prefix_suc":
            term = f"(FD.suc {term})"
        else:
            raise ValueError(f"unknown FinData pattern style: {style}")
    return term


def fin_data_lhs(index: int, spec: SelectorFiniteSubtypeSpec) -> str:
    term = fin_data_pattern(index, spec.fin_pattern_style)
    return f"({term})" if spec.wrap_fin_lhs else term


def nat_exact_pattern(index: int) -> str:
    term = "zero"
    for _ in range(index):
        term = f"(suc {term})"
    return term


def nat_ge_pattern(bound: int) -> str:
    term = "n"
    for _ in range(bound):
        term = f"(suc {term})"
    return term


def nat_ge_absurd_clause(bound: int) -> str:
    return (
        f"... | {nat_ge_pattern(bound)} | p = "
        f"Empty.rec (NatOrder.¬m+n<m {{m = {bound}}} {{n = n}} p)"
    )


def membership_constructor(prefix: str, move_id: int) -> str:
    return f"{prefix}{move_id}"


def selected_fiber(
    bridge: Mapping[str, Any], selector_key: str, expected_count: int
) -> dict[str, Any]:
    for fiber in bridge["derived"]["selector_fibers"]:
        if fiber["selector"] == selector_key:
            if int(fiber["selected_count"]) != expected_count:
                raise ValueError(f"expected {selector_key} selector count {expected_count}")
            return fiber
    raise ValueError(f"missing selector fiber: {selector_key}")


def selector_payload_from_actual_c2_kernel_orbits(
    orbit_csv: Path,
    *,
    raw_selector_key: str = "raw_componentwise_absolute_spectral_gap",
    lazy_selector_key: str = "lazy_componentwise_spectral_gap",
    paired_selector_key: str = "paired_lazy_componentwise_spectral_gap",
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    with orbit_csv.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fixed = row["fixed"] == "True"
            rows.append(
                {
                    "orbit_id": int(row["orbit_id"]),
                    "size": int(row["size"]),
                    "representative": int(row["representative"]),
                    "member_a": int(row["member_a"]),
                    "member_b": int(row["member_b"]),
                    "fixed": fixed,
                    "nonzero": row["nonzero"] == "True",
                }
            )
    orbit_ids = [int(row["orbit_id"]) for row in rows]
    if orbit_ids != list(range(len(rows))):
        raise ValueError("actual C2 kernel orbit ids must be contiguous in Agda order")
    if not all(row["nonzero"] for row in rows):
        raise ValueError("actual C2 kernel orbit bridge expects nonzero orbit rows")
    fixed_ids = [int(row["orbit_id"]) for row in rows if row["fixed"]]
    paired_ids = [int(row["orbit_id"]) for row in rows if not row["fixed"]]
    if len(rows) != 543 or len(fixed_ids) != 63 or len(paired_ids) != 480:
        raise ValueError("actual C2 kernel orbit split must be 543 = 63 + 480")
    return {
        "derived": {
            "bridge_summary": {"dynamics_count": len(rows)},
            "actual_c2_kernel_orbit_source": {
                "path": str(orbit_csv),
                "raw543_orbit_count": len(rows),
                "fixed63_orbit_count": len(fixed_ids),
                "paired480_two_cycle_orbit_count": len(paired_ids),
            },
            "actual_c2_kernel_orbit_rows": rows,
            "selector_fibers": [
                {
                    "selector": raw_selector_key,
                    "selected_count": len(orbit_ids),
                    "selected_move_orbit_ids": orbit_ids,
                },
                {
                    "selector": lazy_selector_key,
                    "selected_count": len(fixed_ids),
                    "selected_move_orbit_ids": fixed_ids,
                },
                {
                    "selector": paired_selector_key,
                    "selected_count": len(paired_ids),
                    "selected_move_orbit_ids": paired_ids,
                },
            ],
        }
    }


def selector_payload_with_lookup_witness_table(
    selector_payload: Mapping[str, Any], table_json: Path
) -> dict[str, Any]:
    table = json.loads(table_json.read_text(encoding="utf-8"))
    rows = table.get("rows", [])
    if int(table.get("row_count", -1)) != len(rows):
        raise ValueError("lookup witness table row_count does not match rows")
    row_ids = [int(row["row_id"]) for row in rows]
    if row_ids != list(range(len(rows))):
        raise ValueError("lookup witness table row ids must be contiguous")

    fibers = selector_payload["derived"]["selector_fibers"]
    fiber_by_selector = {str(fiber["selector"]): fiber for fiber in fibers}
    rows_by_selector: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        selector_key = str(row["selector_key"])
        normalized = dict(row)
        for key in (
            "row_id",
            "selector_index",
            "fiber_count",
            "fiber_index",
            "dynamics_id",
            "index_bound_witness",
        ):
            normalized[key] = int(normalized[key])
        rows_by_selector.setdefault(selector_key, []).append(normalized)

    for selector_key, selector_rows in rows_by_selector.items():
        if selector_key not in fiber_by_selector:
            raise ValueError(f"lookup witness table selector missing from payload: {selector_key}")
        fiber = fiber_by_selector[selector_key]
        selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
        dynamics_ids = [int(row["dynamics_id"]) for row in selector_rows]
        fiber_indices = [int(row["fiber_index"]) for row in selector_rows]
        if dynamics_ids != selected_ids:
            raise ValueError(f"lookup witness rows do not match selector order: {selector_key}")
        if fiber_indices != list(range(len(selector_rows))):
            raise ValueError(f"lookup witness rows are not contiguous: {selector_key}")
        if int(fiber["selected_count"]) != len(selector_rows):
            raise ValueError(f"lookup witness row count mismatch: {selector_key}")

    derived = dict(selector_payload["derived"])
    derived["lookup_witness_table_source"] = {
        "path": str(table_json),
        "table_sha256": table.get("table_sha256"),
        "row_count": len(rows),
        "selector_count": len(rows_by_selector),
        "row_count_by_selector": {
            selector_key: len(selector_rows)
            for selector_key, selector_rows in sorted(rows_by_selector.items())
        },
    }
    derived["selector_lookup_witness_rows"] = rows_by_selector
    return {"derived": derived}


def lookup_witness_rows_for_spec(
    bridge: Mapping[str, Any], spec: SelectorFiniteSubtypeSpec, selected_ids: list[int]
) -> list[dict[str, Any]] | None:
    rows_by_selector = bridge.get("derived", {}).get("selector_lookup_witness_rows", {})
    rows = rows_by_selector.get(spec.selector_key)
    if rows is None:
        return None
    if not spec.use_nat_lookup_right_inv:
        raise ValueError("lookup witness table rows require use_nat_lookup_right_inv")
    if len(rows) != spec.fiber_count:
        raise ValueError(f"lookup witness row count mismatch for {spec.selector_key}")
    dynamics_ids = [int(row["dynamics_id"]) for row in rows]
    if dynamics_ids != selected_ids:
        raise ValueError(f"lookup witness rows do not match selected ids for {spec.selector_key}")
    for index, row in enumerate(rows):
        dynamics_id = int(row["dynamics_id"])
        constructor = membership_constructor(spec.membership_prefix, dynamics_id)
        if int(row["fiber_index"]) != index:
            raise ValueError(f"lookup witness row index mismatch for {spec.selector_key}")
        if int(row["fiber_count"]) != spec.fiber_count:
            raise ValueError(f"lookup witness fiber count mismatch for {spec.selector_key}")
        if row["lookup_prefix"] != spec.prefix:
            raise ValueError(f"lookup witness prefix mismatch for {spec.selector_key}")
        if row["membership_constructor"] != constructor:
            raise ValueError(f"lookup witness membership mismatch for {spec.selector_key}")
    return list(rows)


def agda_import_block(spec: SelectorFiniteSubtypeSpec) -> list[str]:
    needs_nat_indexing = (
        spec.use_nat_with_from
        or spec.use_nat_with_right_inv
        or spec.use_nat_lookup_right_inv
    )
    lines = [
        "open import Cubical.Foundations.Prelude",
        "open import Cubical.Foundations.Equiv using (_≃_ ; compEquiv)",
        "open import Cubical.Foundations.Isomorphism using (Iso ; iso ; isoToEquiv)",
    ]
    if needs_nat_indexing:
        if spec.use_nat_with_right_inv and not spec.use_nat_lookup_right_inv:
            lines.append("open import Cubical.Foundations.Path using (inspect ; [_]ᵢ)")
        lines.extend(
            [
                "open import Cubical.Data.Empty as Empty",
                "open import Cubical.Data.Nat using (ℕ ; zero ; suc)",
                "import Cubical.Data.Nat.Order as NatOrder",
            ]
        )
    lines.extend(
        [
            "open import Cubical.Data.Sigma using (Σ ; Σ-syntax)",
            "open import Cubical.Data.Fin.Base using (Fin)",
            "open import Cubical.Data.Fin.Properties using (FinData≃Fin)",
            "import Cubical.Data.FinData.Base as FD",
        ]
    )
    if needs_nat_indexing:
        lines.append("import Cubical.Data.FinData.Properties as FDP")
    lines.extend(
        [
            "open import C2SelectorFoundation",
            "open import C2SelectorFoundationGenerated",
        ]
    )
    return lines


def generate_selector_finite_subtype_agda(
    bridge: Mapping[str, Any], spec: SelectorFiniteSubtypeSpec
) -> str:
    fiber = selected_fiber(bridge, spec.selector_key, spec.fiber_count)
    selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
    selected_index = {move_id: index for index, move_id in enumerate(selected_ids)}
    table_rows = lookup_witness_rows_for_spec(bridge, spec, selected_ids)
    table_row_by_dynamics = (
        {int(row["dynamics_id"]): row for row in table_rows}
        if table_rows is not None
        else {}
    )
    dynamics_count = int(bridge["derived"]["bridge_summary"]["dynamics_count"])
    if spec.require_full_selector and selected_ids != list(range(dynamics_count)):
        raise ValueError(f"{spec.selector_key} is expected to select every dynamics id in order")

    lines = [
        "{-# OPTIONS --cubical --safe --guardedness #-}",
        "",
        f"module {spec.module_name} where",
        "",
        *agda_import_block(spec),
        "",
        "SelectorFiber : Selector → Set",
        "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d",
        "",
        f"{spec.prefix}FiberToFinData : SelectorFiber {spec.selector_agda} → FD.Fin {spec.fiber_count}",
    ]
    for dynamics_id in range(dynamics_count):
        if dynamics_id in selected_index:
            index = selected_index[dynamics_id]
            constructor = membership_constructor(spec.membership_prefix, dynamics_id)
            if table_rows is not None and "to_fin_data_clause" in table_row_by_dynamics[dynamics_id]:
                lines.append(str(table_row_by_dynamics[dynamics_id]["to_fin_data_clause"]))
                continue
            if spec.use_from_nat_to_fin:
                rhs = f"FDP.fromℕ' {spec.fiber_count} {index} ({spec.fiber_count - index - 1} , refl)"
            else:
                rhs = fin_data_pattern(index, spec.fin_pattern_style)
            lines.append(
                f"{spec.prefix}FiberToFinData (d{dynamics_id} , {constructor}) = {rhs}"
            )
        else:
            lines.append(f"{spec.prefix}FiberToFinData (d{dynamics_id} , ())")

    if spec.use_nat_lookup_right_inv:
        lines.extend(
            [
                "",
                (
                    f"{spec.prefix}FiberFromNat : "
                    f"(k : ℕ) → NatOrder._<_ k {spec.fiber_count} → "
                    f"SelectorFiber {spec.selector_agda}"
                ),
            ]
        )
        for index, dynamics_id in enumerate(selected_ids):
            if table_rows is not None:
                lines.append(str(table_rows[index]["from_nat_clause"]))
            else:
                constructor = membership_constructor(spec.membership_prefix, dynamics_id)
                lines.append(
                    f"{spec.prefix}FiberFromNat {nat_exact_pattern(index)} _ = "
                    f"d{dynamics_id} , {constructor}"
                )
        lines.append(
            f"{spec.prefix}FiberFromNat {nat_ge_pattern(spec.fiber_count)} p = "
            f"Empty.rec (NatOrder.¬m+n<m {{m = {spec.fiber_count}}} {{n = n}} p)"
        )
        lines.extend(
            [
                "",
                f"{spec.prefix}FiberFromNatToFinData :",
                (
                    f"  (k : ℕ) (p : NatOrder._<_ k {spec.fiber_count}) → "
                    f"{spec.prefix}FiberToFinData ({spec.prefix}FiberFromNat k p) "
                    f"≡ FDP.fromℕ' {spec.fiber_count} k p"
                ),
            ]
        )
        for index in range(len(selected_ids)):
            if table_rows is not None:
                lines.append(str(table_rows[index]["from_nat_to_fin_data_clause"]))
            else:
                lines.append(
                    f"{spec.prefix}FiberFromNatToFinData {nat_exact_pattern(index)} _ = refl"
                )
        lines.append(
            f"{spec.prefix}FiberFromNatToFinData {nat_ge_pattern(spec.fiber_count)} p = "
            f"Empty.rec (NatOrder.¬m+n<m {{m = {spec.fiber_count}}} {{n = n}} p)"
        )

    lines.extend(
        [
            "",
            f"{spec.prefix}FiberFromFinData : FD.Fin {spec.fiber_count} → SelectorFiber {spec.selector_agda}",
        ]
    )
    if spec.use_nat_lookup_right_inv:
        lines.append(
            f"{spec.prefix}FiberFromFinData i = "
            f"{spec.prefix}FiberFromNat (FD.toℕ i) (FDP.toℕ<n i)"
        )
    elif spec.use_nat_with_from:
        lines.append(
            f"{spec.prefix}FiberFromFinData i with FD.toℕ i | FDP.toℕ<n i"
        )
        for index, dynamics_id in enumerate(selected_ids):
            constructor = membership_constructor(spec.membership_prefix, dynamics_id)
            lines.append(
                f"... | {nat_exact_pattern(index)} | _ = d{dynamics_id} , {constructor}"
            )
        lines.append(nat_ge_absurd_clause(spec.fiber_count))
    else:
        for index, dynamics_id in enumerate(selected_ids):
            constructor = membership_constructor(spec.membership_prefix, dynamics_id)
            lines.append(
                f"{spec.prefix}FiberFromFinData {fin_data_lhs(index, spec)} = "
                f"d{dynamics_id} , {constructor}"
            )

    lines.extend(
        [
            "",
            f"{spec.prefix}FiberFinDataRightInv :",
            (
                f"  (i : FD.Fin {spec.fiber_count}) → "
                f"{spec.prefix}FiberToFinData ({spec.prefix}FiberFromFinData i) ≡ i"
            ),
        ]
    )
    if spec.use_nat_lookup_right_inv:
        lines.extend(
            [
                f"{spec.prefix}FiberFinDataRightInv i =",
                (
                    f"  {spec.prefix}FiberFromNatToFinData "
                    f"(FD.toℕ i) (FDP.toℕ<n i) ∙ "
                    f"FDP.fromToId' {spec.fiber_count} i (FDP.toℕ<n i)"
                ),
            ]
        )
    elif spec.use_nat_with_right_inv:
        lines.append(
            f"{spec.prefix}FiberFinDataRightInv i with FD.toℕ i | inspect FD.toℕ i | FDP.toℕ<n i"
        )
        for index in range(len(selected_ids)):
            lines.append(
                f"... | {nat_exact_pattern(index)} | [ eq ]ᵢ | _ = "
                f"FDP.inj-toℕ {{k = FDP.fromℕ' {spec.fiber_count} {index} "
                f"({spec.fiber_count - index - 1} , refl)}} {{l = i}} "
                f"(FDP.toFromId' {spec.fiber_count} {index} "
                f"({spec.fiber_count - index - 1} , refl) ∙ sym eq)"
            )
        lines.append(
            f"... | {nat_ge_pattern(spec.fiber_count)} | [ eq ]ᵢ | p = "
            f"Empty.rec (NatOrder.¬m+n<m {{m = {spec.fiber_count}}} {{n = n}} p)"
        )
    else:
        for index in range(len(selected_ids)):
            lines.append(
                f"{spec.prefix}FiberFinDataRightInv {fin_data_lhs(index, spec)} = refl"
            )

    lines.extend(
        [
            "",
            f"{spec.prefix}FiberFinDataLeftInv :",
            (
                f"  (x : SelectorFiber {spec.selector_agda}) → "
                f"{spec.prefix}FiberFromFinData ({spec.prefix}FiberToFinData x) ≡ x"
            ),
        ]
    )
    for dynamics_id in range(dynamics_count):
        if dynamics_id in selected_index:
            constructor = membership_constructor(spec.membership_prefix, dynamics_id)
            if table_rows is not None and "left_inverse_clause" in table_row_by_dynamics[dynamics_id]:
                lines.append(str(table_row_by_dynamics[dynamics_id]["left_inverse_clause"]))
            else:
                lines.append(
                    f"{spec.prefix}FiberFinDataLeftInv (d{dynamics_id} , {constructor}) = refl"
                )
        else:
            lines.append(f"{spec.prefix}FiberFinDataLeftInv (d{dynamics_id} , ())")

    lines.extend(
        [
            "",
            f"{spec.prefix}FiberFinDataIso : Iso (SelectorFiber {spec.selector_agda}) (FD.Fin {spec.fiber_count})",
            (
                f"{spec.prefix}FiberFinDataIso = "
                f"iso {spec.prefix}FiberToFinData {spec.prefix}FiberFromFinData "
                f"{spec.prefix}FiberFinDataRightInv {spec.prefix}FiberFinDataLeftInv"
            ),
            "",
            f"{spec.prefix}FiberFinDataEquiv : SelectorFiber {spec.selector_agda} ≃ FD.Fin {spec.fiber_count}",
            f"{spec.prefix}FiberFinDataEquiv = isoToEquiv {spec.prefix}FiberFinDataIso",
            "",
            f"{spec.prefix}FiberEquivFin : SelectorFiber {spec.selector_agda} ≃ Fin {spec.fiber_count}",
            (
                f"{spec.prefix}FiberEquivFin = "
                f"compEquiv {spec.prefix}FiberFinDataEquiv (FinData≃Fin {spec.fiber_count})"
            ),
            "",
            f"{spec.index_type_name} : Set",
            f"{spec.index_type_name} = Fin {spec.fiber_count}",
        ]
    )
    return "\n".join(lines) + "\n"


def singleton_fiber_block(
    fiber: Mapping[str, Any],
    dynamics_count: int,
    *,
    selector_to_agda: Mapping[str, str],
    selector_prefix: Mapping[str, str],
    membership_prefix: Mapping[str, str],
) -> list[str]:
    selector_key = str(fiber["selector"])
    selector = selector_to_agda[selector_key]
    prefix = selector_prefix[selector_key]
    move_id = int(fiber["selected_move_orbit_ids"][0])
    constructor = membership_constructor(membership_prefix[selector_key], move_id)
    lines = [
        "",
        f"{prefix}SingletonFiberToFinData : SelectorFiber {selector} → FD.Fin 1",
    ]
    for dynamics_id in range(dynamics_count):
        if dynamics_id == move_id:
            lines.append(f"{prefix}SingletonFiberToFinData (d{move_id} , {constructor}) = FD.zero")
        else:
            lines.append(f"{prefix}SingletonFiberToFinData (d{dynamics_id} , ())")
    lines.extend(
        [
            "",
            f"{prefix}SingletonFiberFromFinData : FD.Fin 1 → SelectorFiber {selector}",
            f"{prefix}SingletonFiberFromFinData FD.zero = d{move_id} , {constructor}",
            "",
            f"{prefix}SingletonFiberRightInv :",
            f"  (i : FD.Fin 1) → {prefix}SingletonFiberToFinData ({prefix}SingletonFiberFromFinData i) ≡ i",
            f"{prefix}SingletonFiberRightInv FD.zero = refl",
            "",
            f"{prefix}SingletonFiberLeftInv :",
            (
                f"  (x : SelectorFiber {selector}) → "
                f"{prefix}SingletonFiberFromFinData ({prefix}SingletonFiberToFinData x) ≡ x"
            ),
        ]
    )
    for dynamics_id in range(dynamics_count):
        if dynamics_id == move_id:
            lines.append(f"{prefix}SingletonFiberLeftInv (d{move_id} , {constructor}) = refl")
        else:
            lines.append(f"{prefix}SingletonFiberLeftInv (d{dynamics_id} , ())")
    lines.extend(
        [
            "",
            f"{prefix}SingletonFiberFinDataIso : Iso (SelectorFiber {selector}) (FD.Fin 1)",
            (
                f"{prefix}SingletonFiberFinDataIso = "
                f"iso {prefix}SingletonFiberToFinData {prefix}SingletonFiberFromFinData "
                f"{prefix}SingletonFiberRightInv {prefix}SingletonFiberLeftInv"
            ),
            "",
            f"{prefix}SingletonFiberFinDataEquiv : SelectorFiber {selector} ≃ FD.Fin 1",
            f"{prefix}SingletonFiberFinDataEquiv = isoToEquiv {prefix}SingletonFiberFinDataIso",
            "",
            f"{prefix}SingletonFiberEquivFin : SelectorFiber {selector} ≃ Fin 1",
            f"{prefix}SingletonFiberEquivFin = compEquiv {prefix}SingletonFiberFinDataEquiv (FinData≃Fin 1)",
        ]
    )
    return lines


def generate_singleton_finite_subtype_agda(
    bridge: Mapping[str, Any],
    *,
    module_name: str,
    selector_to_agda: Mapping[str, str],
    singleton_constructor_to_agda: Mapping[str, str],
    selector_prefix: Mapping[str, str],
    membership_prefix: Mapping[str, str],
) -> str:
    fibers = []
    for fiber in bridge["derived"]["selector_fibers"]:
        if fiber["selector"] in selector_to_agda:
            if int(fiber["selected_count"]) != 1:
                raise ValueError(f"expected singleton selector: {fiber['selector']}")
            fibers.append(fiber)
    dynamics_count = int(bridge["derived"]["bridge_summary"]["dynamics_count"])
    lines = [
        "{-# OPTIONS --cubical --safe --guardedness #-}",
        "",
        f"module {module_name} where",
        "",
        "open import Cubical.Foundations.Prelude",
        "open import Cubical.Foundations.Equiv using (_≃_ ; compEquiv)",
        "open import Cubical.Foundations.Isomorphism using (Iso ; iso ; isoToEquiv)",
        "open import Cubical.Data.Sigma using (Σ ; Σ-syntax)",
        "open import Cubical.Data.Fin.Base using (Fin)",
        "open import Cubical.Data.Fin.Properties using (FinData≃Fin)",
        "import Cubical.Data.FinData.Base as FD",
        "open import C2SelectorFoundation",
        "open import C2SelectorFoundationGenerated",
        "",
        "SelectorFiber : Selector → Set",
        "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d",
        "",
        "data SingletonSelector : Set where",
    ]
    for fiber in fibers:
        lines.append(f"  {singleton_constructor_to_agda[fiber['selector']]} : SingletonSelector")
    lines.extend(["", "singletonSelector : SingletonSelector → Selector"])
    for fiber in fibers:
        selector_key = fiber["selector"]
        lines.append(
            f"singletonSelector {singleton_constructor_to_agda[selector_key]} = {selector_to_agda[selector_key]}"
        )
    for fiber in fibers:
        lines.extend(
            singleton_fiber_block(
                fiber,
                dynamics_count,
                selector_to_agda=selector_to_agda,
                selector_prefix=selector_prefix,
                membership_prefix=membership_prefix,
            )
        )
    lines.extend(
        [
            "",
            "singletonSelectorFiberEquivFin :",
            "  (s : SingletonSelector) → SelectorFiber (singletonSelector s) ≃ Fin 1",
        ]
    )
    for fiber in fibers:
        selector_key = fiber["selector"]
        lines.append(
            f"singletonSelectorFiberEquivFin {singleton_constructor_to_agda[selector_key]} = "
            f"{selector_prefix[selector_key]}SingletonFiberEquivFin"
        )
    lines.extend(["", "SingletonSelectorIndex : Set", "SingletonSelectorIndex = Fin 5"])
    return "\n".join(lines) + "\n"
