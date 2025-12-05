using PdfGenerator.Api;
using IronPdf;

var builder = WebApplication.CreateBuilder(args);

IronPdf.License.LicenseKey = "IRONSUITE.RIDDHI.SHAH.WOMENINAI.CO.29708-22C5C7C8FE-GALYT-MUB36KIOEQWJ-GY5SLYJNJ7ZE-27M3NSL6MDQ6-WVROVNKYEWSI-E47T2PBRHVXP-GW3EDRUKR43I-22R3NB-TF44XBVOOC6QUA-DEPLOYMENT.TRIAL-S6NBID.TRIAL.EXPIRES.27.DEC.2025";
// Add CORS so Python Streamlit can call it
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", p =>
        p.AllowAnyOrigin()
         .AllowAnyHeader()
         .AllowAnyMethod());
});

// Add controller support
builder.Services.AddControllers();

// Add our PDF service
builder.Services.AddSingleton<PdfService>();

var app = builder.Build();

app.UseCors("AllowAll");

app.MapControllers();

app.Run();
