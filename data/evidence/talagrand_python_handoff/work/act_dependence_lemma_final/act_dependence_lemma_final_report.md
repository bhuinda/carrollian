# Act Dependence Lemma

## Status

`ACT_DEPENDENCE_LEMMA_FORMALIZED`

## Lemma

Let \(C_2\) be the finite face-scene space in the audited scenic toric complex. Let

\[
Act:C_2\to \Pi_3
\]

send a face scene to its public three-level shell profile.

Then the Talagrand shell functional on face scenes factors through \(Act\):

\[
\mathcal T_w=\widehat{\mathcal T}_w\circ Act.
\]

Equivalently, if two face scenes have the same public shell profile, then they have the same Talagrand shell value.

## Proof

The Talagrand shell functional depends on a face scene only through the shell profile counts

\[
N_{jk}
=
\#\{x\in G_{24}^{(w)}:\ |x\cap A|=j,\ |x\cap B|=k\}.
\]

These counts are exactly the public three-level shell profile. The map \(Act\) is defined by taking a face scene and returning precisely that profile. Therefore every term used by \(\mathcal T_w\) is already determined by \(Act\), and no non-public placement label, deletion label, or internal filler coordinate can change \(\mathcal T_w\).

Hence \(\mathcal T_w\) factors through \(Act\).

## Consequence for the audited \(H_2\) sector

The previous audit proved that every \(Act(H_2)\) image is zero or a finite sum of exact three-level nonnegative shell gaps. Therefore, for the audited band,

\[
\mathcal T_w(H_2)\ge0.
\]

## Consequence for horn cycles

The same-boundary horn cycle sector is alternating/Vandermonde and vanishes under ordinary color-symmetric shell readout. Therefore it contributes zero to the public Talagrand shell functional.

## Audited closure

For

\[
w=12,16,\qquad \mathrm{rest}\le6,
\]

the audited four-level obstruction is holotopy-sound and closed after Act readout:

\[
\text{horn sector}=0,
\qquad
\mathcal T_w(H_2)\ge0.
\]

## Boundary

This remains an audited-band theorem. The full Talagrand proof still requires extension beyond \(\mathrm{rest}\le6\), level reduction, or a global certificate.
