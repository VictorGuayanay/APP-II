# Script para Corregir Codificación UTF-8 en Archivos HTML
# Carrocería Alvarado - 2025-12-27

$frontendDir = "frontend"
$archivosCorregidos = 0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Corrección de Codificación UTF-8" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Obtener todos los archivos HTML
$archivos = Get-ChildItem -Path $frontendDir -Filter "*.html"

foreach ($archivo in $archivos) {
    try {
        Write-Host "Procesando: $($archivo.Name)..." -NoNewline
        
        # Leer con la codificación por defecto del sistema
        $contenido = Get-Content $archivo.FullName -Raw -Encoding Default
        
        # Guardar con UTF-8 BOM
        $utf8BOM = New-Object System.Text.UTF8Encoding $true
        [System.IO.File]::WriteAllText($archivo.FullName, $contenido, $utf8BOM)
        
        Write-Host " ✓ CORREGIDO" -ForegroundColor Green
        $archivosCorregidos++
    }
    catch {
        Write-Host " ✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Archivos corregidos: $archivosCorregidos" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

if ($archivosCorregidos -gt 0) {
    Write-Host "✓ Corrección completada!" -ForegroundColor Green
    Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
    Write-Host "1. Refresca el navegador (Ctrl + Shift + R)" -ForegroundColor White
    Write-Host "2. Verifica que las tildes y ñ se vean correctamente`n" -ForegroundColor White
}
