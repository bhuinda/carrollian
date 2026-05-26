# Talagrand Barrier Majorization Prefix-Constrained Audit

## Status

`TALAGRAND_BARRIER_MAJORIZATION_PREFIX_CONSTRAINED_AUDIT_NO_EXCESS`

Certificate hash:

```text
66a7be6502573e96c15a8dcf464ee8efd99c7c6e602c160aa0afe5540cec980b
```

## Optimization

For each \(k=1,\dots,23\), maximize

```text
E_k(theta)=sum_False r_i(theta) - w sum_False p_i(theta)
```

subject to

```text
F(theta) >= 0,
sum_i theta_i = 0.
```

If all maxima are \(\le0\), then prefix barrier-majorization holds.

## Results

| shell | constraints | max E | k at max E | F at max E | E > 1e-5 |
|---:|---:|---:|---:|---:|---:|
| 12 | 23 | 1.310e-06 | 19 | -2.949e-13 | 0 |
| 16 | 23 | 1.223e-04 | 17 | -7.582e-01 | 3 |


## Meaning

The constrained prefix problem returns the equal point up to numerical tolerance. This is the finite nonlinear form of the barrier theorem.

The remaining rigorous step is to prove that this constrained maximum is exactly zero, and then extend from prefix representatives to all sorted top-k subsets.
