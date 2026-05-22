# Gnatural verifier

One-command certificate:

```powershell
.\certify.ps1
```

Pretty certificate:

```powershell
.\certify.ps1 -Pretty -Out .\certificate.pretty.json
```

The default command is non-stalling. Heavy categorical lifts are explicit opt-in commands.

Generate concrete relation memberships, if source generation is desired:

```powershell
.\certify.ps1 -GenerateRelations -GenerateBe3 -Pretty -Out .\certificate.pretty.json
```

Generate F-symbol chain-set samples after relation memberships exist:

```powershell
.\certify.ps1 -GenerateFSymbols -FSymbolSampleLimit 32 -Pretty -Out .\certificate.pretty.json
```

Generate F-symbol left/right basis orderings and sparse permutation samples after relation memberships exist:

```powershell
.\certify.ps1 -GenerateFPermutations -FPermutationSampleLimit 32 -Pretty -Out .\certificate.pretty.json
```

The certificate records the exact boundary between the finite K0 object, the incidence multiplicity skeleton, the relation-membership generator, the F-symbol chain-set generator, and the F-symbol permutation-sample generator.

### Optional C985 full F-symbol inventory manifest

After concrete relation memberships have been generated, a chunked inventory manifest for associator/F-symbol domains can be generated explicitly:

```powershell
.\certify.ps1 -GenerateRelations -GenerateBe3
.\certify.ps1 -GenerateFInventory -FInventoryChunkLimit 100000 -Pretty -Out .\certificate.pretty.json
```

The default `./certify.ps1` remains non-stalling and does not generate the full inventory by default.

### Optional C985 full F-symbol inventory manifest

After concrete relation memberships have been generated, a chunked inventory manifest for associator/F-symbol domains can be generated explicitly:

```powershell
.\certify.ps1 -GenerateRelations -GenerateBe3
.\certify.ps1 -GenerateFInventory -FInventoryChunkLimit 100000 -Pretty -Out .\certificate.pretty.json
```

The default `./certify.ps1` remains non-stalling and does not generate the full inventory by default.
