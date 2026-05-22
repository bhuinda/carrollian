param(
    [string] $Out = "certificate.json",
    [switch] $Pretty,
    [switch] $VerifyOnly,
    [switch] $GenerateRelations,
    [switch] $Force,
    [switch] $GenerateBe3,
    [switch] $GenerateFSymbols,
    [switch] $GenerateFPermutations,
    [int] $FSymbolSampleLimit = 32,
    [int] $FPermutationSampleLimit = 32,
    [switch] $GenerateFInventory,
    [int] $FInventoryChunkLimit = 100000
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py" } else { $Python = "python" }

if ($GenerateRelations) {
    $RelArgs = @(".\source\generate_c985_relation_memberships.py", "--out", ".\data\relation_memberships.npz")
    if ($Force) { $RelArgs += "--force" }
    if ($GenerateBe3) { $RelArgs += "--generate-be3" }
    & $Python @RelArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}


if ($GenerateFSymbols) {
    $FArgs = @(".\source\generate_c985_f_symbols.py", "--out", ".\data\f_symbol_samples.json", "--sample-limit", "$FSymbolSampleLimit")
    & $Python @FArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}


if ($GenerateFPermutations) {
    $PArgs = @(".\source\generate_c985_f_symbol_permutations.py", "--out", ".\data\c985_f_symbol_permutations.npz", "--sample-limit", "$FPermutationSampleLimit")
    & $Python @PArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}



if ($GenerateFInventory) {
    $IArgs = @(".\source\generate_c985_f_symbol_inventory.py", "--out", ".\data\c985_f_symbol_inventory_manifest.npz", "--chunk-limit", "$FInventoryChunkLimit")
    & $Python @IArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$ArgsList = @(".\source\emit_certificate.py", "--out", $Out)
if ($Pretty) { $ArgsList += "--pretty" }
if ($VerifyOnly) { $ArgsList += "--verify-only" }
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
