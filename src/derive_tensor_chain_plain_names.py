#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Pattern

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "tensor_chain"
INDEX = BASE / "index.json"
OUT = BASE / "plain_name_view.json"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_index() -> dict[str, Any]:
    if not INDEX.exists():
        return {"plain_names": {}}
    return json.loads(INDEX.read_text(encoding="utf-8"))


LegacyRule = tuple[str, str, Pattern[str]]


def replacement_rules(index: dict[str, Any]) -> list[LegacyRule]:
    plain_names = index.get("plain_names", {})
    if not isinstance(plain_names, dict):
        return []

    rules: list[LegacyRule] = []
    for source, target in plain_names.items():
        source_s = str(source)
        target_s = str(target)
        if not source_s or not target_s or source_s == target_s:
            continue
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(source_s)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        rules.append((source_s, target_s, pattern))
    return sorted(rules, key=lambda item: len(item[0]), reverse=True)


def plain_name(text: str, rules: list[LegacyRule]) -> str:
    out = text
    for _source, target, pattern in rules:
        out = pattern.sub(target, out)
    out = out.lower()
    out = re.sub(r"__+", "_", out)
    out = out.replace("_-", "-").replace("-_", "-")
    return out


def legacy_hits(text: str, rules: list[LegacyRule]) -> list[str]:
    hits: list[str] = []
    for source, _target, pattern in rules:
        if pattern.search(text):
            hits.append(source)
    return hits


def csv_columns(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return next(reader, [])


def json_top_level_keys(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
    return sorted(str(key) for key in payload.keys())


def npz_array_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(Path(name).stem for name in zf.namelist() if name.endswith(".npy"))


def alias_rows(names: list[str], rules: list[LegacyRule]) -> list[dict[str, str]]:
    return [{"source": name, "plain": plain_name(name, rules)} for name in names]


def changed_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if row["source"] != row["plain"])


def collect_legacy_hits(
    section: str,
    container: str,
    rows: list[dict[str, str]],
    rules: list[LegacyRule],
    out: list[dict[str, str]],
) -> None:
    for row in rows:
        hits = legacy_hits(row["plain"], rules)
        for term in hits:
            out.append({
                "section": section,
                "container": container,
                "source": row["source"],
                "plain": row["plain"],
                "term": term,
            })


def derive() -> dict[str, Any]:
    index = load_index()
    rules = replacement_rules(index)

    file_aliases: list[dict[str, Any]] = []
    csv_header_aliases: dict[str, Any] = {}
    json_key_aliases: dict[str, Any] = {}
    npz_array_aliases: dict[str, Any] = {}
    legacy_plain_token_hits: list[dict[str, str]] = []

    for path in sorted(BASE.rglob("*")):
        if not path.is_file() or path == OUT:
            continue

        rel = path.relative_to(BASE).as_posix()
        plain_rel = plain_name(rel, rules)
        file_aliases.append({
            "source": rel,
            "plain": plain_rel,
            "changed": rel != plain_rel,
            "size": path.stat().st_size,
            "sha256": sha_file(path),
        })
        collect_legacy_hits("file_aliases", rel, [{"source": rel, "plain": plain_rel}], rules, legacy_plain_token_hits)

        if path.suffix.lower() == ".csv":
            try:
                rows = alias_rows(csv_columns(path), rules)
                collect_legacy_hits("csv_header_aliases", rel, rows, rules, legacy_plain_token_hits)
                csv_header_aliases[rel] = {
                    "columns": rows,
                    "changed_column_count": changed_count(rows),
                }
            except Exception as exc:
                csv_header_aliases[rel] = {"unreadable_csv_header": f"{type(exc).__name__}: {exc}"}
        elif path.suffix.lower() == ".json":
            try:
                rows = alias_rows(json_top_level_keys(path), rules)
                collect_legacy_hits("json_key_aliases", rel, rows, rules, legacy_plain_token_hits)
                json_key_aliases[rel] = {
                    "top_level_keys": rows,
                    "changed_key_count": changed_count(rows),
                }
            except Exception as exc:
                json_key_aliases[rel] = {"unreadable_json_keys": f"{type(exc).__name__}: {exc}"}
        elif path.suffix.lower() == ".npz":
            try:
                rows = alias_rows(npz_array_names(path), rules)
                collect_legacy_hits("npz_array_aliases", rel, rows, rules, legacy_plain_token_hits)
                npz_array_aliases[rel] = {
                    "arrays": rows,
                    "changed_array_count": changed_count(rows),
                }
            except Exception as exc:
                npz_array_aliases[rel] = {"unreadable_npz_arrays": f"{type(exc).__name__}: {exc}"}

    changed_file_aliases = sum(1 for row in file_aliases if row["changed"])
    changed_csv_headers = sum(
        int(entry.get("changed_column_count", 0))
        for entry in csv_header_aliases.values()
        if isinstance(entry, dict)
    )
    changed_json_keys = sum(
        int(entry.get("changed_key_count", 0))
        for entry in json_key_aliases.values()
        if isinstance(entry, dict)
    )
    changed_npz_arrays = sum(
        int(entry.get("changed_array_count", 0))
        for entry in npz_array_aliases.values()
        if isinstance(entry, dict)
    )

    return {
        "schema": "d20.tensor_chain.plain_name_view.v1",
        "status": "TENSOR_CHAIN_PLAIN_NAME_VIEW_GENERATED",
        "source_folder": "data/tensor_chain",
        "generated_file": "data/tensor_chain/plain_name_view.json",
        "source_preservation": "This is an alias view only. It does not rename or edit source evidence files.",
        "rule_source": "data/tensor_chain/index.json#/plain_names",
        "plain_names": index.get("plain_names", {}),
        "summary": {
            "source_file_count": len(file_aliases),
            "changed_file_alias_count": changed_file_aliases,
            "csv_file_count": len(csv_header_aliases),
            "changed_csv_header_count": changed_csv_headers,
            "json_file_count": len(json_key_aliases),
            "changed_json_key_count": changed_json_keys,
            "npz_file_count": len(npz_array_aliases),
            "changed_npz_array_count": changed_npz_arrays,
            "remaining_legacy_plain_token_count": len(legacy_plain_token_hits),
        },
        "remaining_legacy_plain_token_examples": legacy_plain_token_hits[:25],
        "file_aliases": file_aliases,
        "csv_header_aliases": csv_header_aliases,
        "json_key_aliases": json_key_aliases,
        "npz_array_aliases": npz_array_aliases,
    }


def main() -> None:
    OUT.write_text(json.dumps(derive(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "WROTE", "path": str(OUT.relative_to(ROOT))}, sort_keys=True))


if __name__ == "__main__":
    main()
