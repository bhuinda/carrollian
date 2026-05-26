# Multilevel KKT Obstruction System

## Status

`MULTILEVEL_KKT_OBSTRUCTION_SYSTEM_FORMALIZED_NOT_CLOSED`

Certificate hash:

```text
f4bf718c1a1b94269d17b65e95748f5557323994098832e1ee4295b23b897e6a
```

## Exact remaining lemma

The multilevel contact lemma is:

```text
F_w(theta)=0, theta0>=theta1 => partial_0 F_w - partial_1 F_w <= 0.
```

Let

```text
v=e0-e1,
g=grad F_w(theta),
H=Hessian F_w(theta).
```

Then the pair derivative is:

```text
dF = v·g.
```

## KKT obstruction

If the contact lemma fails, then there must exist a contact maximizer with:

```text
F=0,
sum theta_i=0,
v·theta >= 0,
dF > 0.
```

At such a maximizer, the exact KKT equation is:

```text
H v = lambda g + nu v,
nu >= 0,
nu(v·theta)=0.
```

Interior ordered branch:

```text
theta0>theta1 => nu=0 => H v = lambda g.
```

Boundary ordered branch:

```text
theta0=theta1 => H v = lambda g + nu v.
```

## Meaning

This is the true multilevel generalization. It does not assume pair-stabilized rest coordinates.

The remaining proof is now an exact exclusion problem:

```text
No solution of the KKT obstruction system with dF>0.
```

The previous weighted-asymmetry numerical audit found no such solution and collapsed to the equal point, but an exact Terwilliger/Krawtchouk/SOS certificate is still needed.
