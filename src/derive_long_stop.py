from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_cls import (
        EPSILONS,
        HORIZON,
        OUT_DIR as LONG_CLS_DIR,
        STATUS as LONG_CLS_STATUS,
    )
    from .derive_long_mart import (
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OUT_DIR as LONG_MART_DIR,
        STATUS as LONG_MART_STATUS,
        fiber_moments,
        grouped_weights,
        transport_edges,
    )
    from .derive_long_prob import (
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from .derive_long_dual import STATUS as LONG_DUAL_STATUS
    from .derive_long_path import STATUS as LONG_PATH_STATUS
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_cls import (
        EPSILONS,
        HORIZON,
        OUT_DIR as LONG_CLS_DIR,
        STATUS as LONG_CLS_STATUS,
    )
    from derive_long_mart import (
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OUT_DIR as LONG_MART_DIR,
        STATUS as LONG_MART_STATUS,
        fiber_moments,
        grouped_weights,
        transport_edges,
    )
    from derive_long_prob import (
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from derive_long_dual import STATUS as LONG_DUAL_STATUS
    from derive_long_path import STATUS as LONG_PATH_STATUS
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_stop"
STATUS = "LONG_STOP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_CLS_REPORT = LONG_CLS_DIR / "report.json"
LONG_CLS_TAIL = LONG_CLS_DIR / "tail.csv"
LONG_CLS_TABLES = LONG_CLS_DIR / "tables.npz"
LONG_MART_REPORT = LONG_MART_DIR / "report.json"
LONG_MART_EDGE = LONG_MART_DIR / "edge.csv"
LONG_MART_LEVEL = LONG_MART_DIR / "level.csv"
LONG_MART_TABLES = LONG_MART_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_stop.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_stop.py"

TAIL_TEXT_HASH = "246f23496f11bbbc0bd9d815247d2d34e91a150d5826007766c5b5f87052a8f2"
STOP_TEXT_HASH = "97ea048f456eeb860ea290d7db2e437e48c4f8044d0ff02ec37aaf6f23d625e9"
COMPARE_TEXT_HASH = "82a89bed16fb1b859b82ea20b79c214d01cad06033c058a8a487bb40d4a78e60"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

TAIL_COLUMNS = [
    "sample_count",
    "epsilon_id",
    "eps_num",
    "eps_den",
    *prefixed_fraction_columns("tail_prob"),
    *prefixed_fraction_columns("cheb_bound"),
    *prefixed_fraction_columns("gap"),
    "gap_nonnegative_flag",
]
STOP_COLUMNS = [
    "horizon",
    "epsilon_id",
    "eps_num",
    "eps_den",
    *prefixed_fraction_columns("stopped_prob"),
    *prefixed_fraction_columns("union_bound"),
    *prefixed_fraction_columns("gap"),
    "gap_nonnegative_flag",
]
COMPARE_COLUMNS = [
    "compare_id",
    "epsilon_count",
    "horizon",
    "long_cls_tail_row_count",
    "long_cls_tail_gap_count",
    "long_stop_tail_row_count",
    "long_stop_tail_gap_count",
    "long_stop_stop_row_count",
    "long_stop_stop_gap_count",
    "tail_grammar_match_flag",
    "input_cls_certified_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "horizon",
    "epsilon_count",
    "tail_row_count",
    "tail_gap_nonnegative_count",
    "stop_row_count",
    "stop_gap_nonnegative_count",
    "compare_row_count",
    "long_cls_tail_gap_count",
    "tail_prob_num_mod_sum_1000000007",
    "tail_gap_num_mod_sum_1000000007",
    "stopped_prob_num_mod_sum_1000000007",
    "union_bound_num_mod_sum_1000000007",
    "stop_gap_num_mod_sum_1000000007",
    "max_tail_prob_num_digits",
    "max_tail_prob_den_digits",
    "max_stopped_prob_num_digits",
    "max_stopped_prob_den_digits",
    "grammar_match_flag",
    "input_long_prob_certified",
    "input_long_dual_certified",
    "input_long_path_certified",
    "input_long_mart_certified",
    "input_long_cls_certified",
    "current_dual_tail_flag",
    "current_stopped_tail_flag",
    "current_optional_union_bound_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def load_inputs() -> dict[str, Any]:
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    input_reports = {
        "long_prob": load_json(LONG_PROB_REPORT),
        "long_dual": load_json(LONG_DUAL_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
        "long_mart": load_json(LONG_MART_REPORT),
        "long_cls": load_json(LONG_CLS_REPORT),
    }
    return {
        "path_rows": path_rows,
        "input_reports": input_reports,
    }


def tail_event(sum_value: int, sample_count: int, mean: Fraction, epsilon: Fraction) -> bool:
    return abs(Fraction(sum_value, sample_count) - mean) >= epsilon


def build_moments(
    groups: dict[int, list[dict[str, int]]]
) -> dict[int, dict[str, Any]]:
    moments: dict[int, dict[str, Any]] = {}
    for sample_count, rows in sorted(groups.items()):
        weight_total, mean, variance = fiber_moments(rows, sample_count)
        moments[sample_count] = {
            "weight_total": weight_total,
            "mean": mean,
            "variance": variance,
        }
    return moments


def transition_probabilities(
    groups: dict[int, list[dict[str, int]]]
) -> dict[int, dict[int, list[tuple[int, Fraction]]]]:
    transitions: dict[int, dict[int, list[tuple[int, Fraction]]]] = {}
    for sample_count in range(1, max(groups)):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        edges, _, target_total = transport_edges(source, target)
        source_weight = {row["sum_value"]: row["weight"] for row in source}
        by_source: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
        for from_sum, to_sum, mass in edges:
            probability = Fraction(mass, source_weight[from_sum] * target_total)
            by_source[from_sum].append((to_sum, probability))
        transitions[sample_count] = dict(by_source)
    return transitions


def build_tail_rows(
    groups: dict[int, list[dict[str, int]]],
    moments: dict[int, dict[str, Any]],
) -> list[dict[str, int]]:
    tail_rows: list[dict[str, int]] = []
    for sample_count in range(1, HORIZON + 1):
        rows = groups[sample_count]
        mean = moments[sample_count]["mean"]
        variance = moments[sample_count]["variance"]
        weight_total = moments[sample_count]["weight_total"]
        for epsilon_id, epsilon in EPSILONS:
            tail_mass = sum(
                row["weight"]
                for row in rows
                if tail_event(row["sum_value"], sample_count, mean, epsilon)
            )
            tail_prob = Fraction(tail_mass, weight_total)
            cheb_bound = variance / (epsilon * epsilon)
            gap = cheb_bound - tail_prob
            row = {
                "sample_count": sample_count,
                "epsilon_id": epsilon_id,
                "eps_num": epsilon.numerator,
                "eps_den": epsilon.denominator,
                "gap_nonnegative_flag": int(gap >= 0),
            }
            row.update(prefixed_fraction_fields("tail_prob", tail_prob))
            row.update(prefixed_fraction_fields("cheb_bound", cheb_bound))
            row.update(prefixed_fraction_fields("gap", gap))
            tail_rows.append(row)
    return tail_rows


def build_stop_rows(
    groups: dict[int, list[dict[str, int]]],
    moments: dict[int, dict[str, Any]],
    transitions: dict[int, dict[int, list[tuple[int, Fraction]]]],
    tail_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    bound_by_key: dict[tuple[int, int], Fraction] = {}
    for sample_count in range(1, HORIZON + 1):
        for epsilon_id, epsilon in EPSILONS:
            variance = moments[sample_count]["variance"]
            bound_by_key[(sample_count, epsilon_id)] = variance / (epsilon * epsilon)

    stop_rows: list[dict[str, int]] = []
    for epsilon_id, epsilon in EPSILONS:
        current: dict[int, tuple[Fraction, Fraction]] = {}
        first_total = moments[1]["weight_total"]
        first_mean = moments[1]["mean"]
        for row in groups[1]:
            probability = Fraction(row["weight"], first_total)
            hit = tail_event(row["sum_value"], 1, first_mean, epsilon)
            current[row["sum_value"]] = (
                Fraction(0) if hit else probability,
                probability if hit else Fraction(0),
            )
        for horizon in range(1, HORIZON + 1):
            stopped_prob = sum(hit for _, hit in current.values())
            union_bound = sum(
                bound_by_key[(sample_count, epsilon_id)]
                for sample_count in range(1, horizon + 1)
            )
            gap = union_bound - stopped_prob
            row = {
                "horizon": horizon,
                "epsilon_id": epsilon_id,
                "eps_num": epsilon.numerator,
                "eps_den": epsilon.denominator,
                "gap_nonnegative_flag": int(gap >= 0),
            }
            row.update(prefixed_fraction_fields("stopped_prob", stopped_prob))
            row.update(prefixed_fraction_fields("union_bound", union_bound))
            row.update(prefixed_fraction_fields("gap", gap))
            stop_rows.append(row)
            if horizon == HORIZON:
                continue
            next_state: dict[int, tuple[Fraction, Fraction]] = defaultdict(
                lambda: (Fraction(0), Fraction(0))
            )
            next_mean = moments[horizon + 1]["mean"]
            for from_sum, (not_hit_mass, hit_mass) in current.items():
                for to_sum, probability in transitions[horizon][from_sum]:
                    already_not, already_hit = next_state[to_sum]
                    next_hit = tail_event(to_sum, horizon + 1, next_mean, epsilon)
                    if next_hit:
                        already_hit += (not_hit_mass + hit_mass) * probability
                    else:
                        already_not += not_hit_mass * probability
                        already_hit += hit_mass * probability
                    next_state[to_sum] = (already_not, already_hit)
            current = dict(next_state)
    tail_gap_count = sum(row["gap_nonnegative_flag"] for row in tail_rows)
    if tail_gap_count != len(tail_rows):
        raise AssertionError("tail Chebyshev gap failure")
    return stop_rows


def read_long_cls_tail_gap_count() -> tuple[int, int]:
    rows = read_csv_rows(LONG_CLS_TAIL)
    return len(rows), sum(int(row["gap_nonnegative_flag"]) for row in rows)


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    groups = grouped_weights(loaded["path_rows"])
    moments = build_moments(groups)
    transitions = transition_probabilities(groups)
    tail_rows = build_tail_rows(groups, moments)
    stop_rows = build_stop_rows(groups, moments, transitions, tail_rows)
    long_cls_tail_count, long_cls_tail_gap_count = read_long_cls_tail_gap_count()
    compare_rows = [
        {
            "compare_id": 0,
            "epsilon_count": len(EPSILONS),
            "horizon": HORIZON,
            "long_cls_tail_row_count": long_cls_tail_count,
            "long_cls_tail_gap_count": long_cls_tail_gap_count,
            "long_stop_tail_row_count": len(tail_rows),
            "long_stop_tail_gap_count": sum(
                row["gap_nonnegative_flag"] for row in tail_rows
            ),
            "long_stop_stop_row_count": len(stop_rows),
            "long_stop_stop_gap_count": sum(
                row["gap_nonnegative_flag"] for row in stop_rows
            ),
            "tail_grammar_match_flag": int(
                long_cls_tail_count == len(tail_rows)
                and len(tail_rows) == len(stop_rows)
                and HORIZON == 16
                and len(EPSILONS) == 3
            ),
            "input_cls_certified_flag": int(
                loaded["input_reports"]["long_cls"].get("status") == LONG_CLS_STATUS
            ),
        }
    ]
    fraction_rows = tail_rows + stop_rows
    obs = {
        "horizon": HORIZON,
        "epsilon_count": len(EPSILONS),
        "tail_row_count": len(tail_rows),
        "tail_gap_nonnegative_count": sum(
            row["gap_nonnegative_flag"] for row in tail_rows
        ),
        "stop_row_count": len(stop_rows),
        "stop_gap_nonnegative_count": sum(
            row["gap_nonnegative_flag"] for row in stop_rows
        ),
        "compare_row_count": len(compare_rows),
        "long_cls_tail_gap_count": long_cls_tail_gap_count,
        "tail_prob_num_mod_sum_1000000007": sum(
            row["tail_prob_num_mod_1000000007"] for row in tail_rows
        )
        % MOD_PRIMES[0],
        "tail_gap_num_mod_sum_1000000007": sum(
            row["gap_num_mod_1000000007"] for row in tail_rows
        )
        % MOD_PRIMES[0],
        "stopped_prob_num_mod_sum_1000000007": sum(
            row["stopped_prob_num_mod_1000000007"] for row in stop_rows
        )
        % MOD_PRIMES[0],
        "union_bound_num_mod_sum_1000000007": sum(
            row["union_bound_num_mod_1000000007"] for row in stop_rows
        )
        % MOD_PRIMES[0],
        "stop_gap_num_mod_sum_1000000007": sum(
            row["gap_num_mod_1000000007"] for row in stop_rows
        )
        % MOD_PRIMES[0],
        "max_tail_prob_num_digits": max(
            row["tail_prob_num_digits"] for row in tail_rows
        ),
        "max_tail_prob_den_digits": max(
            row["tail_prob_den_digits"] for row in tail_rows
        ),
        "max_stopped_prob_num_digits": max(
            row["stopped_prob_num_digits"] for row in stop_rows
        ),
        "max_stopped_prob_den_digits": max(
            row["stopped_prob_den_digits"] for row in stop_rows
        ),
        "grammar_match_flag": compare_rows[0]["tail_grammar_match_flag"],
        "input_long_prob_certified": int(
            loaded["input_reports"]["long_prob"].get("status") == LONG_PROB_STATUS
        ),
        "input_long_dual_certified": int(
            loaded["input_reports"]["long_dual"].get("status") == LONG_DUAL_STATUS
        ),
        "input_long_path_certified": int(
            loaded["input_reports"]["long_path"].get("status") == LONG_PATH_STATUS
        ),
        "input_long_mart_certified": int(
            loaded["input_reports"]["long_mart"].get("status") == LONG_MART_STATUS
        ),
        "input_long_cls_certified": compare_rows[0]["input_cls_certified_flag"],
        "current_dual_tail_flag": int(
            sum(row["gap_nonnegative_flag"] for row in tail_rows) == len(tail_rows)
        ),
        "current_stopped_tail_flag": int(
            sum(row["gap_nonnegative_flag"] for row in stop_rows) == len(stop_rows)
        ),
        "current_optional_union_bound_flag": int(
            sum(row["gap_nonnegative_flag"] for row in stop_rows) == len(stop_rows)
        ),
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    tail_hash = hashlib.sha256(
        digest_text(TAIL_COLUMNS, tail_rows).encode("ascii")
    ).hexdigest()
    stop_hash = hashlib.sha256(
        digest_text(STOP_COLUMNS, stop_rows).encode("ascii")
    ).hexdigest()
    compare_hash = hashlib.sha256(
        digest_text(COMPARE_COLUMNS, compare_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": loaded["input_reports"],
        "tail_rows": tail_rows,
        "stop_rows": stop_rows,
        "compare_rows": compare_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "tail_table": table_from_rows(TAIL_COLUMNS, tail_rows),
        "stop_table": table_from_rows(STOP_COLUMNS, stop_rows),
        "compare_table": table_from_rows(COMPARE_COLUMNS, compare_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "tail_hash": tail_hash,
        "stop_hash": stop_hash,
        "compare_hash": compare_hash,
        "fraction_row_count": len(fraction_rows),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            obs["input_long_prob_certified"],
            obs["input_long_dual_certified"],
            obs["input_long_path_certified"],
            obs["input_long_mart_certified"],
            obs["input_long_cls_certified"],
        )
        == (1, 1, 1, 1, 1),
        "tail_fingerprint_exact": (
            obs["tail_row_count"],
            obs["tail_gap_nonnegative_count"],
            obs["tail_prob_num_mod_sum_1000000007"],
            obs["tail_gap_num_mod_sum_1000000007"],
            obs["max_tail_prob_num_digits"],
            obs["max_tail_prob_den_digits"],
            rows["tail_hash"],
        )
        == (
            48,
            48,
            228_485_013,
            455_837_620,
            13,
            15,
            TAIL_TEXT_HASH,
        ),
        "stopped_tail_fingerprint_exact": (
            obs["stop_row_count"],
            obs["stop_gap_nonnegative_count"],
            obs["stopped_prob_num_mod_sum_1000000007"],
            obs["union_bound_num_mod_sum_1000000007"],
            obs["stop_gap_num_mod_sum_1000000007"],
            obs["max_stopped_prob_num_digits"],
            obs["max_stopped_prob_den_digits"],
            rows["stop_hash"],
        )
        == (
            48,
            48,
            16_587,
            93_091_961,
            543_186_879,
            4,
            4,
            STOP_TEXT_HASH,
        ),
        "grammar_comparison_exact": (
            obs["compare_row_count"],
            obs["long_cls_tail_gap_count"],
            obs["grammar_match_flag"],
            rows["compare_hash"],
        )
        == (1, 48, 1, COMPARE_TEXT_HASH),
        "current_representation_exact": (
            obs["current_dual_tail_flag"],
            obs["current_stopped_tail_flag"],
            obs["current_optional_union_bound_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["tail_table"].shape),
            tuple(rows["stop_table"].shape),
            tuple(rows["compare_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (48, len(TAIL_COLUMNS)),
            (48, len(STOP_COLUMNS)),
            (1, len(COMPARE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "dual_transport_stopped_tail_certificate",
        "horizon": HORIZON,
        "epsilons": [
            {"epsilon_id": epsilon_id, "num": eps.numerator, "den": eps.denominator}
            for epsilon_id, eps in EPSILONS
        ],
        "tail": {
            "row_count": obs["tail_row_count"],
            "gap_nonnegative_count": obs["tail_gap_nonnegative_count"],
            "tail_prob_num_mod_sum_1000000007": obs[
                "tail_prob_num_mod_sum_1000000007"
            ],
            "gap_num_mod_sum_1000000007": obs["tail_gap_num_mod_sum_1000000007"],
            "fraction_text_sha256": rows["tail_hash"],
            "table_sha256": sha_array(rows["tail_table"]),
        },
        "stopped_tail": {
            "row_count": obs["stop_row_count"],
            "gap_nonnegative_count": obs["stop_gap_nonnegative_count"],
            "stopped_prob_num_mod_sum_1000000007": obs[
                "stopped_prob_num_mod_sum_1000000007"
            ],
            "union_bound_num_mod_sum_1000000007": obs[
                "union_bound_num_mod_sum_1000000007"
            ],
            "gap_num_mod_sum_1000000007": obs["stop_gap_num_mod_sum_1000000007"],
            "fraction_text_sha256": rows["stop_hash"],
            "table_sha256": sha_array(rows["stop_table"]),
        },
        "comparison": {
            "long_cls_tail_gap_count": obs["long_cls_tail_gap_count"],
            "grammar_match_flag": bool(obs["grammar_match_flag"]),
            "fraction_text_sha256": rows["compare_hash"],
            "table_sha256": sha_array(rows["compare_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    stop_payload = {
        "schema": "long.stop@1",
        "object": "dual_transport_stopped_tail_certificate",
        "status": STATUS if all(checks.values()) else "LONG_STOP_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.stop.report@1",
        "status": stop_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_stop turns the long_mart finite transport operator into "
            "dual-measure tail and stopped-tail certificates. For epsilons "
            "1/2, 1/3, and 1/4 through horizon 16, every per-level "
            "Chebyshev gap is nonnegative and every stopped hitting event is "
            "bounded by the finite union of those Chebyshev bounds. The "
            "epsilon/horizon grammar is matched against long_cls, but the "
            "measure is the long_prob dual transport law rather than the "
            "public long_conv Markov law."
        ),
        "stage_protocol": {
            "draft": "read long_prob, long_mart, long_path, and long_cls finite concentration artifacts",
            "witness": "compute exact dual per-level tails and stopped hitting probabilities along the finite transport",
            "coherence": "check Chebyshev gaps, stopped union-bound gaps, grammar match, statuses, hashes, and shapes",
            "closure": "emit dual stopped-tail certificate with measure boundary recorded",
            "emit": "write long_stop artifacts and verifier hook",
        },
        "inputs": {
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {"status": input_reports["long_prob"].get("status")},
            ),
            "long_prob_dist": input_entry(LONG_PROB_DIST),
            "long_prob_moment": input_entry(LONG_PROB_MOMENT),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "long_dual_report": input_entry(
                LONG_DUAL_REPORT,
                {"status": input_reports["long_dual"].get("status")},
            ),
            "long_dual_path": input_entry(LONG_DUAL_PATH),
            "long_dual_tables": input_entry(LONG_DUAL_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": input_reports["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_mart_report": input_entry(
                LONG_MART_REPORT,
                {"status": input_reports["long_mart"].get("status")},
            ),
            "long_mart_edge": input_entry(LONG_MART_EDGE),
            "long_mart_level": input_entry(LONG_MART_LEVEL),
            "long_mart_tables": input_entry(LONG_MART_TABLES),
            "long_cls_report": input_entry(
                LONG_CLS_REPORT,
                {"status": input_reports["long_cls"].get("status")},
            ),
            "long_cls_tail": input_entry(LONG_CLS_TAIL),
            "long_cls_tables": input_entry(LONG_CLS_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "stop": relpath(OUT_DIR / "stop.json"),
            "tail_csv": relpath(OUT_DIR / "tail.csv"),
            "stop_csv": relpath(OUT_DIR / "stop.csv"),
            "compare_csv": relpath(OUT_DIR / "compare.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exact dual per-level tail probabilities under long_prob through horizon 16",
                "nonnegative Chebyshev gaps for the dual measure on epsilons 1/2, 1/3, and 1/4",
                "exact stopped hitting probabilities along the long_mart transport",
                "nonnegative finite union-bound gaps for stopped hitting events",
                "epsilon/horizon grammar agreement with long_cls tail windows",
            ],
            "does_not_certify_because_out_of_scope": [
                "optimal stopping bounds",
                "a public Markov-law stopped process",
                "a semantic C985 associator process",
                "an infinite-horizon optional-stopping theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_dlim: extract the finite drift-limit obstruction from "
            "long_mart/long_stop, separating the single first-level drift "
            "defect from the eventual submartingale regime."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.stop.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.stop.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "stop": stop_payload,
        "tail_csv": csv_text(TAIL_COLUMNS, rows["tail_rows"]),
        "stop_csv": csv_text(STOP_COLUMNS, rows["stop_rows"]),
        "compare_csv": csv_text(COMPARE_COLUMNS, rows["compare_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tail_table": rows["tail_table"],
        "stop_table": rows["stop_table"],
        "compare_table": rows["compare_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "stop.json", payloads["stop"])
    (OUT_DIR / "tail.csv").write_text(payloads["tail_csv"], encoding="utf-8")
    (OUT_DIR / "stop.csv").write_text(payloads["stop_csv"], encoding="utf-8")
    (OUT_DIR / "compare.csv").write_text(payloads["compare_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tail_table=payloads["tail_table"],
        stop_table=payloads["stop_table"],
        compare_table=payloads["compare_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
