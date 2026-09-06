param([string]$PdfLaTeX = 'pdflatex')
$ErrorActionPreference = 'Stop'
$buildDir = Join-Path $PSScriptRoot '.build'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
Push-Location $PSScriptRoot
try {
    $sourceFiles = @('unified-report.tex')
    $sourceHashes = @{}
    foreach ($sourceFile in $sourceFiles) {
        $sourceHashes[$sourceFile] = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    for ($pass = 1; $pass -le 3; $pass++) {
        & $PdfLaTeX -interaction=nonstopmode -halt-on-error -no-shell-escape "-output-directory=$buildDir" unified-report.tex *> (Join-Path $buildDir "pass-$pass.txt")
        if ($LASTEXITCODE -ne 0) {
            Get-Content -LiteralPath (Join-Path $buildDir "pass-$pass.txt") -Tail 70
            throw "pdfLaTeX pass $pass failed with exit code $LASTEXITCODE"
        }
        Write-Output "pdfLaTeX pass $pass succeeded"
    }
    $logText = Get-Content -LiteralPath (Join-Path $buildDir 'unified-report.log') -Raw
    $problems = [regex]::Matches($logText, '(?m)^.*(?:Overfull|Missing character|undefined|Rerun to get|Label\(s\) may have changed|destination with the same identifier).*$')
    if ($problems.Count -gt 0) {
        $problems | ForEach-Object { Write-Output $_.Value }
        throw 'The final LaTeX log contains unresolved references, glyphs, or overflow.'
    }
    foreach ($sourceFile in $sourceFiles) {
        $finalSourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($sourceHashes[$sourceFile] -ne $finalSourceHash) { throw "TeX input changed during the build: $sourceFile" }
    }
    Copy-Item -LiteralPath (Join-Path $buildDir 'unified-report.pdf') -Destination (Join-Path $PSScriptRoot 'unified-report.pdf') -Force
    $pdfHash = (Get-FileHash -LiteralPath 'unified-report.pdf' -Algorithm SHA256).Hash.ToLowerInvariant()
    @{ tex_sha256 = $sourceHashes['unified-report.tex']; tex_inputs = $sourceHashes; pdf_sha256 = $pdfHash; passes = 3 } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $buildDir 'build-receipt.json') -Encoding utf8
    Write-Output 'Final PDF copied after three successful passes and log checks.'
} finally {
    Pop-Location
}
