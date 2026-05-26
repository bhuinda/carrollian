# Weighted Asymmetry Contact Audit

## Status

`WEIGHTED_ASYMMETRY_CONTACT_AUDIT_NO_VALID_OUTWARD_DERIVATIVE`

Certificate hash:

```text
a10f870ed9e3a68f8394a5a158a3884a66c7538af1c850cbd92fa9850d632e72
```

## Target

The exact multilevel remaining lemma is:

```text
F(theta)=0, theta0>=theta1 => partial_0F-partial_1F <= 0.
```

In the four-coefficient normal form this is:

```text
24^h(a C10-b C01) <= m w S^(h-1)(a^2-b^2)
```

on the contact surface.

## Audit

This pass maximizes the outward derivative using analytic gradients:

```text
objective: maximize partial_0F-partial_1F
constraints: F=0, sum(theta)=0, theta0-theta1>=0.
```

## Results

| shell | starts | valid contact rows | positive outward rows | max valid D(F) |
|---:|---:|---:|---:|---:|
| 12 | 37 | 24 | 0 | 1.0547118733938987e-15 |
| 16 | 37 | 23 | 0 | 9.992007221626409e-16 |


## Meaning

No valid contact point with positive outward pair derivative was found.

The exact remaining proof is still the weighted asymmetry lemma. This audit confirms that the multilevel obstruction is localized correctly, but does not close it.
