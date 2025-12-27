# Script de Configuración Automática para ngrok
# Este script actualiza automáticamente la URL del backend en config.js

param(
    [Parameter(Mandatory=$true, HelpMessage="URL de ngrok del backend (ejemplo: https://abc123.ngrok-free.app)")]
    [string]$BackendUrl,
    
    [Parameter(Mandatory=$false)]
    [switch]$Revertir
)

$configFile = "frontend\js\config.js"
$localUrl = "http://127.0.0.1:5000"

if ($Revertir) {
    Write-Host "🔄 Revirtiendo configuración a desarrollo local..." -ForegroundColor Yellow
    
    $content = Get-Content $configFile -Raw
    $content = $content -replace "const API_BASE_URL = '.*';", "const API_BASE_URL = '$localUrl';"
    Set-Content $configFile -Value $content
    
    Write-Host "✅ Configuración revertida a: $localUrl" -ForegroundColor Green
} else {
    # Validar que la URL comience con https://
    if (-not $BackendUrl.StartsWith("https://")) {
        Write-Host "❌ Error: La URL debe comenzar con https://" -ForegroundColor Red
        Write-Host "Ejemplo: https://abc123.ngrok-free.app" -ForegroundColor Yellow
        exit 1
    }
    
    # Remover trailing slash si existe
    $BackendUrl = $BackendUrl.TrimEnd('/')
    
    Write-Host "🔧 Actualizando configuración del backend..." -ForegroundColor Cyan
    Write-Host "   URL anterior: $localUrl" -ForegroundColor Gray
    Write-Host "   URL nueva: $BackendUrl" -ForegroundColor Gray
    
    $content = Get-Content $configFile -Raw
    $content = $content -replace "const API_BASE_URL = '.*';", "const API_BASE_URL = '$BackendUrl';"
    Set-Content $configFile -Value $content
    
    Write-Host "✅ Configuración actualizada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "   1. Asegúrate de que ngrok esté corriendo en el backend (puerto 5000)" -ForegroundColor White
    Write-Host "   2. Asegúrate de que ngrok esté corriendo en el frontend (puerto 8000)" -ForegroundColor White
    Write-Host "   3. Comparte la URL del frontend con tus usuarios de prueba" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 Para revertir los cambios, ejecuta:" -ForegroundColor Yellow
    Write-Host "   .\configurar_ngrok.ps1 -Revertir" -ForegroundColor Gray
}
