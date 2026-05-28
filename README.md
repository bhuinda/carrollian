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

We study the infinitesimally rigid object with

- `3` Hamming codes
- `5` kernel atoms
- `8` alpha dimensions
- `11` H-cycle homology rank
- `12` classes in A12
- `20` faces
- `24` visible payload channels
- `27` relationals
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

and denote its condensation, i.e. algebra, as `d20`.

`d20` may be intuited as the icosahedral boundary algebra of the finite semisimple multifusion category `C985`. Pending third-party verification, I recommend that `d20` be geometrically typed as the *Carrollian pseudosphere of indexical torsion* and intuited as a mathematical Fata Morgana: a spectral algebra projected out of a thermal boundary.

An alternative way to think about `d20` is to imagine a shape in your head (the red triangle being mildly iconic): `d20` is the object of study enabling calculus to investigate the physics of **how** you conjured that triangle there, and **where** it exists relative to *hyperspace*. Yes, hyperspace. We're talking about hyperspace in 2026. (Did you forget about [AI 2027](https://ai-2027.com/)?)

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
<summary>P.S.</summary>

Dear reader, you are cordially invited to explore *why* you should care about `d20`'s combinatorics. My own prose does it little service, but I will give you a headstart: It refutes the notion that infinity exists; that is, infinity is a category error. And when you take the big picture of it all, this characterization of infinity dictates the **why** of computation: how electricity self-interacts.

. In the most severe terms currently verifiable by hand: `d20` is to cybernetics what Laplace's Demon is to the Langlands program.

In English, that means: `d20` represents the complete possible arrangement of an atom in the universe superdetermined by `C985`. In Spanish, that means: Es algo grande. In French, that means: `d20 = Λ³H₆`​.

Plugging `d20`'s JSON files (or this README) into a LLM of your choice and interrogating it with an open critical mind may be the fastest way to learn about, well, anything that doesn't normally appear in the forced perspective of our everyday [flatland](https://youtu.be/hjXyRZP4ITQ).

Just as well, agentic programming centered on `d20` as a kernel architecture is its own whole category of joy. 



But I won't spoil quite yet what that full catalog of goodies looks like when you really take the

 in the file located at `./data/raw/Halloween.npz`

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