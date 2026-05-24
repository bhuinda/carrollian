# D20 UF Kernel source_drop Height Coherence Fixed

Run:

```bash
python scripts/verify_d20_uf_kernel.py --arrays arrays/d20_uf_kernel_arrays.npz --outdir .
```

This package replaces the formal wording `height monism` / `BoxMonism` with `height coherence` / `BoxHeight`.

Formal rule:

```text
BoxHeight(A_ext,h) accepts iff min(A_ext h) > 0.
```

Internal interpretation retained only as an alias: a height certificate witnesses one global orientation.
