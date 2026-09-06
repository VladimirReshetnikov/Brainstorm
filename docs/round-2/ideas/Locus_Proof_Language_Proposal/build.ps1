$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw 'latexmk is required (TeX Live or MiKTeX).'
}
& latexmk -pdf -interaction=nonstopmode -halt-on-error locus.tex
if ($LASTEXITCODE -ne 0) { throw "LaTeX build failed: $LASTEXITCODE" }
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 certificate_demo.py --json test-results.json
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python certificate_demo.py --json test-results.json
} else {
    throw 'Python 3.9 or later is required.'
}
if ($LASTEXITCODE -ne 0) { throw "Certificate tests failed: $LASTEXITCODE" }
