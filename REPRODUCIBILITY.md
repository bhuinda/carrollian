# Reproducibility

## Supported run modes

```bash
python certify.py --mode fast --pretty
python certify.py --mode audit --pretty
python certify.py --mode rebuild --pretty
```

- `fast`: validates certificates, schemas, declared statuses, file hashes, root hash, and dependency-hash manifest.
- `audit`: runs `fast` plus array-level hashes and lightweight raw-data invariants.
- `rebuild`: runs `audit` and reports which expensive reconstruction scripts are present. This compact release keeps historical certificates and lightweight sources; it is not a full expensive reconstruction archive.

## Environment

- Python 3.10+
- NumPy for `audit` mode
- No network access required
- No `jsonschema` dependency; schemas are included as formal documentation and the verifier performs built-in validation.

## Canonical field

The certified finite-field computations are primarily over `F_1000003`. A multi-prime replay is a recommended hardening task, not part of this compact release.

## Release reproducibility

Use:

```bash
python tools/make_release.py --out verifier_core_v37_hash_chain_schema_release.zip
```

The release builder writes sorted ZIP entries with fixed timestamps.

## v38 clean-room protocol

Run `python certify.py --mode fast --pretty`, `python certify.py --mode audit --pretty`, `python certify.py --mode rebuild --pretty`, `python tests/tamper_tests.py`, and `python tools/verify_release_signature.py`. The rebuild mode in this compact release replays the audit boundary and declares the expensive historical reconstruction boundary.
