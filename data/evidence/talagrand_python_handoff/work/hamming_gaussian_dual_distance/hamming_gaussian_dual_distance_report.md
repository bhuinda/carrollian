# Hamming Gaussian dual-distance / Krawtchouk audit
Status: `HAMMING_GAUSSIAN_DUAL_DISTANCE_KRAWTCHOUK_PASS`
## Main theorem-grade finite bridge
At the Golay endpoint, the MacWilliams/Krawtchouk dual enumerator has no weights `1..7` and first nonzero dual weight `8`. Because the endpoint is self-dual, this is the same as the extended Golay minimum distance. Therefore every projection to fewer than eight coordinates is uniform.
Consequently, for every support `S` with `|S| < 8` and every real coefficient vector `a`,
```text
L_C(a,S)=sum_{i in S} a_i (-1)^{c_i}, c uniform in G24
```
has exactly the same distribution as the independent Rademacher sum
```text
L_Rad(a,S)=sum_{i in S} a_i eps_i.
```
This proves that the Golay endpoint removes all extra code-induced sparse signed projection obstructions below weight 8.
## Stage summary
| stage | min d | dual d | wt4 roots | affected k<=7 supports | uniform all k<=7 |
|---|---:|---:|---:|---:|---:|
| C0_H8_oplus_3 | 4 | 4 | 42 | 53742 | False |
| C1_neighbor_1 | 4 | 4 | 18 | 23862 | False |
| C2_neighbor_2 | 4 | 4 | 6 | 8106 | False |
| C3_Golay_endpoint | 8 | 8 | 0 | 0 | True |

## Endpoint low dual weights
```json
{
  "1": 0,
  "2": 0,
  "3": 0,
  "4": 0,
  "5": 0,
  "6": 0,
  "7": 0
}
```
## Interpretation
The prior brute sparse signed audit observed one baseline distribution per support size at the Golay endpoint through k<=5. This audit explains why that must persist for every support size k<8 and every real coefficient vector: it is forced by dual distance 8.
## Boundary
This still does not prove full multivariate convex order or Talagrand equivalence. It proves the complete below-weight-8 sparse projection collapse to the independent Rademacher baseline. The remaining analytic bridge is Rademacher-to-Gaussian convex-order calibration, then extension from sparse projections to arbitrary projections.
