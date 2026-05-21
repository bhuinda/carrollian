param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $VerifierArgs
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $Python = "py"
} else {
    $Python = "python"
}

& $Python ".\source\verify.py" @VerifierArgs
exit $LASTEXITCODE
