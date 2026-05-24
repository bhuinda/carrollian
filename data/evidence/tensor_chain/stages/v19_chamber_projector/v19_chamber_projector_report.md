# v19 chamber-projector test for $R_\Omega$

## Main result

The constructed signed-Fano action from v18 gives an exact carrier. In that carrier, the active chamber is the two-plane

\[
\langle u_0,u_V\rangle,
\qquad
u_0=(B+V+S)/\sqrt3,
\qquad
u_V=(B-2V+S)/\sqrt6.
\]

The excluded line is

\[
u_{BS}=(B-S)/\sqrt2.
\]

So the mechanism is not a \(B\) versus \(S\) split. It is the \((B+S)/V\) chamber.

## Energy and ablation

- active chamber energy inside \(A_6\): `0.993553`
- pair projection energy inside \(A_6\): `0.993553`
- non-pair residual inside \(A_6\): `0.006447`
- \(W(D_6)\)-scalar invariant energy inside \(A_6\): `0.165271`
- active chamber share of the six-channel reconstruction: `1.000000`

The full \(R_\Omega\) e-lock is still a global \(16\times16\) question. v19 certifies the exact chamber projector on the constructed six-channel/foam carrier.

## Stabilizer

- signed-Fano active-plane stabilizer: `32` of `768`; orbit size `24`
- full \(W(D_6)\) active-plane stabilizer: `192` of `23040`; orbit size `120`
- signed-Fano active-operator stabilizer: `16`
- full \(W(D_6)\) active-operator stabilizer: `96`

## Commutant

- signed-Fano active-plane stabilizer commutant dimension on \(H_6\): `5`
- full \(W(D_6)\) active-plane stabilizer commutant dimension on \(H_6\): `4`
- signed-Fano active-plane stabilizer commutant dimension on Foam16: `16`
- full \(W(D_6)\) active-plane stabilizer commutant dimension on Foam16: `8`

## Random two-plane control

Over `2000` random two-planes in \(H_6\):

- observed active-plane energy percentile: `1.000000`
- random mean active-plane energy share: `0.173194`
- random max active-plane energy share: `0.961385`

## Interpretation

Invariant averaging kills the object; chamber projection recovers it. Therefore the payoff-forming mechanism is not signed-Fano invariance. It is the choice of an active chamber inside the signed-Fano/6j carrier.

## Key files

- `chamber_projector_reconstruction_ablation.csv`
- `chamber_projector_stabilizers.csv`
- `chamber_operator_stabilizers.csv`
- `active_chamber_stabilizer_commutant_dimensions.csv`
- `invariant_vs_chamber_projector_averages.csv`
- `random_2plane_chamber_projector_control_summary.json`
