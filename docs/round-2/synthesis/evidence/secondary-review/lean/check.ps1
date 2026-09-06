# Read-only dependency use; no Lake, builds, or downloads.
$ErrorActionPreference = 'Stop'
$env:LAKE_JOBS = '1'
$env:LEAN_NUM_THREADS = '0'
$taskLean = Join-Path $env:USERPROFILE '.elan/toolchains/leanprover--lean4---v4.32.0/bin/lean.exe'
$taskPackages = 'C:/ProveIt/.lake/packages'
$taskSource = Join-Path $PSScriptRoot 'TargetChecks.lean'
$taskLog = Join-Path $PSScriptRoot 'TargetChecks.log'
if (-not (Test-Path -LiteralPath $taskLean)) { throw 'Pinned existing Lean executable missing.' }
if (Get-Process lean,lake -ErrorAction SilentlyContinue) { throw 'Another Lean/Lake process is active; wait for serialized execution.' }
$taskLibraries = @(Get-ChildItem -LiteralPath $taskPackages -Directory | ForEach-Object {
  $taskLibrary = Join-Path $_.FullName '.lake/build/lib/lean'
  if (Test-Path -LiteralPath $taskLibrary) { $taskLibrary }
})
$env:LEAN_PATH = $taskLibraries -join ';'
$taskImport = "$taskPackages/mathlib/.lake/build/lib/lean/Mathlib/Tactic/LinearCombination.olean"
if (-not (Test-Path -LiteralPath $taskImport)) { throw 'Required cached import missing.' }
$taskVersion = (& $taskLean --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Version command failed.' }
$taskManifest = Get-Content -LiteralPath 'C:/ProveIt/lake-manifest.json' -Raw | ConvertFrom-Json
$taskStarted = [DateTime]::UtcNow
$taskTimer = [Diagnostics.Stopwatch]::StartNew()
Push-Location -LiteralPath $PSScriptRoot
try {
  & $taskLean $taskSource *> $taskLog
  $taskExit = $LASTEXITCODE
} finally {
  Pop-Location
}
$taskTimer.Stop()
[ordered]@{
  scope = 'Four focused original-target Lean theorem checks and axiom audits; no benchmark, checker soundness theorem, language implementation, or dependency rebuild.'
  started_utc = $taskStarted.ToString('o')
  completed_utc = [DateTime]::UtcNow.ToString('o')
  wall_seconds = $taskTimer.Elapsed.TotalSeconds
  exit_code = $taskExit
  version = $taskVersion
  executable = $taskLean
  arguments = @($taskSource)
  working_directory = $PSScriptRoot
  environment = [ordered]@{ LAKE_JOBS=$env:LAKE_JOBS; LEAN_NUM_THREADS=$env:LEAN_NUM_THREADS; LEAN_PATH=$env:LEAN_PATH }
  source_sha256 = (Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash
  log_sha256 = (Get-FileHash -LiteralPath $taskLog -Algorithm SHA256).Hash
  direct_import_sha256 = (Get-FileHash -LiteralPath $taskImport -Algorithm SHA256).Hash
  declared_dependencies = @($taskManifest.packages | Select-Object name,rev,inputRev)
  limits = 'Existing cached imports used as supplied; no full transitive artifact or independent kernel recheck audit.'
  native_probe = 'One deliberately permitted native_decide theorem, with its generated computation axiom printed.'
  lake_invoked = $false
  builds_or_downloads_requested = $false
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'receipt.json') -Encoding utf8
Get-Content -LiteralPath $taskLog
Write-Output "LEAN_EXIT_CODE=$taskExit"
exit $taskExit

