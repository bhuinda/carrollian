# Hamming–Gaussian KKT covariance reduction audit

## Result

`HAMMING_GAUSSIAN_KKT_COVARIANCE_REDUCTION_COMPLETE`

Certificate hash:

```text
c2592c274dd36d7ca89433b8a96f6a5d87eeb3ac2acf540a9fa83686162d4f3c
```

## Target

The remaining shell-domination lemma is

```math
A_w(x) \le A_w(1)\left(rac1{24}\sum_i x_i^2ight)^{w/2},\qquad x_i\ge0,
```

for the two open extended-Golay shells `w=12,16`.

In log coordinates `x_i=e^{z_i}`, the Hessian of the log-ratio is exactly

```math
\operatorname{Cov}_z(1_{i\in B},1_{j\in B})
-2w\left(q_i\delta_{ij}-q_iq_jight),
\qquad q_i=rac{e^{2z_i}}{\sum_j e^{2z_j}}.
```

At an interior KKT point,

```math
\mathbb P_z(i\in B)=wq_i.
```

Thus the residue can be retyped as a covariance-domination/uniqueness problem for product-biased Golay shell measures.

## Equal point

| shell | ratio | grad norm | max tangent Hessian eigenvalue |
|---:|---:|---:|---:|
| 12 | 1.0000000000000000 | 2.197e-14 | 0.000000000000 |
| 16 | 1.0000000000000000 | 2.092e-15 | 0.000000000000 |


## Multistart KKT audit

Starts tested per shell: `82`.

| shell | best ratio | best gradient norm | best max Hessian eigenvalue | coefficient CV |
|---:|---:|---:|---:|---:|
| 12 | 1.0000000000000027 | 1.760e-08 | 0.000000000000 | 4.860e-09 |
| 16 | 1.0000000000000013 | 6.586e-09 | 0.000000000000 | 1.221e-09 |


No multistart final point exceeded ratio `1` beyond floating tolerance. The best points return to the all-equal orbit.

## Route status

This pass does not prove the lemma. It gives the next exact proof target:

```math
\operatorname{Cov}_z(I_B)\preceq 2w(\operatorname{diag}q-qq^T)
```

at every positive KKT point, followed by uniqueness of the positive KKT fixed point.

Equivalently, the remaining proof is a Veronese-constrained Krawtchouk/SOS certificate for the `w=12,16` shell measures.
