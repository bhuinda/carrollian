# Tube-kernel descent audit for Drinfeld modular completion

status: `TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED`
sha256: `935c83cc641a329bb4d6890d6ea52f10623d6a760c9b1c29d1fd8af6c380a35a`

## Exact descent through the 44,224-dimensional projection kernel

| candidate | formula | descends | defect support | HB39 stable | primitive support | diagonal |
|---|---|---:|---:|---:|---:|---:|
| `identity` | `(a,b)` | `True` | `0` | `True` | `39` | `True` |
| `swap` | `(b,a)` | `False` | `3070672` | `False` | `136` | `False` |
| `dual_swap` | `(b^vee,a^vee)` | `True` | `0` | `True` | `39` | `True` |
| `dual_each` | `(a^vee,b^vee)` | `False` | `3070672` | `False` | `152` | `False` |

## Interpretation

The exact test is `P Φ = R P`, equivalently `Φ(ker P) ⊂ ker P`. This stage explicitly uses the full projection kernel rather than only the 297-dimensional quotient.

Exact descending operations: `['identity', 'dual_swap']`.
Kernel-obstructed operations: `['swap', 'dual_each']`.

The annular pair-swap and dual-each pair rotation do not define section-independent braid/Hopf-link operators. The only surviving operations are identity and dual-swap/transpose, and their primitive Drinfeld-sector action is diagonal/trivial.
