# Hamming/Gaussian Indicator Shell Domination Certificate

Status:

```text
HAMMING_GAUSSIAN_INDICATOR_SHELL_DOMINATION_CERTIFIED
```

## Scope

This exhaustively certifies the Boolean-indicator subcase of the Golay shell block-RMS domination lemma.
For every support \(T\subset\{1,\dots,24\}\) and every Golay shell \(w\in\{8,12,16,24\}\), it checks

\[
\#\{d\in G_{24}: \operatorname{wt}(d)=w,\ \operatorname{supp}(d)\subseteq T\}
\le
A_w(1)\left(rac{|T|}{24}ight)^{w/2}.
\]

All \(2^{24}=16777216\) supports are checked for each shell by subset zeta transform.

## Result

Global max ratio:

```text
1.000000000000000
```

Global min margin:

```text
0.000000000000000e+00
```

The max ratio equals 1 only at the full support cases/equality cases; every proper-support obstruction stays below the block-RMS envelope.

## Meaning

The remaining block-RMS lemma is no longer failing on any coordinate-support face of the nonnegative cone. Any counterexample must be genuinely non-Boolean: it must use nontrivial unequal positive weights, not merely concentration on a subset of coordinates.

## Remaining residue

This does not prove the arbitrary nonnegative real inequality. It closes the full support-indicator boundary of the cone and leaves the interior/tensor spectral bound.
