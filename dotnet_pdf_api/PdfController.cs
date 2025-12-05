using Microsoft.AspNetCore.Mvc;

namespace PdfGenerator.Api
{
    [ApiController]
    [Route("api/pdf")]
    public class PdfController : ControllerBase
    {
        private readonly PdfService _pdfService;

        public PdfController(PdfService pdfService)
        {
            _pdfService = pdfService;
        }

        [HttpPost("generate")]
        public IActionResult GeneratePdf([FromBody] HtmlPayload payload)
        {
            if (string.IsNullOrWhiteSpace(payload.Html))
                return BadRequest("HTML cannot be empty");

            var bytes = _pdfService.GeneratePdf(payload.Html);

            return File(bytes, "application/pdf", payload.FileName);
        }

        [HttpGet("test")]
        public IActionResult Test()
        {
            return Ok("PDF API is working!");
        }
    }
}
