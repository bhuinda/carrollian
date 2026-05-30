# Krein Denominator Obstruction Source Boundary

Status: provisional.

This report records the next acceptance-ladder target from `docs/real.txt` without upgrading it to a certified Krein computation. The current checked input boundary contains the canonical A985 sector character table, but it does not yet contain a full `q_ij^k` Krein parameter tensor or idempotent Hadamard-product witness.

## Available Evidence

- canonical character sectors: `39`
- canonical relation columns: `985`
- character-table rows: `38415`
- blocking source surfaces still absent: `2`

## Target Half-Integral Rows

| i | j | k | expected | computed | verified |
|---:|---:|---:|---:|---:|---:|
| 5 | 5 | 2 | 135/2 | 0 | 0 |
| 5 | 6 | 2 | 135/2 | 0 | 0 |
| 6 | 5 | 2 | 135/2 | 0 | 0 |
| 6 | 6 | 2 | 135/2 | 0 | 0 |

The four rows above are the handoff target. Their expected denominator obstruction is not certified here because the full Krein parameter table has not been materialized.

## Clearance Candidates

| candidate | tested | passed | open |
|---|---:|---:|---:|
| double_E5_E6 | 0 | 0 | 1 |
| z2_graded_cover | 0 | 0 | 1 |
| spinor_state_lift | 0 | 0 | 1 |
| weak_fusion_category | 0 | 0 | 1 |
| module_category_realization | 0 | 0 | 1 |

## Closure Boundary

Certified here: the source boundary and missing-evidence seam for the Krein denominator task.

Not certified here: all Krein parameters, the four 135/2 rows, any denominator-clearing double cover, or any acceptance-ladder closure depending on those computations.

Next highest-yield item: compute the full Krein parameter table from the canonical A985 idempotent/eigenmatrix data, then rerun this report as a certified denominator obstruction or clearance theorem.
