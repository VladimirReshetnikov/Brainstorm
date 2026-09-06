# Build the article using XeLaTeX. See README.md for dependencies.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
    throw 'XeLaTeX was not found on PATH. See README.md for prerequisites.'
}
$source = Join-Path $PSScriptRoot 'Spine_Proof_Language.tex'
$build = Join-Path $PSScriptRoot '.build'
[void](New-Item -ItemType Directory -Path $build -Force)
for ($pass = 1; $pass -le 3; $pass++) {
    Write-Host "XeLaTeX pass $pass/3"
    & xelatex '-interaction=nonstopmode' '-halt-on-error' "-output-directory=$build" $source
    if ($LASTEXITCODE -ne 0) {
        throw "XeLaTeX pass $pass failed with exit code $LASTEXITCODE."
    }
}
$destination = Join-Path $PSScriptRoot 'Spine_Proof_Language.pdf'
Copy-Item -LiteralPath (Join-Path $build 'Spine_Proof_Language.pdf') -Destination $destination -Force
Write-Host "Built $destination"
