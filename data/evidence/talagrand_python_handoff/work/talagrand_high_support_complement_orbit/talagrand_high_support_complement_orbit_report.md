# Talagrand High-Support Complement Orbit and Local-Max Certificate

## Status

`TALAGRAND_HIGH_SUPPORT_COMPLEMENT_ORBIT_AND_LOCAL_MAX_CERTIFIED`

Certificate hash:

```text
f349c697d50d132f65213110eabdeea7edd236dc71e8ac9b8f93526056cc7904
```

## What this certifies

The AM-GM sieve left high-support boundary faces. This pass checks their complement-size structure.

For each remaining complement size, it verifies:

```text
number of contained shell blocks is constant over all complements of that size
equal-on-support ratio is <= 1
equal-on-support has negative tangent Hessian
```

## Summary

| shell | complement sizes | complement counts constant | max proper boundary ratio | max tangent Hessian |
|---:|---|---|---:|---:|
| 12 | 0 1 2 3 4 5 | True | 6.4546164207518608e-01 | -7.3913043478260698e-01 |
| 16 | 0 1 2 | True | 4.6853926381261146e-01 | -1.1014492753623173e+00 |


## Meaning

The high-support boundary is no longer a large uncontrolled family. It reduces cleanly by complement size, and every proper high-support boundary face has an equal-on-support ratio below one.

The remaining gap is global: prove equal-on-support is the global maximizer on those high-support faces, not only a strict local maximizer supported by KKT stress.
