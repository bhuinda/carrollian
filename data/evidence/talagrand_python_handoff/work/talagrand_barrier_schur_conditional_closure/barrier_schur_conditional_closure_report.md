# Barrier Schur Conditional Closure

## Status

`TALAGRAND_CONDITIONAL_CLOSURE_FROM_BARRIER_SCHUR_FORMALIZED`

## What this does

This pass proves the exact implication:

```text
Barrier Schur Compression Lemma
=> global shell-domination theorem.
```

It does not prove the Barrier Schur Compression Lemma itself.

## Key identity

For centered theta and g = grad F_w(theta),

```text
24 <theta,g> = sum_{i<j} (theta_i-theta_j)(g_i-g_j).
```

So if the pairwise Schur compression inequality holds on the barrier F_w >= 0, then

```text
<theta,g> <= 0.
```

## Radial barrier argument

Let

```text
phi(s)=F_w((1-s)theta).
```

Whenever phi(s) >= 0,

```text
phi'(s) = -<theta, grad F_w((1-s)theta)> >= 0.
```

Since phi(1)=F_w(0)=0, phi(0)>0 is impossible. Therefore

```text
F_w(theta)<=0
```

globally.

## Remaining theorem

The single remaining proof target is exactly:

```text
F_w(theta)>=0
=> (theta_i-theta_j)(grad_i F_w-grad_j F_w)<=0 for all i,j.
```
