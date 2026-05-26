# Hamming--Gaussian Jensen Scalar Reduction

## Result

`HAMMING_GAUSSIAN_JENSEN_SCALAR_REDUCTION_PASS`

This pass reduces the global Golay/Gaussian MGF inequality to a single finite combinatorial lemma plus a one-dimensional scalar maximization.

Let

$$
W(r)=1+759r^8+2576r^{12}+759r^{16}+r^{24}.
$$

Assume the block-RMS domination lemma for the Golay weight shells:

$$
A_w(x)\le A_w(1)\left(rac1{24}\sum_i x_i^2ight)^{w/2},
\qquad w\in\{8,12,16,24\},\quad x_i\ge0.
$$

Then the exact MacWilliams/Fourier identity gives

$$
M_C(u)\le \prod_i\cosh(u_i)\,W\!\left(\sqrt{rac1{24}\sum_i	anh^2u_i}ight).
$$

The analytic Jensen step uses concavity of

$$
x\mapsto \log\cosh\sqrt x,
\qquad
x\mapsto 	anh^2\sqrt x.
$$

Thus for

$$
t=rac{\|u\|}{\sqrt{24}},
$$

one has

$$
\log M_C(u)
\le
24\log\cosh t+\log W(	anh t).
$$

Therefore the global constant is bounded by the scalar problem

$$
K^2=\sup_{t>0}
rac{2\left(24\log\cosh t+\log W(	anh t)ight)}{24t^2}.
$$

## Scalar optimum

$$
oxed{t^*=0.686080808690279}
$$

$$
oxed{K^2=1.444854859266432}
$$

$$
oxed{K=1.202021155914667}
$$

Derivative sanity at optimum:

```text
dF/dt   = 5.298e-08
d2F/dt2 = -5.548e+00
```

## Meaning

This closes the analytic part conditionally. The remaining residue is no longer a 24-variable analytic inequality; it is the finite Golay shell inequality

$$
A_w(x)\le A_w(1)\left(rac1{24}\sum_i x_i^2ight)^{w/2}.
$$

Once that block-RMS lemma is proved, the sharp codeword-sign constant follows globally.
