# Reproduce only the focused checks in this directory, using existing cached imports.
# No Lake command, dependency build, cache download, or -o/-i output is requested.
$ErrorActionPreference = 'Stop'
$env:LAKE_JOBS = '1'
$env:LEAN_NUM_THREADS = '0'
$taskToolchain = 'leanprover--lean4---v4.32.0'
$taskLean = Join-Path $env:USERPROFILE ".elan/toolchains/$taskToolchain/bin/lean.exe"
$taskPackages = 'C:/ProveIt/.lake/packages'
$taskSource = Join-Path $PSScriptRoot 'FocusedChecks.lean'
$taskLog = Join-Path $PSScriptRoot 'FocusedChecks.log'
$taskReceipt = Join-Path $PSScriptRoot 'receipt.json'

if (-not (Test-Path -LiteralPath $taskLean)) { throw "Existing pinned toolchain missing: $taskLean" }
if (Get-Process lean,lake -ErrorAction SilentlyContinue) {
    throw 'Another Lean/Lake process is active; this experiment must be serialized.'
}

$taskLibraries = @(Get-ChildItem -LiteralPath $taskPackages -Directory |
    ForEach-Object {
        $taskLibrary = Join-Path $_.FullName '.lake/build/lib/lean'
        if (Test-Path -LiteralPath $taskLibrary) { $taskLibrary }
    })
$env:LEAN_PATH = $taskLibraries -join ';'
$taskDirectImports = @(
    'Mathlib/Data/Real/Basic.olean',
    'Mathlib/Data/Nat/Choose/Basic.olean',
    'Mathlib/Algebra/BigOperators/Group/Finset/Basic.olean',
    'Mathlib/Tactic/NormNum.olean',
    'Mathlib/Tactic/Ring.olean'
)
$taskImportHashes = @($taskDirectImports | ForEach-Object {
    $taskImportPath = Join-Path "$taskPackages/mathlib/.lake/build/lib/lean" $_
    if (-not (Test-Path -LiteralPath $taskImportPath)) { throw "Cached import missing: $taskImportPath" }
    [ordered]@{ import_olean = $_; sha256 = (Get-FileHash -LiteralPath $taskImportPath -Algorithm SHA256).Hash }
})
$taskVersion = (& $taskLean --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Failed to read Lean version.' }
$taskManifest = Get-Content -LiteralPath 'C:/ProveIt/lake-manifest.json' -Raw | ConvertFrom-Json
$taskMathlibRev = (& git -C "$taskPackages/mathlib" rev-parse HEAD | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Failed to read mathlib revision.' }

$taskStarted = [DateTime]::UtcNow
$taskWatch = [Diagnostics.Stopwatch]::StartNew()
& $taskLean $taskSource *> $taskLog
$taskExit = $LASTEXITCODE
$taskWatch.Stop()

[ordered]@{
    scope = 'Focused ordinary Lean theorem elaboration and axiom audit only; no proposed language or checker implemented.'
    started_utc = $taskStarted.ToString('o')
    completed_utc = [DateTime]::UtcNow.ToString('o')
    wall_seconds = $taskWatch.Elapsed.TotalSeconds
    exit_code = $taskExit
    executable = $taskLean
    version = $taskVersion
    arguments = @($taskSource)
    environment = [ordered]@{
        LAKE_JOBS = $env:LAKE_JOBS
        LEAN_NUM_THREADS = $env:LEAN_NUM_THREADS
        LEAN_PATH = $env:LEAN_PATH
    }
    source_sha256 = (Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash
    log_sha256 = (Get-FileHash -LiteralPath $taskLog -Algorithm SHA256).Hash
    mathlib_head = $taskMathlibRev
    declared_dependencies = @($taskManifest.packages | Select-Object name,rev,inputRev)
    direct_import_hashes = $taskImportHashes
    dependency_limit = 'Existing cached dependencies were used as supplied; no full transitive artifact integrity or kernel recheck audit was performed.'
    lake_invoked = $false
    builds_or_downloads_requested = $false
    read_only_repositories_modified = $false
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskReceipt -Encoding utf8
Get-Content -LiteralPath $taskLog
Write-Output "LEAN_EXIT_CODE=$taskExit"
exit $taskExit

