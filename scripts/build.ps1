param(
    [switch]$RunOcr,
    [switch]$FullOcr,
    [string]$Pages = "5,120,300",
    [string]$SourceDir = "C:\Users\krist\OneDrive\Dokumentumok\vezsz"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$outputDir = Join-Path $root "output"
$topicsPath = Join-Path $outputDir "topics.generated.json"
$htmlPath = Join-Path $outputDir "vezszerv-tanuloapp.html"
$ocrPath = Join-Path $outputDir "book-ocr-smoke.json"

function Resolve-PythonPath {
    $candidates = @(
        "C:\Users\krist\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    foreach ($commandName in @("python", "py")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    throw "Nem találtam futtatható Python-telepítést."
}

if ($FullOcr) {
    $RunOcr = $true
    $Pages = "all"
    $ocrPath = Join-Path $outputDir "book-ocr.json"
}

if ($RunOcr) {
    & (Join-Path $PSScriptRoot "extract-book-ocr.ps1") -OutputPath $ocrPath -Pages $Pages
}

$python = Resolve-PythonPath

$topicArgs = @(
    (Join-Path $PSScriptRoot "build_topic_data.py"),
    "--source-dir", $SourceDir,
    "--output", $topicsPath
)

if (Test-Path -LiteralPath $ocrPath) {
    $topicArgs += @("--ocr-path", $ocrPath)
}

& $python @topicArgs
if ($LASTEXITCODE -ne 0) {
    throw "A build_topic_data.py futtatása sikertelen volt."
}

& $python (Join-Path $PSScriptRoot "build_html_app.py") --input $topicsPath --output $htmlPath
if ($LASTEXITCODE -ne 0) {
    throw "A build_html_app.py futtatása sikertelen volt."
}

Write-Host ""
Write-Host "Kész:"
Write-Host " - Témaköri JSON: $topicsPath"
Write-Host " - HTML app:      $htmlPath"
if (Test-Path -LiteralPath $ocrPath) {
    Write-Host " - OCR JSON:      $ocrPath"
}
