# Registered support raw matrix units

## Result

\[
\boxed{\texttt{D20_NESTED_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED}}
\]

This stage propagates the certified raw-orbital block matrix units back into the registered nested-pointer support table.
It also resolves the four legacy sectors appearing in the public-zero support theorem against the raw separating-center sector order.

## Legacy-to-raw sector matching

The raw central idempotent package produced primitive central idempotents in a separating-center order, while the registered null supports use legacy theorem labels.
The match is obtained by comparing identity-orbit coefficient fingerprints on the six identity relations:

\[
(6,163,227,349,618,893).
\]

| legacy sector | raw sector | block dimension | reason |
|---:|---:|---:|---|
| 6 | 9 | 2 | UNIQUE_IDENTITY_FINGERPRINT_MATCH |
| 25 | 30 | 1 | UNIQUE_IDENTITY_FINGERPRINT_MATCH |
| 26 | 29 | 1 | UNIQUE_IDENTITY_FINGERPRINT_MATCH |
| 33 | 19 | 2 | UNIQUE_IDENTITY_FINGERPRINT_MATCH |


So the public-zero registered supports resolve as:

\[
\Pi_{33}\mapsto e_{19}^{\rm raw},
\qquad
\{25,26\}\mapsto\{30,29\}_{\rm raw},
\qquad
\{6,26\}\mapsto\{9,29\}_{\rm raw}.
\]

## Propagated support matrix units

For every registered support \(C\), the package now records the raw-sector support \(C_{\rm raw}\) and the explicit matrix units

\[
u[s;i,j]=\sum_\alpha c_{sij,\alpha}R_\alpha
\]

belonging to every raw block \(s\in C_{\rm raw}\).

| quantity | value |
|---|---:|
| registered supports | 7 |
| support matrix-unit manifest rows | 1011 |
| registered null-support COO coefficients | 832 |
| registered Hom pairs | 49 |
| Hom rank total over registered pairs | 1109 |


## Meaning

The nested-pointer support table is now grounded as:

\[
(\text{public token},\text{legacy support},\text{raw sector support},\text{raw orbital matrix units}).
\]

This closes the gap between the public-zero support theorem and the explicit raw-orbital matrix-unit theorem for the registered null supports.

## Boundary

This package resolves only the legacy sectors needed by the registered public-zero supports:

\[
6,25,26,33.
\]

It does not relabel all 39 sectors. The next global target is:

\[
\boxed{\texttt{D20\_NESTED\_POINTER\_A985\_FULL\_LEGACY\_SECTOR\_MATCH\_CERTIFIED}}
\]

which requires a full invariant fingerprint table for all 39 legacy sector labels.
