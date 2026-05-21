# verifier

This bundle calculates the object and emits a deterministic JSON certificate.

## Windows PowerShell

Unpack and enter the bundle:

```powershell
Expand-Archive .\verifier_H_cycle_full_certificate_powershell.zip -DestinationPath .
Set-Location .\verifier
```

Create the virtual environment and install requirements:

```powershell
.\setup.ps1
```

Generate a compact JSON certificate:

```powershell
.\generate_certificate.ps1 -Out .\certificate.json
```

Generate a pretty JSON certificate:

```powershell
.\generate_certificate.ps1 -Out .\certificate.pretty.json -Pretty
```

Verify the full object:

```powershell
.\verify.ps1 verify --pass-only
```

Print the full verification payload:

```powershell
.\verify.ps1 all --pretty
```

Print the root certificate hash:

```powershell
(Get-Content .\certificate.json -Raw | ConvertFrom-Json).certificate_sha256
```

Run individual components:

```powershell
.\verify.ps1 golay --pretty
.\verify.ps1 tensor --pretty
.\verify.ps1 quotients --pretty
.\verify.ps1 packet20 --pretty
.\verify.ps1 h-cycle --pretty
.\verify.ps1 sixj --pretty
.\verify.ps1 co1 --pretty
.\verify.ps1 hamiltonian --pretty
.\verify.ps1 deepcheck --pretty
```

## Direct Python commands

Install:

```text
python -m venv .venv
python -m pip install -r requirements.txt
```

Generate compact JSON:

```text
python source/verify.py generate --out certificate.json --quiet
```

Generate pretty JSON:

```text
python source/verify.py generate --pretty --out certificate.pretty.json --quiet
```

Verify:

```text
python source/verify.py verify --pass-only
```

Print all component checks:

```text
python source/verify.py all --pretty
```

## Certificate contents

The generated JSON includes:

```text
schema
object
status
counters
  finite_code
  coherent_algebra
  quotient_tower
  packet20
  H-cycle
  sixj_scalar_block
  projective_Leech_shell
group_theory
  Be3
  Co1_projective_Leech
  quotient_symmetries
data_hashes
results
result_hashes
certificate_sha256
```
