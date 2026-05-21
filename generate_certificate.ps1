param(
    [string] $Out = "certificate.json",
    [switch] $Pretty
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ArgsList = @("generate", "--out", $Out, "--quiet")
if ($Pretty) {
    $ArgsList += "--pretty"
}

& "$PSScriptRoot\verify.ps1" @ArgsList
exit $LASTEXITCODE
