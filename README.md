# Q* verifier

This is the v38 audit-grade verifier for the finite Q* / Natural Object certificate stack.

## Run

```bash
python certify.py --mode fast --pretty
python certify.py --mode audit --pretty
python certify.py --mode rebuild --pretty
```

Expected headline:

```text
QSTAR_VERIFIER_FULL_CERTIFIED
```

## Tamper tests

```bash
python tests/tamper_tests.py
```

The test suite mutates the root certificate, a layer certificate, a raw array, a manifest, and a theorem-status guardrail. Each mutation must be rejected.

## Release signature

```bash
python tools/verify_release_signature.py
```

The signature is a detached OpenSSL signature over `release/SHA256SUMS.txt`. It verifies integrity of the release checksum ledger using the included public key. Trust in the key itself is external to this bundle.

## Appendix export

```bash
python tools/export_appendix.py
```

This writes TeX appendix tables under `appendices/`.

## Guardrails

The verifier certifies the finite stack and its obstruction results. It does not claim Golay independence from the Golay-conditioned source, a nontrivial strict modular S,T pair, or row canonicity from pair-octad/Wu/6j data alone.
