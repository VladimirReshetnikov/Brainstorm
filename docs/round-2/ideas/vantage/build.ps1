$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (Get-Command latexmk -ErrorAction SilentlyContinue) {
        & latexmk -pdf -interaction=nonstopmode -halt-on-error vantage.tex
        if ($LASTEXITCODE -ne 0) { throw 'LaTeX build failed.' }
    } else {
        1..3 | ForEach-Object {
            & pdflatex -interaction=nonstopmode -halt-on-error vantage.tex
            if ($LASTEXITCODE -ne 0) { throw "pdflatex pass $_ failed." }
        }
    }
    & python reference_checks.py --output reference-checks.json
    if ($LASTEXITCODE -ne 0) { throw 'Exact-arithmetic checks failed.' }
} finally {
    Pop-Location
}
