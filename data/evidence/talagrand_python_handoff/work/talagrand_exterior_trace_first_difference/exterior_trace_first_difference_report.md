# Exterior Trace First-Difference Normal Form

## Status

`EXTERIOR_TRACE_FIRST_DIFFERENCE_NORMAL_FORM_CERTIFIED`

Certificate hash:

```text
7bd07ce43aac93bdc28a1274effec5a4040ac32079d8b2921d73bb3645054378
```

## What this proves

For the pairwise Schur obstruction polynomial \(P_w\), the correct exact factor is the first exterior pair trace:

```text
P_w = (x_0 - x_1) Q_w.
```

This is checked independently for every fixed tuple of the other 22 exponents.

## Certified summary

| shell | raw P terms | rest groups | remainder terms | Q terms | Q sign split |
|---:|---:|---:|---:|---:|---:|
| 12 | 69440 | 32144 | 0 | 34720 | 17360+ / 17360- |
| 16 | 18524 | 8503 | 0 | 9262 | 4631+ / 4631- |


## Meaning

The earlier square-factor route was false. This certificate gives the corrected normal form:

```text
one exterior pair trace survives.
```

So the remaining ordered-branch proof is:

```text
x_0 >= x_1,  B_w >= 0  =>  Q_w >= 0.
```

Equivalently:

```text
B_w >= 0 => P_w >= 0.
```

The death-rate / exterior-annihilation law helps by identifying the trace normal form, not by supplying a probability proof.
