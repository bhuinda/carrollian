# Hamming/Golay Gaussian Maclaurin Domination Reduction

Status:

```text
HAMMING_GAUSSIAN_MACLAURIN_DOMINATION_REDUCTION_COMPLETE
```

## Exact endpoint data

The endpoint code is the extended binary Golay code with weight enumerator

\[
1+759y^8+2576y^{12}+759y^{16}+y^{24}.
\]

## Candidate block domination lemma

For nonnegative \(x\in\mathbb R^{24}\), define

\[
A_w(x)=\sum_{d\in G_{24},\,\operatorname{wt}(d)=w}\prod_{i\in\operatorname{supp}(d)}x_i.
\]

The tested domination lemma is

\[
A_w(x)\le A_w(1)\left(\frac124\sum_i x_i^2\right)^{w/2},
\qquad w\in\{8,12,16,24\}.
\]

Equality holds at \(x=(1,\ldots,1)\). Multistart optimization returned ratio 1.0 for every shell.

## Conditional analytic consequence

Using MacWilliams/Fourier,

\[
M_C(u)=\prod_i\cosh(u_i)\sum_{d\in C}\prod_{i\in\operatorname{supp}(d)}\tanh(u_i).
\]

If the block domination lemma holds, then with \(s=\|u\|_2\) and \(r\le\min(1,s/\sqrt{24})\),

\[
M_C(u)\le \exp(s^2/2)\bigl(1+759r^8+2576r^{12}+759r^{16}+r^{24}\bigr).
\]

This gives the certified conditional safe upper bound

\[
K^2\le 1.757518644157811,\qquad K\le 1.325714390114934.
\]

The current sharp candidate from the codeword-sign direction remains

\[
K^2=1.444854859266432.
\]

## Remaining residue

This package does not prove the block domination lemma; it reduces the global inequality to that explicit combinatorial domination statement and stress-tests it. The next target is a theorem-grade proof of that lemma by association-scheme/Krawtchouk methods or a sharper direct domination certificate.
