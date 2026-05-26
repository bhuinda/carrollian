# Four-level Terwilliger pilot

## Status

`FOUR_LEVEL_TERWILLIGER_PILOT_COMPLETE`

Certificate hash:

```text
342518fde37732fd3592242a76f17d42d9d63d218043e316b94e7709fc6359d1
```

## What this does

Starting from the exact three-level Terwilliger representatives, this pilot splits the remaining third color once more. For a three-level representative `(A,B,C)`, it scans every subset `D ⊂ C` and records the four-level shell profile by

```text
(|word ∩ A|, |word ∩ B|, |word ∩ D|)
```

for shell words of weight `w`.

## Pilot cutoff

```text
rest_size <= 4
```

## Results

| shell | three-level profiles included | fourth-color subsets scanned | unique four-profile hashes |
|---:|---:|---:|---:|
| 12 | 648 | 6101 | 1139 |
| 16 | 648 | 6101 | 1139 |


## Interpretation

This confirms the four-level refinement is computationally reachable by the same zeta-transform profile machinery. The full scan is larger:

```text
79,552,853 fourth-color subsets per shell
```

from the current three-level table.

The next serious run is the full four-level profile derivation, then the same pairwise-square/SOS positivity search on four-level profiles.
