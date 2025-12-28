# Script para reemplazar URLs de ngrok con URL local del backend
# Este script reemplaza todas las ocurrencias de la URL de ngrok con http://127.0.0.1:5000

$frontendPath = ".\frontend"
$oldUrl = "https://553682876eea.ngrok-free.app"
$newUrl = "http://127.0.0.1:5000"

Write-Host "Buscando archivos HTML en $frontendPath..." -ForegroundColor Cyan

# Obtener todos los archivos HTML
$htmlFiles = Get-ChildItem -Path $frontendPath -Filter "*.html" -File

$totalFiles = 0
$totalReplacements = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    
    # Contar ocurrencias antes del reemplazo
    $matches = ([regex]::Matches($content, [regex]::Escape($oldUrl))).Count
    
    if ($matches -gt 0) {
        Write-Host "  Procesando: $($file.Name) - $matches ocurrencia(s)" -ForegroundColor Yellow
        
        # Reemplazar la URL
        $newContent = $content -replace [regex]::Escape($oldUrl), $newUrl
        
        # Guardar el archivo con codificación UTF-8 con BOM
        [System.IO.File]::WriteAllText($file.FullName, $newContent, [System.Text.UTF8Encoding]::new($true))
        
        $totalFiles++
        $totalReplacements += $matches
    }
}

Write-Host "`n✅ Completado!" -ForegroundColor Green
Write-Host "   Archivos modificados: $totalFiles" -ForegroundColor Green
Write-Host "   Total de reemplazos: $totalReplacements" -ForegroundColor Green
Write-Host "`nTodas las URLs han sido actualizadas de:" -ForegroundColor Cyan
Write-Host "  $oldUrl" -ForegroundColor Red
Write-Host "a:" -ForegroundColor Cyan
Write-Host "  $newUrl" -ForegroundColor Green
