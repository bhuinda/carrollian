# Hamming/Gaussian Shell Structure Audit

Status:

```text
HAMMING_GAUSSIAN_SHELL_STRUCTURE_AUDIT_COMPLETE
```

Certificate hash:

```text
ef343ed15d2fefcccbcc732eedb26982da26f870e99392115fb93cf3ddf0ce65
```

## Purpose

This pass attacks the remaining Golay shell domination residue from three directions:

1. strong-Rayleigh / Lorentzian route;
2. structured two-level split directions;
3. KKT fixed-point formulation for positive interior extrema.

The source remains the finite chain `H8^3 -> G24` with root cancellation `42 -> 18 -> 6 -> 0`.

## Result 1: strong-Rayleigh route is rejected

The shell generating polynomials are not strongly Rayleigh on the sampled certificates. Negative Rayleigh differences were found:

| shell | min sampled Rayleigh difference |
|---:|---:|
| 8 | -6.853937e+14 |
| 12 | -7.048874e+19 |
| 16 | -7.586795e+27 |


Thus standard strong-Rayleigh / real-stability / Lorentzian negative-dependence machinery cannot be used directly.

## Result 2: structured two-level directions still do not break domination

The audit optimized directions with one value on a support and one value on its complement, across prefix supports, codeword supports, complements, and random supports.

| shell | best tested ratio | support label | support size |
|---:|---:|---|---:|
| 8 | 1.0000000000000011 | prefix_24 | 24 |
| 12 | 1.0000000000000011 | prefix_17 | 17 |
| 16 | 1.0000000000000018 | prefix_24 | 24 |


No tested two-level split exceeded ratio `1 + 1e-8`.

## Result 3: exact KKT form

For an interior positive maximizer of shell `w`, the Gibbs inclusion probabilities must satisfy

```text
P(i in B under product-biased shell measure) = (w/24) x_i^2.
```

Damped KKT fixed-point iteration returns the equal point or boundary/non-maximal attractors in the stress tests.

## Current residue

The remaining proof cannot be a generic symmetric-polynomial, pairwise smoothing, or strong-Rayleigh argument. The target is now a custom certificate:

```text
Veronese-constrained Krawtchouk/SOS certificate for w=12 and w=16 shell domination.
```
