# Hamming--Gaussian Two-Level Direction Probe

## Result

`HAMMING_GAUSSIAN_TWO_LEVEL_PROBE_COMPLETE`

This tests the next reduction class after the codeword-sign local maximum: directions taking two coordinate values, `a` on a subset `S` and `b` on the complement. It covers all prefix support sizes, representative Golay codeword supports of weights 8, 12, 16, 24, and random medium supports.

## Candidate bound

```text
K^2_candidate = 1.444854859266432
K_candidate   = 1.202021155914667
```

## Best two-level direction found

```json
{
  "label": "prefix_k23",
  "k": 23,
  "F": 1.4448548592664323,
  "K": 1.202021155914667,
  "t_norm": 3.3610958544968006,
  "theta": 0.20556892690973716,
  "a": 0.6860808189499489,
  "b": 0.6860808043531266,
  "excess_over_candidate": 2.220446049250313e-16,
  "split_profile_size": 8
}
```

No tested two-level direction exceeded the codeword-sign candidate:

```text
True
```

## Top rows

```json
[
  {
    "label": "prefix_k23",
    "k": 23,
    "F": 1.4448548592664323,
    "K": 1.202021155914667,
    "t_norm": 3.3610958544968006,
    "theta": 0.20556892690973716,
    "a": 0.6860808189499489,
    "b": 0.6860808043531266,
    "excess_over_candidate": 2.220446049250313e-16,
    "split_profile_size": 8
  },
  {
    "label": "prefix_k18",
    "k": 18,
    "F": 1.444854859266432,
    "K": 1.202021155914667,
    "t_norm": 3.361095854473185,
    "theta": 0.5235987653781232,
    "a": 0.6860808223852303,
    "b": 0.6860808061920184,
    "excess_over_candidate": 0.0,
    "split_profile_size": 21
  },
  {
    "label": "random_k6_0",
    "k": 6,
    "F": 1.444854859266432,
    "K": 1.202021155914667,
    "t_norm": 3.361095854473185,
    "theta": 1.0471975423817348,
    "a": 0.6860808288118655,
    "b": 0.6860808148452813,
    "excess_over_candidate": 0.0,
    "split_profile_size": 21
  },
  {
    "label": "random_k6_1",
    "k": 6,
    "F": 1.444854859266432,
    "K": 1.202021155914667,
    "t_norm": 3.361095854473185,
    "theta": 1.0471975423817348,
    "a": 0.6860808288118655,
    "b": 0.6860808148452813,
    "excess_over_candidate": 0.0,
    "split_profile_size": 21
  },
  {
    "label": "prefix_k6",
    "k": 6,
    "F": 1.4448548592664319,
    "K": 1.202021155914667,
    "t_norm": 3.3610958544993927,
    "theta": 1.0471975423817395,
    "a": 0.6860808288172097,
    "b": 0.6860808148506329,
    "excess_over_candidate": -2.220446049250313e-16,
    "split_profile_size": 21
  }
]
```

## Boundary

This is a structured finite diagnostic, not a proof over all subset orbits or arbitrary directions.
