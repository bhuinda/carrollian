# Talagrand Barrier Sonification Scanner

## Status

`TALAGRAND_BARRIER_SONIFICATION_SCANNER_BUILT`

Certificate hash:

```text
b0ae9d9948a5a6dc572536770a3edad8d004464cf908fb202289bf9e3cb29cfc
```

## Purpose

This package generalizes sonification into a proof scanner.

Each radial trace is encoded as:

```text
alpha,t -> (F, dF, Emax, kmax, Lambda_hc)
```

and rendered as CSV plus WAV.

## Channel map

| invariant | role |
|---|---|
| `F`, `ratio=exp(F)` | pitch / barrier altitude |
| `dF` | radial pull |
| `Emax` | roughness / dissonance |
| `kmax` | cumulative-excess location |
| `Lambda_hc` | silent channel, because `Lambda_hc in ker(Act)` |

## Trace summary

| trace | shell | max ratio | max E | F at max E | danger rows |
|---|---:|---:|---:|---:|---:|
| w12_random_safe | 12 | 1.000e+00 | 3.250e-14 | -2.111e+01 | 0 |
| w16_prefix16_low_barrier_dissonance | 16 | 1.000e+00 | 1.415e-02 | -3.399e+00 | 0 |
| w16_random_safe | 16 | 1.000e+00 | 4.584e-14 | -4.543e+01 | 0 |


## Interpretation

The scanner separates harmless dissonance from dangerous dissonance:

```text
dissonance below barrier = harmless
dissonance at barrier    = proof obstruction
```

The generated traces contain no danger rows. The `w16_prefix16_low_barrier_dissonance` WAV makes the key phenomenon explicit: majorization dissonance occurs, but far below the barrier.
