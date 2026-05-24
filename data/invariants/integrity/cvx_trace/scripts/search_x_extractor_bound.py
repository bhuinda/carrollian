from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data" / "invariants" / "integrity" / "cvx_trace"
TRACE_PATHS = [
    BASE / "traces" / "cadical_lrat_contradiction_4.trace.json",
    BASE / "traces" / "public_dpll_contradiction_4.trace.json",
]
CLASSIFIER_PATH = BASE / "reports" / "solver_opcode_totality_classifier.json"
TOTALITY_REPORT = BASE / "reports" / "solver_opcode_totality_report.json"
PURE_C_REPORT = BASE / "reports" / "pure_c_no_escape_report.json"
REPORT_PATH = BASE / "reports" / "x_extractor_bounded_search_report.json"


EXTRACTOR_TOKENS = {
    "E33",
    "EXTRACTOR",
    "FOURIER",
    "GAUSSIAN",
    "GF(2)",
    "GF2",
    "HIDDEN",
    "PARITY",
    "SPECTRAL",
    "XOR",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def event_strings(event: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("op", "integrity_type", "class_code", "reason", "event_id"):
        value = event.get(key)
        if isinstance(value, str):
            values.append(value)
    return values


def extractor_hits(event: dict[str, Any]) -> list[str]:
    haystack = " ".join(event_strings(event)).upper()
    hits = sorted(token for token in EXTRACTOR_TOKENS if token in haystack)
    checks = event.get("checks", {})
    if checks.get("uses_extension_variable") is True:
        hits.append("EXTENSION_VARIABLE")
    if event.get("integrity_type") == "X":
        hits.append("INTEGRITY_X")
    class_code = str(event.get("class_code", ""))
    if class_code.startswith("X_EXTRACTOR_"):
        hits.append("X_EXTRACTOR_CLASS_CODE")
    return sorted(set(hits))


def observable_public_features(events: list[dict[str, Any]]) -> dict[str, Any]:
    class_codes = sorted({event.get("class_code", "") for event in events})
    ops = sorted({event.get("op", "") for event in events})
    literal_atoms = sorted(
        {
            lit
            for event in events
            for lit in event.get("public_inputs", {}).get("literals", [])
        }
    )
    hint_atoms = sorted(
        {
            hint
            for event in events
            for hint in event.get("public_inputs", {}).get("clause_hints", [])
        }
    )
    literal_pairs = list(itertools.combinations(literal_atoms, 2))
    hint_pairs = list(itertools.combinations(hint_atoms, 2))
    return {
        "class_codes": class_codes,
        "ops": ops,
        "literal_atoms": literal_atoms,
        "hint_atoms": hint_atoms,
        "bounded_literal_pairs_examined": len(literal_pairs),
        "bounded_hint_pairs_examined": len(hint_pairs),
    }


def positive_controls(classifier: dict[str, Any]) -> dict[str, Any]:
    x_codes = classifier.get("extractor_x_class_codes", {})
    v_codes = classifier.get("visible_v_class_codes", {})
    c_codes = classifier.get("public_c_class_codes", {})
    return {
        "x_extractor_class_codes": sorted(x_codes),
        "x_positive_control_count": len(x_codes),
        "v_visible_class_codes": sorted(v_codes),
        "c_public_class_codes": sorted(c_codes),
        "classifier_contains_x_surface": len(x_codes) > 0,
    }


def main() -> int:
    classifier = load_json(CLASSIFIER_PATH)
    totality = load_json(TOTALITY_REPORT)
    pure_c = load_json(PURE_C_REPORT)
    traces = [load_json(path) for path in TRACE_PATHS]
    events = [
        event
        for trace in traces
        for event in trace.get("events", [])
    ]

    detected: list[dict[str, Any]] = []
    for trace, path in zip(traces, TRACE_PATHS):
        for event in trace.get("events", []):
            hits = extractor_hits(event)
            if hits:
                detected.append(
                    {
                        "trace_path": rel(path),
                        "trace_id": trace.get("trace_id"),
                        "event_id": event.get("event_id"),
                        "class_code": event.get("class_code"),
                        "integrity_type": event.get("integrity_type"),
                        "hits": hits,
                    }
                )

    public_features = observable_public_features(events)
    controls = positive_controls(classifier)
    antecedents = {
        "totality_passed": totality.get("status") == "SOLVER_OPCODE_TOTALITY_WITNESS_PASS",
        "pure_c_no_escape_passed": pure_c.get("status") == "PURE_C_NO_ESCAPE_WITNESS_PASS",
        "accepted_trace_residue_count": totality.get("accepted_trace_residue_count"),
        "pure_c_trace_count": pure_c.get("trace_count"),
        "pure_c_event_count": pure_c.get("event_count"),
    }
    pass_condition = (
        not detected
        and antecedents["totality_passed"]
        and antecedents["pure_c_no_escape_passed"]
        and antecedents["accepted_trace_residue_count"] == 0
        and controls["classifier_contains_x_surface"]
    )
    report = {
        "schema": "d20.integrity.x_extractor_bounded_search.v1",
        "status": (
            "X_EXTRACTOR_BOUNDED_SEARCH_NO_EXTRACTOR_FOUND"
            if pass_condition
            else "X_EXTRACTOR_BOUNDED_SEARCH_REQUIRES_REVIEW"
        ),
        "search_scope": {
            "trace_paths": [rel(path) for path in TRACE_PATHS],
            "trace_count": len(traces),
            "event_count": len(events),
            "bounded_candidate_family": "accepted C/V/X trace events, class codes, opcode labels, public literals, public clause hints, and pairwise public atoms",
            "extractor_tokens": sorted(EXTRACTOR_TOKENS),
        },
        "antecedents": antecedents,
        "positive_controls": controls,
        "public_observable_features": public_features,
        "detected_extractor_candidates": detected,
        "result": {
            "x_extractor_present": bool(detected),
            "e33_extraction_present": bool(detected),
            "bounded_search_passed": pass_condition,
        },
        "non_claim": "This is a bounded search over current accepted trace artifacts. It does not prove no polynomial-size X extractor exists for the hidden e33 family.",
        "next_blocker": "v_wall_crossing_accounting",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if pass_condition else 1


if __name__ == "__main__":
    raise SystemExit(main())
