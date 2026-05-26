# Talagrand Radial Barrier Route

## Status

`TALAGRAND_RADIAL_BARRIER_ROUTE_ISOLATED`

Certificate hash:

```text
7abe921afd387f4907a3d879e2455b2058922df379cef4aee770d86f48bc4951
```

## Critical correction

Global radial majorization is **too strong**.

It holds in the sampled `w=12` grid, but fails in sampled `w=16` low-ratio regions.

The first visible failure is the `prefix_16` direction around `t≈6.5`:

```text
F ≈ -3.399
ratio ≈ 0.0337
```

So this is nowhere near the Talagrand barrier.

## Failure summary

| shell | violation rows | max F among violations | max ratio among violations | max derivative |
|---:|---:|---:|---:|---:|
| 12 | 0 | None | None | 1.813e-15 |
| 16 | 15 | -3.3882809162923166 | 0.03376667477415548 | 6.132e-03 |


## Breakthrough target

The correct lemma is not global majorization.

It is **barrier majorization**:

```text
If F_alpha(t) >= 0, then r_t is majorized by w p_t.
```

That is enough. At a first crossing above zero, one has `F=0` and would need `F'>0`; barrier majorization forces `F'<=0`, contradiction.

## Meaning

The proof is no longer searching blindly for KKT uniqueness. It has a precise barrier formulation:

```text
majorization may fail deep below the barrier,
but must hold at the barrier.
```

Proving that finishes the shell-domination theorem.
