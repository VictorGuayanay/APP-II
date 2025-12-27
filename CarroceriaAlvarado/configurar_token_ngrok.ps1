# Script para Configurar ngrok.yml con tu Authtoken
# Automatiza la configuración del archivo ngrok.yml

param(
    [Parameter(Mandatory = $false, HelpMessage = "Tu authtoken de ngrok")]
    [string]$Authtoken
)

$ngrokConfigFile = "ngrok.yml"

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Configuración de ngrok.yml - Carrocería Alvarado         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar si el archivo existe
if (-not (Test-Path $ngrokConfigFile)) {
    Write-Host "❌ Error: No se encontró el archivo $ngrokConfigFile" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en la carpeta del proyecto.`n" -ForegroundColor Yellow
    exit 1
}

# Si no se proporcionó el token, pedirlo
if (-not $Authtoken) {
    Write-Host "📋 Necesitas tu authtoken de ngrok" -ForegroundColor Yellow
    Write-Host "   1. Ve a: https://dashboard.ngrok.com" -ForegroundColor White
    Write-Host "   2. Copia tu authtoken`n" -ForegroundColor White
    
    $Authtoken = Read-Host "Ingresa tu authtoken de ngrok"
    
    if (-not $Authtoken) {
        Write-Host "`n❌ No se proporcionó ningún token. Operación cancelada.`n" -ForegroundColor Red
        exit 1
    }
}

# Validar que el token no sea el placeholder
if ($Authtoken -eq "TU_TOKEN_AQUI") {
    Write-Host "`n❌ Error: Debes usar tu authtoken real, no el placeholder.`n" -ForegroundColor Red
    exit 1
}

# Leer el contenido actual
$contenido = Get-Content $ngrokConfigFile -Raw

# Verificar si ya está configurado
if ($contenido -notmatch "TU_TOKEN_AQUI") {
    Write-Host "⚠️  El archivo ya parece estar configurado." -ForegroundColor Yellow
    Write-Host "   Token actual: " -NoNewline -ForegroundColor Gray
    
    if ($contenido -match "authtoken:\s*(.+)") {
        $tokenActual = $matches[1].Trim()
        $tokenMostrar = $tokenActual.Substring(0, [Math]::Min(10, $tokenActual.Length)) + "..."
        Write-Host "$tokenMostrar" -ForegroundColor Gray
    }
    
    Write-Host "`n¿Deseas reemplazarlo? (S/N): " -ForegroundColor Cyan -NoNewline
    $confirmacion = Read-Host
    
    if ($confirmacion -ne 'S' -and $confirmacion -ne 's') {
        Write-Host "`n❌ Operación cancelada.`n" -ForegroundColor Red
        exit 0
    }
    
    # Reemplazar el token existente
    $contenido = $contenido -replace "authtoken:\s*.+", "authtoken: $Authtoken"
}
else {
    # Reemplazar el placeholder
    $contenido = $contenido -replace "TU_TOKEN_AQUI", $Authtoken
}

# Guardar el archivo
Set-Content $ngrokConfigFile -Value $contenido -NoNewline

Write-Host "`n✅ Archivo $ngrokConfigFile configurado exitosamente!" -ForegroundColor Green

# Mostrar el contenido (ocultando parte del token)
Write-Host "`n📄 Contenido del archivo:" -ForegroundColor Cyan
Write-Host ("─" * 70) -ForegroundColor Gray

$lineas = $contenido -split "`n"
foreach ($linea in $lineas) {
    if ($linea -match "authtoken:") {
        $tokenMostrar = $Authtoken.Substring(0, [Math]::Min(10, $Authtoken.Length)) + "..." + $Authtoken.Substring([Math]::Max(0, $Authtoken.Length - 4))
        Write-Host "authtoken: $tokenMostrar" -ForegroundColor Gray
    }
    else {
        Write-Host $linea -ForegroundColor White
    }
}

Write-Host ("─" * 70) -ForegroundColor Gray

Write-Host "`n📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Asegúrate de que el backend esté corriendo (puerto 5000)" -ForegroundColor White
Write-Host "   2. Asegúrate de que el frontend esté corriendo (puerto 8000)" -ForegroundColor White
Write-Host "   3. Ejecuta ngrok con:" -ForegroundColor White
Write-Host "`n      " -NoNewline
Write-Host "ngrok start --all --config ngrok.yml" -ForegroundColor Yellow
Write-Host "`n      O si ngrok está en C:\ngrok\:" -ForegroundColor Gray
Write-Host "`n      " -NoNewline
Write-Host "C:\ngrok\ngrok.exe start --all --config ngrok.yml" -ForegroundColor Yellow

Write-Host "`n   4. Copia las URLs que aparezcan (backend y frontend)" -ForegroundColor White
Write-Host "   5. Ejecuta:" -ForegroundColor White
Write-Host "`n      " -NoNewline
Write-Host ".\configurar_ngrok_completo.ps1 -BackendUrl 'URL_DEL_BACKEND'" -ForegroundColor Yellow

Write-Host "`n💡 Consejo:" -ForegroundColor Cyan
Write-Host "   Abre http://localhost:4040 para ver los túneles activos`n" -ForegroundColor White
