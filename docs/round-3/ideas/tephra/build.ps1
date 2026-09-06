$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
        throw 'pdflatex is not available on PATH.'
    }
    for ($pass = 1; $pass -le 3; $pass++) {
        & pdflatex -interaction=nonstopmode -halt-on-error tephra.tex
        if ($LASTEXITCODE -ne 0) {
            throw "pdfLaTeX failed on pass $pass with exit code $LASTEXITCODE."
        }
    }
} finally {
    Pop-Location
}
