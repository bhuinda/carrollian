param(
  [string]$OutDir = "drop_external_logs_here"
)
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Out = Join-Path $Root $OutDir
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Get-ChildItem (Join-Path $Root "benchmarks") -Filter *.cnf | ForEach-Object {
  $cnf = $_.FullName
  $base = $_.BaseName
  if (Get-Command cadical -ErrorAction SilentlyContinue) {
    & cadical $cnf 1> (Join-Path $Out "$base.cadical.stdout.txt") 2> (Join-Path $Out "$base.cadical.stderr.txt")
  }
  if (Get-Command kissat -ErrorAction SilentlyContinue) {
    & kissat $cnf 1> (Join-Path $Out "$base.kissat.stdout.txt") 2> (Join-Path $Out "$base.kissat.stderr.txt")
  }
  if (Get-Command minisat -ErrorAction SilentlyContinue) {
    & minisat $cnf (Join-Path $Out "$base.minisat.model.txt") 1> (Join-Path $Out "$base.minisat.stdout.txt") 2> (Join-Path $Out "$base.minisat.stderr.txt")
  }
}
python (Join-Path $Root "scripts/analyze_external_evidence.py") $Out --out (Join-Path $Root "external_analysis")
