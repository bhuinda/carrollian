# Hamming Gaussian Full Subgaussian Probe

## Result

`HAMMING_GAUSSIAN_FULL_SUBGAUSSIAN_PROBE_COMPLETE`

This continues the Hamming/Golay -> Gaussian bridge beyond the already proved sparse `<8` regime.

## Theorem-grade part

Because the Golay endpoint has dual distance 8, every coordinate projection of size `<8` is uniform. Therefore every real sparse projection supported on fewer than eight coordinates is exactly an independent Rademacher linear form:

```text
sum_{i in S} a_i (-1)^{c_i}  ==_law  sum_{i in S} a_i eps_i,   |S|<8.
```

This is the completed finite theorem layer.

## New probe beyond the sparse theorem

For support size 8 and above, Golay constraints reappear. The cleanest exact direction is a full sign direction from a Golay codeword `d`:

```text
<sign(d), Y(c)> = 24 - 2 wt(c+d).
```

Since `c+d` is again uniform in `G24`, the distribution is determined exactly by the Golay weight enumerator:

```text
{"-24": 1, "-8": 759, "0": 2576, "8": 759, "24": 1}
```

The one-dimensional subgaussian proxy constant required by this direction is approximately:

```text
K^2 = 1.444849055442
K   = 1.202018741718
lambda* = 0.684636871508
```

The octad even-parity equal-coefficient probe gives:

```text
K^2 = 0.999983333779
K   = 0.999991666855
lambda* = 0.010000000000
```

Best structured probe:

```json
{
  "name": "equal_first_24",
  "type": "equal_subset",
  "support": 24,
  "K2": 1.4448490554420184,
  "K": 1.2020187417182888,
  "lambda": 0.6846368715083798,
  "log_mgf": 8.126888356023315
}
```

Best random probe among 400 directions:

```json
{
  "sample": 21,
  "K": 1.0109254066835094,
  "K2": 1.0219701778782186,
  "lambda": 0.7448101265822785,
  "support": 24,
  "a_sha256": "ea160cf27fa71e8819d0af52aa9b8bb7366498388a3b9047479bfba88c25171a"
}
```

## Interpretation

The root-killing chain eliminates the extra Hamming/Golay obstruction below the Golay distance threshold. At and above weight 8, structure is visible again; it is no longer a defect of the Hamming source, but the genuine Golay code law.

The next exact target is to prove or disprove that the full Golay sign vector has sharp subgaussian proxy constant achieved by a codeword sign direction.
