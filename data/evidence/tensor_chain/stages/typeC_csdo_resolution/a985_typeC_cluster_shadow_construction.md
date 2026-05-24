# A985 Type-C Cluster-Shadow Construction
**Status:** `A985_CLUSTER_SHADOW_CONSTRUCTED_PASS`
**Certificate SHA-256:** `3ba139c038f2c3cc02c612b090af7f85be894c65d60116066f683ff1804d7f55`
## Precise theorem
Construct the six-object incidence category
\[
\mathcal I_{985}^{C}:=\bigl(H_6,\operatorname{Hom}(i,j)=e_iA_{985}e_j\bigr),
\]
with composition inherited from the coherent multiplication tensor of \(A_{985}\). Its decategorified Hom-dimension matrix is
\[
M=
\begin{pmatrix}
33 & 12 & 8 & 24 & 30 & 32\\
12 & 16 & 4 & 12 & 12 & 20\\
8 & 4 & 14 & 22 & 8 & 20\\
24 & 12 & 22 & 86 & 32 & 64\\
30 & 12 & 8 & 32 & 44 & 44\\
32 & 20 & 20 & 64 & 44 & 104\\
\end{pmatrix},
\qquad \sum_{i,j}M_{ij}=985.
\]
The type-C cluster-shadow functor is
\[
\operatorname{Trop}^{\pm}_{C_3}(A_{985}):
\mathcal I_{985}^{C}
\longrightarrow
\bigl(\Lambda^3H_6,\;D_6\text{-edges},\;\nu_{u/y}\bigr),
\]
followed by the quotient tower
\[
A_{985}\to A_{236}\to A_{42}\to A_{12}.
\]
This is a construction of a finite noncommutative/categorified source for the type-C signed tropical chamber pattern. It is not a claim that \(A_{985}\) is a commutative cluster coordinate algebra.
## Construction data
- Objects: `['B-', 'B+', 'V-', 'V+', 'S-', 'S+']`.
- D6 projective root transitions: `30`.
- Public face states: `|Λ^3H6| = 20`.
- Public graph pentagons: `12`.
- Public graph hexagons: `0`.
- CSDO sign chambers in A42: `4`.
- A12 collapse single image: `True`.

## Four CSDO sign chambers
| class | A42 CSDO order | sign vector | negative coordinates | A12 image |
|---:|---|---|---|---|
| 1 | `['B-', 'S-', 'V-', 'B+', 'S+', 'V+']` | `-+++++` | `['y_{B-,S-}']` | `[7, 11, 8, 7, 11, 8]` |
| 2 | `['B-', 'S-', 'V+', 'B+', 'S+', 'V-']` | `++++-+` | `['y_{V-,S+}']` | `[7, 11, 8, 7, 11, 8]` |
| 3 | `['B-', 'S+', 'V-', 'B+', 'S-', 'V+']` | `++-+++` | `['y_{B-,V+}']` | `[7, 11, 8, 7, 11, 8]` |
| 4 | `['B-', 'S+', 'V+', 'B+', 'S-', 'V-']` | `++++++` | `[]` | `[7, 11, 8, 7, 11, 8]` |

## Checks
| check | pass |
|---|---:|
| `A985_relation_count_985` | `True` |
| `A985_tensor_support_present` | `True` |
| `M_sum_equals_985` | `True` |
| `M_is_symmetric` | `True` |
| `A42_class_count_42` | `True` |
| `A12_class_count_12` | `True` |
| `A42_to_A12_consistent` | `True` |
| `D6_roots_count_30` | `True` |
| `Lambda3_face_count_20` | `True` |
| `public_ASDO_pentagons_12` | `True` |
| `public_CSDO_hexagons_absent` | `True` |
| `CSDO_sign_chambers_4` | `True` |
| `CSDO_A12_collapse_single_image` | `True` |
| `A236_not_ordinary_center_projection` | `True` |

## Consequence
The constructed object is the span/functor
\[
\mathcal I_{985}^{C}
\xrightarrow{K_0}
A_{985}
\to A_{42}
\xleftarrow{\mathrm{CSDO}}
\{4\text{ signed hexagons}\}
\xrightarrow{\nu}
\{\pm1\}^{6}
\to A_{12}.
\]
Thus \(A_{985}\) is the finite incidence body whose signed quotient shadows recover the type-C tropical chambers.
