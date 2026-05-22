# Drinfeld Wedderburn trace certificate

Status: `DRINFELD_WEDDERBURN_TRACE_CERTIFIED`

This stage embeds the 39 Drinfeld/Grothendieck primitive idempotents into the `A_985` relation basis and computes the regular-trace and permutation-trace invariants.

```text
Drinfeld primitive idempotents:        39
full A985 relation basis dimension:    985
closed-loop dimension:                 297
```

## Wedderburn recovery

```text
regular traces are squares:             True
block dimensions by sector:
[10, 6, 4, 5, 4, 2, 2, 1, 3, 3, 1, 5, 4, 2, 5, 4, 3, 4, 6, 1, 2, 2, 2, 3, 1, 1, 1, 4, 5, 4, 4, 10, 2, 2, 1, 9, 12, 11, 8]

block dimension histogram:
{'1': 7, '2': 8, '3': 4, '4': 8, '5': 4, '6': 2, '8': 1, '9': 1, '10': 2, '11': 1, '12': 1}

sum d_i^2:                              985
known Wedderburn multiset matched:       True
```

## Dodecad-shell permutation decomposition

```text
permutation ranks by sector:
[360, 108, 72, 120, 72, 18, 18, 3, 9, 9, 1, 15, 16, 2, 10, 72, 18, 72, 6, 6, 36, 18, 36, 6, 2, 1, 3, 12, 30, 72, 24, 180, 6, 36, 3, 216, 216, 528, 144]

multiplicities by sector:
[36, 18, 18, 24, 18, 9, 9, 3, 3, 3, 1, 3, 4, 1, 2, 18, 6, 18, 1, 6, 18, 9, 18, 2, 2, 1, 3, 3, 6, 18, 6, 18, 3, 18, 3, 24, 18, 48, 18]

sum permutation ranks:                  2576
rank = d_i * multiplicity:              True
```

So the same 39 idempotents split the 2576-point dodecad shell into 39 isotypic ranks.

## Public diagonal shadows

```text
q42 diagonal shadow rank:                12
q42 active diagonal columns:             [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
q12 diagonal shadow rank:                6
q12 active diagonal columns:             [0, 1, 2, 3, 4, 5]
```

## First 16 sector profiles

```text
00  d=10  rank=360  mult=36  pre=5  obj=B-,V-,V+,S-,S+
01  d= 6  rank=108  mult=18  pre=5  obj=B-,V-,V+,S-,S+
02  d= 4  rank= 72  mult=18  pre=2  obj=V+,S+
03  d= 5  rank=120  mult=24  pre=3  obj=V+,S-,S+
04  d= 4  rank= 72  mult=18  pre=3  obj=B-,S-,S+
05  d= 2  rank= 18  mult= 9  pre=2  obj=V-,S+
06  d= 2  rank= 18  mult= 9  pre=2  obj=S-,S+
07  d= 1  rank=  3  mult= 3  pre=1  obj=B+
08  d= 3  rank=  9  mult= 3  pre=3  obj=B-,V+,S-
09  d= 3  rank=  9  mult= 3  pre=2  obj=V+,S+
10  d= 1  rank=  1  mult= 1  pre=1  obj=B+
11  d= 5  rank= 15  mult= 3  pre=4  obj=V-,V+,S-,S+
12  d= 4  rank= 16  mult= 4  pre=3  obj=B+,V-,V+
13  d= 2  rank=  2  mult= 1  pre=2  obj=V+,S+
14  d= 5  rank= 10  mult= 2  pre=3  obj=V-,V+,S+
15  d= 4  rank= 72  mult=18  pre=3  obj=B-,V-,S-
```

## Timed-out full sweep

The following fuller command crossed the timeout boundary and was not rerun:

```bash
cd /mnt/data/drinfeld_v15 && python compute_drinfeld_wedderburn_lift.py
```

That command attempts an additional full `A_985` centrality sweep. The trace certificate above relies on the already-certified v14 half-braiding centrality and idempotent algebra.

Hash:

```text
drinfield_wedderburn_trace_sha256 = b1bba040f897dc2e50a37d461acf84072a246c19d2222f6601fd6dfee0a62dbf
embedded_idempotent_matrix_sha256 = e9066713580845e187b29aaa41b148581e6c43266f993a010b3a192e4d41c8c7
```

Boundary: this is a Wedderburn/isotypic trace lift of the Drinfeld idempotents. It still does not claim modular `S,T` matrices.
