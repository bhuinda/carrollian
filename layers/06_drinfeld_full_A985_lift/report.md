# Drinfeld full A985 lift

Status: `DRINFELD_FULL_A985_LIFT_CERTIFIED`

This replaces the broken monolithic Wedderburn lift with a chunked finite-field verifier. It embeds the 39 Drinfeld/Grothendieck primitive idempotents into the full 985-dimensional relation algebra and verifies their algebraic behavior directly against the raw multiplication tensor.

```text
field:                              F_1000003
A985 relation basis:                 985
closed-loop quotient:                297
Drinfeld/Grothendieck sectors:        39
pre-HB closed-loop idempotents:       109
```

## Full A985 idempotent and centrality check

```text
pair products checked:               1521
pairwise orthogonal idempotents:      True
sum to full A985 unit:                True
centrality checked:                   True
scalar centrality equalities:         37838775
centrality failures:                  0
```

This is the missing full sweep:
\[ R_a e_i=e_i R_a \]
for all
\[ a=1,\ldots,985,\qquad i=1,\ldots,39. \]

## Wedderburn recovery

```text
regular trace values:
[100, 36, 16, 25, 16, 4, 4, 1, 9, 9, 1, 25, 16, 4, 25, 16, 9, 16, 36, 1, 4, 4, 4, 9, 1, 1, 1, 16, 25, 16, 16, 100, 4, 4, 1, 81, 144, 121, 64]

block dimensions:
[10, 6, 4, 5, 4, 2, 2, 1, 3, 3, 1, 5, 4, 2, 5, 4, 3, 4, 6, 1, 2, 2, 2, 3, 1, 1, 1, 4, 5, 4, 4, 10, 2, 2, 1, 9, 12, 11, 8]

block histogram:
{'1': 7, '2': 8, '3': 4, '4': 8, '5': 4, '6': 2, '8': 1, '9': 1, '10': 2, '11': 1, '12': 1}

sum d_i^2:                           985
```

Hence the 39 Drinfeld sectors recover the full Wedderburn multiset
\[1^7,2^8,3^4,4^8,5^4,6^2,8,9,10^2,11,12.\]

## Irreducible character table

The table
\[\chi_i(R_a)=\frac{\operatorname{Tr}_{reg}(L_{e_iR_a})}{d_i}\]
was computed for all 39 sectors and all 985 relation-basis elements over \(\mathbb F_{1000003}\).

```text
character table shape:               [39, 985]
character table sha256:              3751bdba9b90c17c6f5658fe45d1d4d76d1692ed8a84ea5e0cc78338245cab34
unit characters equal d_i:            True
regular character reconstructs trace: True
central idempotent character diagonal:True
character support histogram:          {'12': 1, '16': 2, '32': 1, '38': 1, '44': 2, '52': 1, '56': 1, '62': 3, '64': 1, '66': 1, '74': 1, '75': 1, '77': 1, '78': 1, '79': 1, '86': 1, '88': 2, '90': 1, '92': 1, '105': 1, '109': 1, '114': 1, '115': 2, '119': 1, '125': 1, '133': 2, '134': 1, '156': 1, '180': 1, '182': 1, '190': 1, '297': 1}
```

## Dodecad permutation decomposition

```text
permutation ranks:
[360, 108, 72, 120, 72, 18, 18, 3, 9, 9, 1, 15, 16, 2, 10, 72, 18, 72, 6, 6, 36, 18, 36, 6, 2, 1, 3, 12, 30, 72, 24, 180, 6, 36, 3, 216, 216, 528, 144]

multiplicities:
[36, 18, 18, 24, 18, 9, 9, 3, 3, 3, 1, 3, 4, 1, 2, 18, 6, 18, 1, 6, 18, 9, 18, 2, 2, 1, 3, 3, 6, 18, 6, 18, 3, 18, 3, 24, 18, 48, 18]

sum permutation ranks:                2576
rank = d_i * multiplicity:            True
```

## Public diagonal shadows

```text
q42 shadow rank:                      12
q42 active columns:                   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
q12 shadow rank:                      6
q12 active columns:                   [0, 1, 2, 3, 4, 5]
```

## Sector profile table

```text
00  d=10  rank=360  mult=36  pre=5  char_supp= 64  obj=B-,V-,V+,S-,S+
01  d= 6  rank=108  mult=18  pre=5  char_supp=125  obj=B-,V-,V+,S-,S+
02  d= 4  rank= 72  mult=18  pre=2  char_supp= 92  obj=V+,S+
03  d= 5  rank=120  mult=24  pre=3  char_supp=114  obj=V+,S-,S+
04  d= 4  rank= 72  mult=18  pre=3  char_supp=119  obj=B-,S-,S+
05  d= 2  rank= 18  mult= 9  pre=2  char_supp= 52  obj=V-,S+
06  d= 2  rank= 18  mult= 9  pre=2  char_supp= 88  obj=S-,S+
07  d= 1  rank=  3  mult= 3  pre=1  char_supp= 16  obj=B+
08  d= 3  rank=  9  mult= 3  pre=3  char_supp=115  obj=B-,V+,S-
09  d= 3  rank=  9  mult= 3  pre=2  char_supp= 79  obj=V+,S+
10  d= 1  rank=  1  mult= 1  pre=1  char_supp= 16  obj=B+
11  d= 5  rank= 15  mult= 3  pre=4  char_supp=133  obj=V-,V+,S-,S+
12  d= 4  rank= 16  mult= 4  pre=3  char_supp= 66  obj=B+,V-,V+
13  d= 2  rank=  2  mult= 1  pre=2  char_supp=190  obj=V+,S+
14  d= 5  rank= 10  mult= 2  pre=3  char_supp=109  obj=V-,V+,S+
15  d= 4  rank= 72  mult=18  pre=3  char_supp= 77  obj=B-,V-,S-
16  d= 3  rank= 18  mult= 6  pre=1  char_supp= 62  obj=V+
17  d= 4  rank= 72  mult=18  pre=3  char_supp= 74  obj=B-,V+,S-
18  d= 6  rank=  6  mult= 1  pre=6  char_supp=297  obj=B-,B+,V-,V+,S-,S+
19  d= 1  rank=  6  mult= 6  pre=1  char_supp= 12  obj=B+
20  d= 2  rank= 36  mult=18  pre=2  char_supp= 62  obj=B-,S-
21  d= 2  rank= 18  mult= 9  pre=2  char_supp= 62  obj=B-,S-
22  d= 2  rank= 36  mult=18  pre=2  char_supp= 32  obj=B+,V+
23  d= 3  rank=  6  mult= 2  pre=3  char_supp=133  obj=B-,V-,V+
24  d= 1  rank=  2  mult= 2  pre=1  char_supp= 86  obj=V+
25  d= 1  rank=  1  mult= 1  pre=1  char_supp= 44  obj=S-
26  d= 1  rank=  3  mult= 3  pre=1  char_supp= 44  obj=S-
27  d= 4  rank= 12  mult= 3  pre=4  char_supp=182  obj=B-,B+,S-,S+
28  d= 5  rank= 30  mult= 6  pre=3  char_supp=105  obj=B-,V-,V+
29  d= 4  rank= 72  mult=18  pre=3  char_supp= 88  obj=V+,S-,S+
30  d= 4  rank= 24  mult= 6  pre=3  char_supp= 75  obj=B+,V-,S+
31  d=10  rank=180  mult=18  pre=5  char_supp=180  obj=B-,B+,V+,S-,S+
32  d= 2  rank=  6  mult= 3  pre=2  char_supp=115  obj=V-,S+
33  d= 2  rank= 36  mult=18  pre=2  char_supp= 56  obj=B+,S+
34  d= 1  rank=  3  mult= 3  pre=1  char_supp= 38  obj=V+
35  d= 9  rank=216  mult=24  pre=5  char_supp=134  obj=B-,B+,V+,S-,S+
36  d=12  rank=216  mult=18  pre=6  char_supp=156  obj=B-,B+,V-,V+,S-,S+
37  d=11  rank=528  mult=48  pre=5  char_supp= 78  obj=B-,B+,V+,S-,S+
38  d= 8  rank=144  mult=18  pre=3  char_supp= 90  obj=V-,V+,S+
```

## Hashes

```text
drinfeld_full_A985_lift_sha256 = 32b6e7c865e15a17ec54448e02c1bf0163491387c03ee28e8734471f29be72fc
embedded_idempotent_matrix_sha256 = e9066713580845e187b29aaa41b148581e6c43266f993a010b3a192e4d41c8c7
character_table_sha256 = 3751bdba9b90c17c6f5658fe45d1d4d76d1692ed8a84ea5e0cc78338245cab34
```

Boundary: no modular `S,T` matrix is claimed; no twist/ribbon operator is present in the certified input. This is the full finite A985 lift of the Drinfeld/Grothendieck center, including full centrality and the irreducible character table over the verifier field.
