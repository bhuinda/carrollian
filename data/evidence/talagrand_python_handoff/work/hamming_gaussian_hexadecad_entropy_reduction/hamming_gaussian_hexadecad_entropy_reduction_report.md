# Hexadecad entropy complement reduction

## Status

`HEXADECAD_ENTROPY_COMPLEMENT_REDUCTION_AUDITED_SCALAR_RESIDUE_OPEN`

Certificate hash:

```text
9978640f863332c3a5e668f8ffe964f7559a1df111a58d481814a200be115b85
```

## Main reduction

The shell `w=16` is the complement of the octad shell `w=8`:

```text
B_16 = [24] \ O_8.
```

For a law on octads with coordinate marginal

```text
p_8(i)=P(i in O)/8,
```

the corresponding hexadecad marginal is

```text
p_16(i) = (1 - 8 p_8(i))/16.
```

Thus the `w=16` entropy contraction follows from the octad shell plus the scalar complement inequality

```text
D(Tp || u_24) <= (1/2) D(p || u_24),
T(p)_i=(1-8p_i)/16,
0 <= p_i <= 1/8,
sum p_i = 1.
```

## Audit summary

| audit | value |
|---|---:|
| two-value minimum gap | `-3.537489056842e-02` |
| two-value minimizing k | `4` |
| two-value arg a | `1.250000000000e-01` |
| two-value arg b | `2.500000000000e-02` |
| random stress minimum gap | `-2.873021948123e-02` |
| random stress best family | `two_value_random` |

No violation was found.

## Meaning

This does not fully prove `w=16`, but it sharply reduces it:

```text
w=16 shell entropy contraction
<= octad entropy contraction + scalar complement entropy inequality.
```

So the genuinely hard Golay-shell residue is now `w=12`, plus this scalar entropy inequality needed to make the `w=16` reduction formal.

## Remaining residue

1. Prove the scalar complement inequality.
2. Prove the `w=12` dodecad entropy contraction.
