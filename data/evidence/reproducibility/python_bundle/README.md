# d20/T985 Reproducibility Python Bundle

This bundle contains the Python scripts needed to reproduce the latest computation stack from the raw files:

- `d20.json`
- `T_985.npz`
- `quotients.npz`

Default command:

```bash
python src/run_all.py --d20 /mnt/data/d20.json --t985 /mnt/data/T_985.npz --quotients /mnt/data/quotients.npz --out ./out --sample 10000
```

Use a smaller sample for pentagon sampling:

```bash
python src/run_all.py --d20 /mnt/data/d20.json --t985 /mnt/data/T_985.npz --quotients /mnt/data/quotients.npz --out ./out --sample 100
```

Included scripts:

1. `01_packet_idempotents_peirce.py`
2. `02_wedderburn_from_d20json.py`
3. `03_rho20_scalar_representation.py`
4. `04_rho20_kernel_quotient.py`
5. `05_rho20_residue_intersections.py`
6. `06_pentagon_sample.py`

These reproduce the packet idempotents, Peirce blocks, Wedderburn sector tables, rho20 representation, rho20 kernel quotient, rho20 residue intersections, and sampled T985 pentagon genome audit.

The scripts are deliberately plain Python + NumPy + CSV/JSON. No hidden notebook state is required.
