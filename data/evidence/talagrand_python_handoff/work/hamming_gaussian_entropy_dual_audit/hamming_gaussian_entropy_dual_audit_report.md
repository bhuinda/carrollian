# Hamming--Gaussian entropy dual audit

## Result

`HAMMING_GAUSSIAN_ENTROPY_DUAL_AUDIT_COMPLETE`

Certificate hash:

```text
b44270de2467f6a903c405e3e98ef7b965952300c3a8fb0c239fa7d5e8599dd3
```

## Exact reduction

The remaining Golay shell-domination lemma

```math
A_w(x) <= A_w(1) ((1/24) sum_i x_i^2)^{w/2},  x_i >= 0,
```

is equivalent, by log-sum-exp duality, to the entropy contraction inequality

```math
D(q || u_{B_w}) >= (w/2) D(p_q || u_24),
```

where `q` is any probability distribution on the Golay shell blocks of weight `w`, and

```math
p_q(i) = (1/w) P_q(i in B).
```

This is a cleaner target than the raw 24-variable polynomial inequality.

## Numerical stress summary

| shell | blocks | min structured gap | min optimized gap | optimized start | p-CV at optimum |
|---:|---:|---:|---:|---|---:|
| 8 | 759 | -5.366077952355e-15 | -5.366077952355e-15 | zero_uniform | 1.221e-15 |
| 12 | 2576 | 5.406786129924e-14 | 5.406786129924e-14 | zero_uniform | 1.444e-15 |
| 16 | 759 | 2.146431180942e-15 | 2.146431180942e-15 | zero_uniform | 6.850e-16 |
| 24 | 1 | 0.000000000000e+00 | 0.000000000000e+00 | trivial_w24 | 0.000e+00 |

## Meaning

No negative entropy gaps were found in structured distributions or direct softmax-parameter optimization over shell-block distributions for the open shells.

This does not close the proof. It retypes the residue as a finite entropy contraction / log-Sobolev problem on the Golay shell hypergraph.

## Remaining residue

```math
D(q || u_{B_w}) >= (w/2) D(p_q || u_24),  w=12,16.
```

A proof should likely use the Golay association scheme, Krawtchouk data, or an SOS/log-Sobolev certificate.
