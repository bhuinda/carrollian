# Hamming-Gaussian entropy log-Sobolev / SDPI route audit

## Status

`ENTROPY_LOGSOBOLEV_ROUTE_AUDIT_COMPLETE_WITH_OPEN_GLOBAL_SDPI`

Certificate hash:

```text
a96d9f56f281ec1c7b4070d600c0f242e11b9574846ed390304ec66bb32b9f54
```

## Exact local SDPI reduction

For a Golay shell block incidence matrix `B` with `m` blocks and block size `w`, the channel

```text
q on blocks -> p_q(i)=P_q(i in B)/w
```

has local entropy contraction coefficient at uniform controlled by the nontrivial spectrum of `B^T B`.

For perturbations around uniform,

```text
D(p_q || u_24) / D(q || u_B)
= (24/(m w^2)) * lambda_nontrivial(B^T B).
```

The target entropy contraction is

```text
D(q || u_B) >= (w/2) D(p_q || u_24),
```

equivalently local SDPI coefficient at most `2/w`.

## Local spectrum

| shell | blocks | local eta | target 2/w | margin |
|---:|---:|---:|---:|---:|
| 8 | 759 | 0.086956521739 | 0.250000000000 | 0.163043478261 |
| 12 | 2576 | 0.043478260870 | 0.166666666667 | 0.123188405797 |
| 16 | 759 | 0.021739130435 | 0.125000000000 | 0.103260869565 |


The local/Fisher-level inequality is strictly inside the target for every nontrivial shell tested.

## Entropy stress summary

| shell | rows | min Dq/Dp | target w/2 | margin | min gap |
|---:|---:|---:|---:|---:|---:|
| 12 | 320 | 11.330916878115 | 6.000000 | 5.330916878115e+00 | 1.166508516745e-01 |
| 16 | 320 | 16.356528946077 | 8.000000 | 8.356528946077e+00 | 1.075937989394e-01 |


No random or structured entropy stress test violated the target.

## What this closes

This pass converts the entropy route into a standard strong-data-processing / log-Sobolev problem for the block-to-coordinate incidence channel.

It proves the exact local/Fisher contraction margin and gives block-intersection data for a graph/SOS route.

## What remains open

The global SDPI is not proved:

```text
D(q || u_B) >= (w/2) D(p_q || u_24),  w=12,16.
```

This is the cleanest current residue. A proof likely needs a custom Golay association-scheme log-Sobolev or Veronese-constrained SOS certificate.
