# Hamming/Gaussian Veronese Gap Audit

Status:

```text
HAMMING_GAUSSIAN_VERONESE_GAP_AUDIT_COMPLETE
```

Certificate hash:

```text
bb5d983020401bc9f4b1b9adc15570f0a3a8a7f397ece9441aa43895111e1627
```

## Main finding

The split-spectral relaxation gaps for shells 12 and 16 are ghost artifacts of relaxing away from the Veronese monomial image.

For shell 12, the positive split vector obtained from the 6+6 incidence operator has nonzero log-additive residual, so it is not of the form `const * prod_{i in I} x_i`.

For shell 16, the 4+12 split has a large right-side zero-degree sector in the ambient 12-subset coordinate space. This confirms that the ambient split space is not the right proof domain.

## Residue

The proof must operate on the Veronese cone:

```text
y_I = prod_{i in I} x_i
```

not on arbitrary split vectors.
