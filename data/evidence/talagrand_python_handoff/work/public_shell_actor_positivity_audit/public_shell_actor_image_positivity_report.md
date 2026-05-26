# Public shell actor image positivity audit

## Status

`PUBLIC_SHELL_ACTOR_IMAGE_POSITIVITY_PASS`

## Test

Use the public shell as the actor `Act`.

`Act` sends a face scene to its public three-level shell profile and forgets deletion-face placement.  For each extracted H2 basis representative, this gives a finite public actor image: a parity set of three-level shell profiles.

The audit checks whether every public profile appearing in those actor images already has an exact nonnegative three-level certificate.

## Results

| shell | H2 reps | zero actor images | nonzero actor images | unique referenced profiles | support median | support max | uncertified refs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 547 | 1 | 546 | 650 | 4.0 | 16 | 0 |
| 16 | 547 | 1 | 546 | 649 | 4.0 | 16 | 0 |


## Interpretation

The public shell actor image of the H2 sector is already covered by the exact three-level positivity certificate.

So, after applying `Act`, every surviving H2 image is a finite sum of certified nonnegative three-level shell gaps, or zero.

This does not prove raw H2 positivity before actor readout. It proves the actor-visible H2 residue is nonnegative under the existing certificate layer.

## Updated Talagrand state

- Vandermonde horn cycles cancel under symmetric shell readout.
- H2 face residues survive before actor readout.
- The public shell actor sends the H2 residue image into the already-certified three-level positive cone.

Therefore the remaining obstruction is now below public shell readout: either raw H2 positivity before `Act`, or a theorem that Talagrand only depends on `Act`.
