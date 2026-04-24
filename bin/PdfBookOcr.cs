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
            throw new Exception("A WinRT mĹ±velet megszakadt.");
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
            throw new Exception("A WinRT mĹ±velet megszakadt.");
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
                    throw new ArgumentException("Ă‰rvĂ©nytelen oldaltartomĂˇny: " + segment);
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
            throw new ArgumentOutOfRangeException("pageNumber", "A kĂ©rt oldalszĂˇm kĂ­vĂĽl esik a PDF tartomĂˇnyĂˇn: " + pageNumber);
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
            Console.Error.WriteLine("HasznĂˇlat: PdfBookOcr.exe <pdfPath> <outputPath> [pageSpec] [destinationWidth]");
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
                throw new InvalidOperationException("A Windows OCR-motor nem indĂ­thatĂł a felhasznĂˇlĂłi nyelvek alapjĂˇn.");
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
            Console.Error.WriteLine("KĂ©sz: " + outputPath);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.ToString());
            return 1;
        }
    }
}
