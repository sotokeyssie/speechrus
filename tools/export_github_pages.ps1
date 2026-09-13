param(
    [string]$SourceUrl = "http://127.0.0.1:5055",
    [string]$ProjectName = "speechrus",
    [string]$Owner = "sotokeyssie"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$outputRoot = Join-Path $projectRoot "docs"
$publicBase = "https://$Owner.github.io/$ProjectName"
$pathBase = "/$ProjectName"

if (Test-Path -LiteralPath $outputRoot) {
    Remove-Item -LiteralPath $outputRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $outputRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot "static") -Destination $outputRoot -Recurse
Set-Content -LiteralPath (Join-Path $outputRoot ".nojekyll") -Value "" -NoNewline

$routes = @(
    "/", "/servicios", "/nosotros", "/articulos", "/preguntas", "/cita",
    "/contacto", "/privacidad", "/galeria", "/primera-visita", "/planes",
    "/talleres", "/testimonios"
)

[xml]$sitemap = (Invoke-WebRequest -UseBasicParsing -Uri "$SourceUrl/sitemap.xml").Content
$articleRoutes = @($sitemap.urlset.url.loc | ForEach-Object {
    ([uri]$_).AbsolutePath
} | Where-Object { $_ -like "/articulos/*" })
$routes += $articleRoutes

foreach ($route in ($routes | Select-Object -Unique)) {
    $response = Invoke-WebRequest -UseBasicParsing -Uri ($SourceUrl + $route)
    $html = $response.Content
    $html = $html.Replace($SourceUrl, $publicBase)
    $html = $html -replace '(href|src|action)="/(?!/)', ('$1="' + $pathBase + '/')
    $html = $html -replace '<a class="lang-switch"[^>]*>.*?</a>', '<span class="lang-switch" title="La versión bilingüe está disponible en el sitio completo">ES</span>'
    $html = $html -replace '<form([^>]*)method="post"', ('<form$1method="post" onsubmit="event.preventDefault(); window.location.href=''https://wa.me/17874232481'';"')

    if ($route -eq "/") {
        $target = Join-Path $outputRoot "index.html"
    } else {
        $folder = Join-Path $outputRoot ($route.Trim("/").Replace("/", [IO.Path]::DirectorySeparatorChar))
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $target = Join-Path $folder "index.html"
    }
    Set-Content -LiteralPath $target -Value $html -Encoding utf8
}

Write-Host "Exported $($routes.Count) pages to $outputRoot"
