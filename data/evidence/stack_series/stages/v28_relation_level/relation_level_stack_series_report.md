# D20 A985 Relation-Level Stack Series v28

## Result

```text
D20_A985_RELATION_LEVEL_STACK_SERIES_CERTIFIED_RAW_TENSOR_MOTIVIC_COHA_OPEN
```

This gate keeps the raw `A985` relation/tensor data before the six-object collapse. It reads `data/raw/T_985.npz`, verifies the `985` relation classes and `1414965` nonzero tensor triples, and computes truncated symmetric-product stack series for relation-level budgets.

## Budgets

```text
Z_B(t,q)=prod_w (1 - t q^w)^(-m_B(w)), n <= 40, q <= 512
```

The budgets are tensor coefficient values, relation orbit sizes, left/right/output coefficient masses, and left/right/output support counts.

## Retest

The focus targets are:

```text
[39, 243, 455640, 534656]
```

No focus target appears as an exact coefficient in the raw relation-level budgets. The nearest rows are recorded in `relation_level_invariant_hits.csv`.

## Seam

This is not yet the full `985 x 985` relation-pair bilinear stack and not a motivic/sheafified CoHA. It is the certified raw relation/tensor symmetric-product gate.
