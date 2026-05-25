#!/usr/bin/env python3
import argparse
from pathlib import Path


def parse_frat_addition(line):
    parts = line.strip().split()
    if not parts or parts[0] != "a" or len(parts) < 4:
        return None
    clause_id = parts[1]
    try:
        first_zero = parts.index("0", 2)
    except ValueError:
        return None
    literals = parts[2:first_zero]
    hints = []
    rest = parts[first_zero + 1 :]
    if rest:
        if rest[0] != "l":
            return None
        try:
            second_zero = rest.index("0", 1)
        except ValueError:
            return None
        hints = rest[1:second_zero]
    if not hints:
        return None
    return " ".join([clause_id, *literals, "0", *hints, "0"])


def extract_file(frat_path, out_path):
    lines = []
    for line in Path(frat_path).read_text(encoding="utf-8", errors="ignore").splitlines():
        extracted = parse_frat_addition(line)
        if extracted is not None:
            lines.append(extracted)
    Path(out_path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frat")
    parser.add_argument("out")
    args = parser.parse_args()
    count = extract_file(args.frat, args.out)
    print(f"extracted_lrat_lines={count}")


if __name__ == "__main__":
    main()
