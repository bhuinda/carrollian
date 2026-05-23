# A236 / Jabberwock computation Python bundle

This bundle collects the Python files needed to reproduce the A236 thread from the raw
`jabberwock.npz` tensor and the `d20.json` certificate.

## Input contract

Place the raw inputs at:

```text
data/jabberwock.npz
 data/d20.json
```

or pass explicit paths with `--npz` and `--d20`.

`jabberwock.npz` must contain:

```text
triples : int array, shape (1414965, 4), columns (alpha, beta, gamma, p)
M       : int array, shape (6, 6), object pair matrix
reps    : int array, shape (985, 5), orbital metadata
```

## Quick run

```bash
python run_all.py --npz /path/to/jabberwock.npz --d20 /path/to/d20.json --out out
```

The runner executes:

1. inspect raw tensor;
2. reconstruct q42/q12 maps and quotient tensors;
3. compute small quotient centers;
4. audit the q236 orbital partition candidates;
5. build the certified A236 K0/fusion layer;
6. realize A236 restricted modules over A42;
7. test ordinary full A985 extension obstruction from cached/known restriction matrices;
8. build the A985 -> A236 profunctor correspondence;
9. build the public bimodule/intertwiner lift over A42.

## Important typing conclusion

The scripts are organized around the corrected result:

```text
A236 is not a 985 -> 236 orbital partition and not an ordinary intermediate
full A985 module category.  It is a semisimple profunctor/fusion interface
between A985 and the public A42/A12 readout.
```

The generated reports are deliberately plain JSON/CSV so they can be compared by hash or ingested by a verifier.
