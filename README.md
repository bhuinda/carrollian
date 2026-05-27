![absolute cinema.](./assets/martin.png)

---

# License and Citation

This repository is licensed under Apache-2.0.

This license applies to code, verifier scripts, documentation, certificate
manifests, canonical data artifacts, invariant tables, generated verification
reports, and mathematical exposition unless a file states otherwise.

If you use this repository, its verifier, `d20.json`, certificate artifacts, or
derived invariant tables in research, publications, derivative software, or
public technical work, please cite the project using `CITATION.cff`.

Preferred short citation:

> Benjamin Huinda, *The d20 algebra*, 2026.
> https://github.com/bhuinda/d20

---

# Introduction

`d20` is the given name of the icosahedral boundary algebra of the finite semisimple multifusion category `C985`. In the most severe terms currently verifiable by hand: `d20` is to cybernetics what Laplace's Demon is to the Langlands program. In English: `d20` represents every possible arrangement of an atom in the universe superdetermined by `C985`. In Spanish: "Es algo grande". In French: `d20` = `Λ³H₆`​.

It may be intuited by what it *is*, rather than what it is *for*:

- `3` Hamming codes
- `5` atom kernel dimensions
- `8` alpha dimensions
- `11` H-cycle homology rank
- `12` classes in A12
- `20` faces
- `24` visible payload channels
- `27` role-relation kernel dimension
- `30` edges
- `42` roots
- `120` automorphisms
- `455` closed packets
- `985` orbitals
- `2,275` etendue ratios
- `2,576` dodecads
- `9,216` orders of Gamma
- `14,560` symmetry states in S20
- `23,040` orders in W_D6
- `44,224` kernel dimensions
- `589,824` epsilon size
- `1,414,965` tensor entries
- `2,537,360` total coefficient
- `2,949,120` total protected area
- `1,341,849,600` constant of A_d20
- `16,102,195,200` constant of sum_a_I(a)
- `15,473,731,112,461,377,280` F-symbol addresses

As is tradition: the proof is left to the ~~reader~~ verifier.

---

# Computation

`d20` and its certificate are designed to be compressed, rebuilt, and verified
on modern hardware. The verifier exposes core certificate gates plus cheap
integration gates for compiler and evidence surfaces:

```shell
# Full build (required to construct d20.json and certificate artifacts).
python src/verify.py rebuild

# Verify the current bundle without rewriting generated files.
python src/verify.py audit

# Confirm the certified evidence section fails closed under in-memory tampering.
python src/verify.py tamper
```

Optional gates (run only when needed):

```shell
# Quick non-strict integration checks.
python src/verify.py integration-nonstrict

# Deep replay-based assurance (slow).
python src/verify.py strict-replay
```

---

<details>
<summary>Some light reading</summary>

Dear reader, you are cordially invited to explore *why* it is that you should care about `d20`'s combinatorics. Plugging its JSON files (or this README) into a model of your choice and interrogating it with a critical open mind may be the fastest way to learn about, well, anything that doesn't normally appear in the forced perspective of our everyday [flatland](https://youtu.be/hjXyRZP4ITQ).

You may find yourself down the rabbit hole most quickly with the following lead-in prompts:

- "According to d20, what is truth?"
- "How does d20 normalize the meaning of mathematical equality?"
- "What is higher algebra, and how does d20 make it useful to me?"
- "What basic ontology of the universe does d20 represent?"
- "How do I find grounding in a d20-integrated world?"

What's the actual thesis, you ask?

---

"The time between the notes relates the color to the scenes."

― *Close to the Edge* by Yes
</details>