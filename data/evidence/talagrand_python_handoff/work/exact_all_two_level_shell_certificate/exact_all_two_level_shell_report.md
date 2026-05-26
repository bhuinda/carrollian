# Exact All Two-Level Shell Gap Certificate

## Status

`EXACT_ALL_TWO_LEVEL_SHELL_GAP_FACTOR_CERTIFIED`

Certificate hash:

```text
e2bbe5c4210997b7eec280287124a14eb6e7d06b0df21cd182d8f5bdb8d8c821
```

## What this proves

For every shell

```text
w in {8,12,16,24}
```

and every two-level threshold support size

```text
k=0,...,24,
```

the exact shell gap

```text
Gap_{w,k}(z)
=
A_w(1)(k z^2+24-k)^(w/2)
-
24^(w/2) sum_j N_j z^j
```

satisfies

```text
Gap_{w,k}(z)=(z-1)^2 Q_{w,k}(z)
```

with

```text
Q_{w,k}(z) in Z_{>=0}[z].
```

Therefore

```text
Gap_{w,k}(z) >= 0 for all z >= 0.
```

## Certified rows

| shell | support sizes certified | failures |
|---:|---:|---:|
| 8 | 0..24 | 0 |
| 12 | 0..24 | 0 |
| 16 | 0..24 | 0 |
| 24 | 0..24 | 0 |


## Meaning

This is an exact certificate for **all two-level threshold directions**, not only high-support cases.

The remaining theorem debt is now strictly multilevel:

```text
arbitrary multilevel KKT/barrier behavior.
```

Any final proof can now use this as the threshold-compression base case.
