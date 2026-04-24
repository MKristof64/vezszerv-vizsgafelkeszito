param(
    [switch]$RunOcr,
    [switch]$FullOcr,
    [string]$Pages = "5,120,300",
    [string]$SourceDir = "C:\Users\krist\OneDrive\Dokumentumok\vezsz"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$outputDir = Join-Path $root "output"
$siteDir = Join-Path $root "site"
$siteOutputDir = Join-Path $siteDir "output"
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

New-Item -ItemType Directory -Force -Path $siteOutputDir | Out-Null
Copy-Item -LiteralPath $htmlPath -Destination (Join-Path $siteOutputDir "vezszerv-tanuloapp.html") -Force
Copy-Item -LiteralPath $topicsPath -Destination (Join-Path $siteOutputDir "topics.generated.json") -Force

$rootIndex = Join-Path $root "index.html"
if (Test-Path -LiteralPath $rootIndex) {
    Copy-Item -LiteralPath $rootIndex -Destination (Join-Path $siteDir "index.html") -Force
}

$noJekyll = Join-Path $root ".nojekyll"
if (Test-Path -LiteralPath $noJekyll) {
    Copy-Item -LiteralPath $noJekyll -Destination (Join-Path $siteDir ".nojekyll") -Force
}

Write-Host ""
Write-Host "Kész:"
Write-Host " - Témaköri JSON: $topicsPath"
Write-Host " - HTML app:      $htmlPath"
Write-Host " - Pages site:    $siteDir"
if (Test-Path -LiteralPath $ocrPath) {
    Write-Host " - OCR JSON:      $ocrPath"
}
