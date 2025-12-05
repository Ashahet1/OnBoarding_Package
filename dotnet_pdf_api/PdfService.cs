using IronPdf;

namespace PdfGenerator.Api
{
    public class PdfService
    {
        private readonly ChromePdfRenderer _renderer;

        public PdfService()
        {
            _renderer = new ChromePdfRenderer();
        }

        public byte[] GeneratePdf(string html)
        {
            var doc = _renderer.RenderHtmlAsPdf(html);
            return doc.BinaryData;
        }
    }
}
