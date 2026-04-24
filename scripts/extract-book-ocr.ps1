param(
    [string]$PdfPath,
    [string]$OutputPath,
    [string]$Pages = "all",
    [int]$DestinationWidth = 1800,
    [switch]$ForceRebuild
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$binDir = Join-Path $root "bin"
$defaultSourceDir = "C:\Users\krist\OneDrive\Dokumentumok\vezsz"

function Resolve-DefaultPdfPath {
    $match = Get-ChildItem -LiteralPath $defaultSourceDir -Filter "*.pdf" |
        Where-Object {
            -not $_.Name.StartsWith('~$') -and
            $_.Name.StartsWith('VezSzerv Teljes') -and
            $_.Name.EndsWith('A.pdf')
        } |
        Select-Object -First 1 -ExpandProperty FullName

    if (-not $match) {
        throw "Nem találtam alapértelmezett könyv-PDF-et itt: $defaultSourceDir"
    }

    return $match
}

if (-not $PdfPath) {
    $PdfPath = Resolve-DefaultPdfPath
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $root "output\book-ocr.json"
}

$resolvedPdf = (Resolve-Path -LiteralPath $PdfPath).Path
$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}

$compilerPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path -LiteralPath $compilerPath)) {
    throw "Nem található a C# fordító: $compilerPath"
}

$sourcePath = Join-Path $binDir "PdfBookOcr.cs"
$exePath = Join-Path $binDir "PdfBookOcr.exe"

$sourceCode = @"
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using Windows.Data.Pdf;
using Windows.Foundation;
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;
using Windows.Storage.Streams;

internal static class Program
{
    private static T Await<T>(IAsyncOperation<T> op)
    {
        while (op.Status == AsyncStatus.Started)
        {
            Thread.Sleep(25);
        }

        if (op.Status == AsyncStatus.Error)
        {
            throw op.ErrorCode;
        }

        if (op.Status == AsyncStatus.Canceled)
        {
            throw new Exception("A WinRT művelet megszakadt.");
        }

        return op.GetResults();
    }

    private static void Await(IAsyncAction op)
    {
        while (op.Status == AsyncStatus.Started)
        {
            Thread.Sleep(25);
        }

        if (op.Status == AsyncStatus.Error)
        {
            throw op.ErrorCode;
        }

        if (op.Status == AsyncStatus.Canceled)
        {
            throw new Exception("A WinRT művelet megszakadt.");
        }

        op.GetResults();
    }

    private static IEnumerable<int> ParsePages(string pageSpec, int pageCount)
    {
        if (string.IsNullOrWhiteSpace(pageSpec) || pageSpec.Trim().Equals("all", StringComparison.OrdinalIgnoreCase))
        {
            return Enumerable.Range(0, pageCount);
        }

        var result = new SortedSet<int>();
        foreach (var rawSegment in pageSpec.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries))
        {
            var segment = rawSegment.Trim();
            if (segment.Contains("-"))
            {
                var parts = segment.Split('-');
                if (parts.Length != 2)
                {
                    throw new ArgumentException("Érvénytelen oldaltartomány: " + segment);
                }

                var start = int.Parse(parts[0]);
                var end = int.Parse(parts[1]);
                if (start > end)
                {
                    var temp = start;
                    start = end;
                    end = temp;
                }

                for (var pageNumber = start; pageNumber <= end; pageNumber++)
                {
                    ValidatePageNumber(pageNumber, pageCount);
                    result.Add(pageNumber - 1);
                }
            }
            else
            {
                var pageNumber = int.Parse(segment);
                ValidatePageNumber(pageNumber, pageCount);
                result.Add(pageNumber - 1);
            }
        }

        return result;
    }

    private static void ValidatePageNumber(int pageNumber, int pageCount)
    {
        if (pageNumber < 1 || pageNumber > pageCount)
        {
            throw new ArgumentOutOfRangeException("pageNumber", "A kért oldalszám kívül esik a PDF tartományán: " + pageNumber);
        }
    }

    private static string NormalizeText(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return string.Empty;
        }

        var normalized = text.Replace("\r\n", "\n").Replace('\r', '\n');
        var lines = normalized
            .Split('\n')
            .Select(line => line.Trim())
            .Where(line => line.Length > 0);

        return string.Join("\n", lines).Trim();
    }

    private static Dictionary<string, object> OcrPage(PdfDocument pdf, OcrEngine engine, int pageIndex, uint destinationWidth)
    {
        using (var page = pdf.GetPage((uint)pageIndex))
        {
            var stream = new InMemoryRandomAccessStream();
            if (destinationWidth > 0)
            {
                var renderOptions = new PdfPageRenderOptions { DestinationWidth = destinationWidth };
                Await(page.RenderToStreamAsync(stream, renderOptions));
            }
            else
            {
                Await(page.RenderToStreamAsync(stream));
            }

            stream.Seek(0);
            var decoder = Await(BitmapDecoder.CreateAsync(stream));
            var bitmap = Await(decoder.GetSoftwareBitmapAsync(BitmapPixelFormat.Bgra8, BitmapAlphaMode.Premultiplied));
            var result = Await(engine.RecognizeAsync(bitmap));
            var text = NormalizeText(result.Text);

            return new Dictionary<string, object>
            {
                { "pageNumber", pageIndex + 1 },
                { "charCount", text.Length },
                { "text", text }
            };
        }
    }

    public static int Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;

        if (args.Length < 2)
        {
            Console.Error.WriteLine("Használat: PdfBookOcr.exe <pdfPath> <outputPath> [pageSpec] [destinationWidth]");
            return 1;
        }

        try
        {
            var pdfPath = args[0];
            var outputPath = args[1];
            var pageSpec = args.Length >= 3 ? args[2] : "all";
            var destinationWidth = args.Length >= 4 ? uint.Parse(args[3]) : 1800U;

            var file = Await(StorageFile.GetFileFromPathAsync(pdfPath));
            var pdf = Await(PdfDocument.LoadFromFileAsync(file));
            var totalPages = (int)pdf.PageCount;
            var selectedPages = ParsePages(pageSpec, totalPages).ToList();

            var engine = OcrEngine.TryCreateFromUserProfileLanguages();
            if (engine == null)
            {
                throw new InvalidOperationException("A Windows OCR-motor nem indítható a felhasználói nyelvek alapján.");
            }

            var pageResults = new List<Dictionary<string, object>>();
            for (var index = 0; index < selectedPages.Count; index++)
            {
                var pageIndex = selectedPages[index];
                Console.Error.WriteLine(string.Format("OCR folyamat: {0}/{1}. oldal -> {2}", index + 1, selectedPages.Count, pageIndex + 1));
                pageResults.Add(OcrPage(pdf, engine, pageIndex, destinationWidth));
            }

            var payload = new Dictionary<string, object>
            {
                { "sourcePdf", pdfPath },
                { "generatedAt", DateTime.UtcNow.ToString("o") },
                { "pageSpec", pageSpec },
                { "destinationWidth", destinationWidth },
                { "totalPdfPages", totalPages },
                { "pages", pageResults }
            };

            var serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };
            var json = serializer.Serialize(payload);
            File.WriteAllText(outputPath, json, new UTF8Encoding(false));
            Console.Error.WriteLine("Kész: " + outputPath);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.ToString());
            return 1;
        }
    }
}
"@

$shouldCompile = $ForceRebuild -or -not (Test-Path -LiteralPath $sourcePath) -or -not (Test-Path -LiteralPath $exePath)
if (-not $shouldCompile) {
    $existingSource = Get-Content -LiteralPath $sourcePath -Raw
    $shouldCompile = $existingSource -ne $sourceCode
}

if ($shouldCompile) {
    $sourceCode | Set-Content -LiteralPath $sourcePath -Encoding UTF8
    & $compilerPath `
        /nologo `
        /target:exe `
        /out:$exePath `
        /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Runtime.dll" `
        /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.dll" `
        /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Core.dll" `
        /reference:"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Web.Extensions.dll" `
        /reference:"C:\Windows\System32\WinMetadata\Windows.Foundation.winmd" `
        /reference:"C:\Windows\System32\WinMetadata\Windows.Storage.winmd" `
        /reference:"C:\Windows\System32\WinMetadata\Windows.Data.winmd" `
        /reference:"C:\Windows\System32\WinMetadata\Windows.Media.winmd" `
        /reference:"C:\Windows\System32\WinMetadata\Windows.Graphics.winmd" `
        $sourcePath

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $exePath)) {
        throw "Az OCR segédprogram fordítása sikertelen volt."
    }
}

Write-Host "OCR forrás:" $resolvedPdf
Write-Host "OCR kimenet:" $OutputPath
Write-Host "Oldalak:" $Pages
Write-Host "Render szélesség:" $DestinationWidth

& $exePath $resolvedPdf $OutputPath $Pages $DestinationWidth
if ($LASTEXITCODE -ne 0) {
    throw "Az OCR futtatás sikertelen volt."
}
