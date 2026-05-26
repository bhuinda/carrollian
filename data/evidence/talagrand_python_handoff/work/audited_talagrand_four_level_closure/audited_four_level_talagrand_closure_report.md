# Audited Four-Level Talagrand Closure

## Status

`AUDITED_TALAGRAND_FOUR_LEVEL_CLOSURE_PASS_REST_LE_6`

## Scope

This closes the Talagrand obstruction only for the audited four-level scenic profile band:

```text
rest_size <= 6
w = 12, 16
```

It does not close the full arbitrary-vector theorem.

## The finite proof ladder

1. Three-level positivity is exact-rational certified.
2. The four-level scenic profiles form a chain complex:

```text
C3 -> C2 -> C1
d2*d3 = 0 mod 2
```

3. Same-boundary horn cycles live in `ker(d3)`.
4. Every horn residue factors through the four-variable Vandermonde.
5. Ordinary color-symmetric shell readout kills the Vandermonde horn sector.
6. The non-oriented H2 face-residue sector has an explicit basis.
7. `Act` sends every audited H2 image into the already-certified three-level nonnegative cone.

## Consequence

For the audited band:

```text
four-level obstruction = symmetric horn sector + Act(H2) sector
```

and both are handled:

```text
symmetric horn sector = 0
Act(H2) >= 0
```

So the audited four-level Talagrand obstruction is closed after actor readout.

## Remaining global obligation

The global proof still needs one of:

```text
1. full four-level Act/Vandermonde/H2 certificate,
2. level-reduction theorem,
3. global Veronese/Krawtchouk SOS certificate.
```
