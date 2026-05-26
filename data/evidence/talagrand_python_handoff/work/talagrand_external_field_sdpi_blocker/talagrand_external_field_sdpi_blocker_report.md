# Talagrand External-Field SDPI Route Blocker

## Status

`TALAGRAND_GLOBAL_EXTERNAL_FIELD_SDPI_ROUTE_BLOCKED`

Certificate hash:

```text
8d45f9757eb2151c9c8961e00f0bed5fe4f85ab20f3c7eaa1842730f1ed4a4b3
```

## What this found

The tempting route was:

```text
prove local chi-square / spectral SDPI <= 2/w under every external field
then upgrade to KL-SDPI.
```

That route is too strong.

Sampled external fields violate the target local coefficient.

| shell | target 2/w | max sampled local eta | eta-violating samples | ratio at max eta |
|---:|---:|---:|---:|---:|
| 12 | 0.166666666667 | 0.431870871939 | 191 | 1.001e-53 |
| 16 | 0.125000000000 | 0.330439150601 | 196 | 9.686e-74 |


## Meaning

This does **not** disprove Talagrand.

It says the proof cannot be the overly strong statement:

```text
all external fields have SDPI coefficient <= 2/w.
```

The high-eta points are low-ratio regions, so they are irrelevant to the maximum if a KKT/barrier theorem is proved.

## Correct remaining route

The proof must be a maximum principle:

```text
near the ratio barrier, the KKT/Hessian mechanism forces equality;
away from the barrier, high eta is harmless.
```

So the remaining theorem is sharper:

```text
No positive-ratio non-equal KKT maximizer exists.
```
